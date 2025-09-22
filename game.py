import streamlit as st

st.set_page_config(page_title="Tetris Game", layout="centered")
st.title("🎮 Tetris in Streamlit")

tetris_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { display: flex; justify-content: center; align-items: flex-start; height: 100vh; background: #111; flex-direction: column; color: #fff; font-family: Arial; }
  #game-container { display: flex; position: relative; }
  canvas { background: #222; margin-right: 20px; }
  #info { display: flex; flex-direction: column; }
  #score, #next-piece-title, #highscore-title { margin-bottom: 10px; font-size: 20px; }
  #controls { margin-top: 10px; }
  .btn { background: #444; color: #fff; border: none; padding: 10px 20px; margin: 5px; font-size: 16px; border-radius: 5px; }
  #game-over { position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); display:flex; justify-content:center; align-items:center; color:#FF0D72; font-size:36px; font-weight:bold; display:none; flex-direction: column; }
  #restart { margin-top: 20px; padding: 10px 20px; font-size: 18px; border-radius: 5px; background: #FF0D72; color: #fff; border: none; cursor: pointer; }
</style>
</head>
<body>
<div id="game-container">
  <canvas id="tetris" width="240" height="400"></canvas>
  <div id="game-over">
    GAME OVER
    <button id="restart">Restart</button>
  </div>
  <div id="info">
    <div id="score">Score: 0</div>
    <div id="highscore-title">High Score: 0</div>
    <div id="next-piece-title">Next Piece:</div>
    <canvas id="next" width="80" height="80"></canvas>
    <div id="controls">
      <button class="btn" id="left">Left (A)</button>
      <button class="btn" id="right">Right (D)</button>
      <button class="btn" id="down">Drop (S)</button>
      <button class="btn" id="rotate">Rotate (W)</button>
      <button class="btn" id="pause">Pause</button>
    </div>
  </div>
</div>

<audio id="dropSound" src="https://actions.google.com/sounds/v1/cartoon/pop.ogg"></audio>
<audio id="lineSound" src="https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg"></audio>
<audio id="gameOverSound" src="https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg"></audio>

<script>
const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');
context.scale(20,20);

const nextCanvas = document.getElementById('next');
const nextCtx = nextCanvas.getContext('2d');
nextCtx.scale(20,20);

const dropSound = document.getElementById('dropSound');
const lineSound = document.getElementById('lineSound');
const gameOverSound = document.getElementById('gameOverSound');

let score = 0;
let highScore = 0;
let dropInterval = 1000;
let nextPiece = null;
let paused = false;
let gameOver = false;

function arenaSweep() {
    let rowCount = 1;
    let cleared = false;
    outer: for (let y = arena.length -1; y > 0; --y) {
        for (let x = 0; x < arena[y].length; ++x) {
            if (arena[y][x] === 0) continue outer;
        }
        const row = arena.splice(y, 1)[0].fill(0);
        arena.unshift(row);
        ++y;
        score += rowCount * 10;
        rowCount *= 2;
        dropInterval = Math.max(100, dropInterval - 10);
        cleared = true;
    }
    if(cleared) lineSound.play();
    document.getElementById('score').innerText = 'Score: ' + score;
    if(score > highScore){
        highScore = score;
        document.getElementById('highscore-title').innerText = 'High Score: ' + highScore;
    }
}

function collide(arena, player) {
    const [m,o] = [player.matrix, player.pos];
    for(let y=0; y<m.length; y++){
        for(let x=0; x<m[y].length; x++){
            if(m[y][x]!==0 &&
               (arena[y+o.y] && arena[y+o.y][x+o.x])!==0){
                return true;
            }
        }
    }
    return false;
}

function createMatrix(w,h){const m=[];while(h--) m.push(new Array(w).fill(0));return m;}
function createPiece(type){
    if(type==='T') return [[0,0,0],[1,1,1],[0,1,0]];
    else if(type==='O') return [[2,2],[2,2]];
    else if(type==='L') return [[0,3,0],[0,3,0],[0,3,3]];
    else if(type==='J') return [[0,4,0],[0,4,0],[4,4,0]];
    else if(type==='I') return [[0,5,0,0],[0,5,0,0],[0,5,0,0],[0,5,0,0]];
    else if(type==='S') return [[0,6,6],[6,6,0],[0,0,0]];
    else if(type==='Z') return [[7,7,0],[0,7,7],[0,0,0]];
}

function drawMatrix(matrix, offset, ctx= context){
    matrix.forEach((row,y)=>{
        row.forEach((value,x)=>{
            if(value!==0){
                ctx.fillStyle=colors[value];
                ctx.fillRect(x+offset.x, y+offset.y,1,1);
            }
        });
    });
}

function draw(){
    context.fillStyle='#222';
    context.fillRect(0,0,canvas.width,canvas.height);
    drawMatrix(arena,{x:0,y:0});
    drawMatrix(player.matrix, player.pos);
    drawNextPiece();
}

function merge(arena, player){
    player.matrix.forEach((row,y)=>{
        row.forEach((value,x)=>{
            if(value!==0) arena[y+player.pos.y][x+player.pos.x]=value;
        });
    });
}

function playerDrop(){
    if(gameOver || paused) return;
    player.pos.y++;
    if(collide(arena,player)){
        player.pos.y--;
        merge(arena,player);
        dropSound.play();
        playerReset();
        arenaSweep();
    }
    dropCounter=0;
}

function playerMove(dir){
    if(gameOver || paused) return;
    player.pos.x += dir;
    if(collide(arena,player)) player.pos.x -= dir;
}

function playerReset(){
    if(nextPiece){
        player.matrix = nextPiece;
    } else {
        const pieces = 'ILJOTSZ';
        player.matrix = createPiece(pieces[Math.floor(Math.random()*pieces.length)]);
    }
    const pieces = 'ILJOTSZ';
    nextPiece = createPiece(pieces[Math.floor(Math.random()*pieces.length)]);
    player.pos.y=0;
    player.pos.x=(arena[0].length/2|0)-(player.matrix[0].length/2|0);
    if(collide(arena,player)){
        gameOver = true;
        document.getElementById('game-over').style.display = 'flex';
        gameOverSound.play();
    }
}

function playerRotate(dir){
    if(gameOver || paused) return;
    const pos = player.pos.x;
    let offset=1;
    rotate(player.matrix,dir);
    while(collide(arena,player)){
        player.pos.x+=offset;
        offset=-(offset+(offset>0?1:-1));
        if(offset>player.matrix[0].length){rotate(player.matrix,-dir);player.pos.x=pos;return;}
    }
}

function rotate(matrix, dir){
    for(let y=0;y<matrix.length;y++){
        for(let x=0;x<y;x++){
            [matrix[x][y],matrix[y][x]]=[matrix[y][x],matrix[x][y]];
        }
    }
    if(dir>0) matrix.forEach(row=>row.reverse());
    else matrix.reverse();
}

function drawNextPiece(){
    nextCtx.fillStyle='#222';
    nextCtx.fillRect(0,0,nextCanvas.width,nextCanvas.height);
    drawMatrix(nextPiece, {x:0,y:0}, nextCtx);
}

let dropCounter=0;
let lastTime=0;

function update(time=0){
    if(!paused && !gameOver){
        const deltaTime = time - lastTime;
        lastTime=time;
        dropCounter+=deltaTime;
        if(dropCounter>dropInterval) playerDrop();
        draw();
    }
    requestAnimationFrame(update);
}

// Keyboard controls
document.addEventListener('keydown', event=>{
    if(paused || gameOver) return;
    if(event.key==='a') playerMove(-1);
    else if(event.key==='d') playerMove(1);
    else if(event.key==='s') playerDrop();
    else if(event.key==='w') playerRotate(1);
});

// Mobile buttons
document.getElementById('left').onclick=()=>playerMove(-1);
document.getElementById('right').onclick=()=>playerMove(1);
document.getElementById('down').onclick=()=>playerDrop();
document.getElementById('rotate').onclick=()=>playerRotate(1);
document.getElementById('pause').onclick=()=>{
    if(gameOver) return;
    paused=!paused;
    document.getElementById('pause').innerText = paused ? 'Resume' : 'Pause';
};

document.getElementById('restart').onclick=()=>{
    arena.forEach(row=>row.fill(0));
    score=0;
    dropInterval=1000;
    gameOver=false;
    document.getElementById('game-over').style.display='none';
    playerReset();
};

const colors=[null,'#FF0D72','#0DC2FF','#0DFF72','#F538FF','#FF8E0D','#FFE138','#3877FF'];
const arena=createMatrix(12,20);
const player={pos:{x:0,y:0}, matrix:null};

playerReset();
update();
</script>
</body>
</html>
"""

st.components.v1.html(tetris_html, height=550)
