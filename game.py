import streamlit as st

st.set_page_config(page_title="Tetris Game", layout="centered")
st.title("🎮 Tetris in Streamlit")

tetris_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body { display:flex; justify-content:center; align-items:flex-start; background:#111; flex-direction:column; color:#fff; font-family:Arial; margin:0; padding:0; }
  #game-container { position:relative; margin-top:10px; touch-action: none; }
  canvas { background:#222; display:block; margin:auto; }
  #score, #highscore-title, #game-over { text-align:center; }
  #score, #highscore-title { font-size:18px; margin:5px 0; }
  #game-over { position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); display:flex; justify-content:center; align-items:center; color:#FF0D72; font-size:36px; font-weight:bold; flex-direction: column; display:none; }
  #restart { margin-top:15px; padding:10px 20px; font-size:18px; border-radius:5px; background:#FF0D72; color:#fff; border:none; cursor:pointer; }
</style>
</head>
<body>
<div id="score">Score: 0</div>
<div id="highscore-title">High Score: 0</div>
<div id="game-container">
  <canvas id="tetris"></canvas>
  <div id="game-over">
    GAME OVER
    <button id="restart">Restart</button>
  </div>
</div>

<audio id="dropSound" src="https://actions.google.com/sounds/v1/cartoon/pop.ogg"></audio>
<audio id="lineSound" src="https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg"></audio>
<audio id="gameOverSound" src="https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg"></audio>

<script>
const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');
const container = document.getElementById('game-container');

function resizeCanvas(){
    let width = Math.min(window.innerWidth-20, 240);
    let height = width*20/12;
    canvas.width = width;
    canvas.height = height*20/12;
    scaleX = canvas.width/12;
    scaleY = canvas.height/20;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

let scaleX = canvas.width/12;
let scaleY = canvas.height/20;

const dropSound = document.getElementById('dropSound');
const lineSound = document.getElementById('lineSound');
const gameOverSound = document.getElementById('gameOverSound');

let score=0;
let highScore=0;
let dropInterval=1000;
let nextPiece = null;
let paused=false;
let gameOver=false;

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

function drawMatrix(matrix, offset){
    matrix.forEach((row,y)=>{
        row.forEach((value,x)=>{
            if(value!==0){
                context.fillStyle=colors[value];
                context.fillRect(x*scaleX, y*scaleY, scaleX, scaleY);
            }
        });
    });
}

function draw(){
    context.fillStyle='#222';
    context.fillRect(0,0,canvas.width,canvas.height);
    drawMatrix(arena,{x:0,y:0});
    drawMatrix(player.matrix, player.pos);
}

function merge(arena, player){
    player.matrix.forEach((row,y)=>{
        row.forEach((value,x)=>{
            if(value!==0) arena[y+player.pos.y][x+player.pos.x]=value;
        });
    });
}

function collide(arena, player){
    const [m,o]=[player.matrix, player.pos];
    for(let y=0;y<m.length;y++){
        for(let x=0;x<m[y].length;x++){
            if(m[y][x]!==0 &&
               (arena[y+o.y] && arena[y+o.y][x+o.x])!==0) return true;
        }
    }
    return false;
}

function arenaSweep(){
    let rowCount=1;
    let cleared=false;
    outer: for(let y=arena.length-1;y>0;--y){
        for(let x=0;x<arena[y].length;x++){
            if(arena[y][x]===0) continue outer;
        }
        const row=arena.splice(y,1)[0].fill(0);
        arena.unshift(row);
        ++y;
        score+=rowCount*10;
        rowCount*=2;
        dropInterval=Math.max(100, dropInterval-10);
        cleared=true;
    }
    if(cleared) lineSound.play();
    document.getElementById('score').innerText='Score: '+score;
    if(score>highScore){highScore=score; document.getElementById('highscore-title').innerText='High Score: '+highScore;}
}

const colors=[null,'#FF0D72','#0DC2FF','#0DFF72','#F538FF','#FF8E0D','#FFE138','#3877FF'];
const arena=createMatrix(12,20);
const player={pos:{x:0,y:0}, matrix:null};

function playerReset(){
    if(nextPiece){player.matrix=nextPiece;} 
    else {const pieces='ILJOTSZ'; player.matrix=createPiece(pieces[Math.floor(Math.random()*pieces.length)]);}
    const pieces='ILJOTSZ';
    nextPiece=createPiece(pieces[Math.floor(Math.random()*pieces.length)]);
    player.pos.y=0;
    player.pos.x=(arena[0].length/2|0)-(player.matrix[0].length/2|0);
    if(collide(arena,player)){
        gameOver=true;
        document.getElementById('game-over').style.display='flex';
        gameOverSound.play();
    }
}

function playerDrop(){
    if(gameOver||paused) return;
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
    if(gameOver||paused) return;
    player.pos.x+=dir;
    if(collide(arena,player)) player.pos.x-=dir;
}

function playerRotate(dir){
    if(gameOver||paused) return;
    const pos=player.pos.x;
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

let dropCounter=0;
let lastTime=0;

function update(time=0){
    if(!paused && !gameOver){
        const deltaTime=time-lastTime;
        lastTime=time;
        dropCounter+=deltaTime;
        if(dropCounter>dropInterval) playerDrop();
        draw();
    }
    requestAnimationFrame(update);
}

// Keyboard controls
document.addEventListener('keydown', event=>{
    if(paused||gameOver) return;
    if(event.key==='a') playerMove(-1);
    else if(event.key==='d') playerMove(1);
    else if(event.key==='s') playerDrop();
    else if(event.key==='w') playerRotate(1);
});

// Touch controls
let startX=0, startY=0, lastTap=0;
canvas.addEventListener('touchstart', e=>{
    if(e.touches.length>1) return;
    const touch=e.touches[0];
    startX=touch.clientX;
    startY=touch.clientY;
    const currentTime = new Date().getTime();
    const tapLength = currentTime - lastTap;
    if(tapLength < 300 && tapLength>0){playerRotate(1);}
    lastTap=currentTime;
}, {passive:false});

canvas.addEventListener('touchmove', e=>{
    if(e.touches.length>1) return;
    const touch=e.touches[0];
    let dx=touch.clientX-startX;
    let dy=touch.clientY-startY;
    if(Math.abs(dx)>20){
        playerMove(dx>0?1:-1);
        startX=touch.clientX;
    }
    if(dy>30){
        playerDrop();
        startY=touch.clientY;
    }
    e.preventDefault();
}, {passive:false});

document.getElementById('restart').onclick=()=>{
    arena.forEach(row=>row.fill(0));
    score=0;
    dropInterval=1000;
    gameOver=false;
    document.getElementById('game-over').style.display='none';
    playerReset();
};

playerReset();
update();
</script>
</body>
</html>
"""

st.components.v1.html(tetris_html, height=650)
