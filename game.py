import streamlit as st

import streamlit as st
import random
import numpy as np

st.set_page_config(page_title="🎮 Tetris in Streamlit", layout="centered")

st.title("🎮 Tetris (Prototype)")

# Board size
ROWS, COLS = 20, 10

# Shapes (Tetriminos)
SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    "L": [[1, 0, 0],
          [1, 1, 1]],
    "J": [[0, 0, 1],
          [1, 1, 1]],
    "S": [[0, 1, 1],
          [1, 1, 0]],
    "Z": [[1, 1, 0],
          [0, 1, 1]],
}

def new_piece():
    shape = random.choice(list(SHAPES.values()))
    return np.array(shape)

# Initialize session state
if "board" not in st.session_state:
    st.session_state.board = np.zeros((ROWS, COLS), dtype=int)
if "piece" not in st.session_state:
    st.session_state.piece = new_piece()
if "pos" not in st.session_state:
    st.session_state.pos = [0, COLS // 2 - 1]

def check_collision(board, piece, pos):
    px, py = pos
    for i in range(piece.shape[0]):
        for j in range(piece.shape[1]):
            if piece[i, j]:
                if (i + px >= ROWS or
                    j + py < 0 or j + py >= COLS or
                    board[i + px, j + py]):
                    return True
    return False

def merge_piece(board, piece, pos):
    px, py = pos
    for i in range(piece.shape[0]):
        for j in range(piece.shape[1]):
            if piece[i, j]:
                board[i + px, j + py] = 1
    return board

def clear_lines(board):
    new_board = board[~np.all(board == 1, axis=1)]
    cleared = ROWS - new_board.shape[0]
    if cleared > 0:
        new_board = np.vstack([np.zeros((cleared, COLS), dtype=int), new_board])
    return new_board, cleared

def draw_board(board, piece, pos):
    temp = board.copy()
    px, py = pos
    for i in range(piece.shape[0]):
        for j in range(piece.shape[1]):
            if piece[i, j] and 0 <= i+px < ROWS and 0 <= j+py < COLS:
                temp[i + px, j + py] = 2
    # Draw with emoji
    return "\n".join("".join("⬛" if x==0 else ("🟥" if x==1 else "🟦") for x in row) for row in temp)

# Movement buttons
col1, col2, col3, col4 = st.columns(4)
if col1.button("⬅️ Left"):
    new_pos = [st.session_state.pos[0], st.session_state.pos[1]-1]
    if not check_collision(st.session_state.board, st.session_state.piece, new_pos):
        st.session_state.pos = new_pos
if col2.button("➡️ Right"):
    new_pos = [st.session_state.pos[0], st.session_state.pos[1]+1]
    if not check_collision(st.session_state.board, st.session_state.piece, new_pos):
        st.session_state.pos = new_pos
if col3.button("⬇️ Down"):
    new_pos = [st.session_state.pos[0]+1, st.session_state.pos[1]]
    if not check_collision(st.session_state.board, st.session_state.piece, new_pos):
        st.session_state.pos = new_pos
    else:
        # Merge piece into board
        st.session_state.board = merge_piece(st.session_state.board, st.session_state.piece, st.session_state.pos)
        st.session_state.board, _ = clear_lines(st.session_state.board)
        st.session_state.piece = new_piece()
        st.session_state.pos = [0, COLS // 2 - 1]
if col4.button("🔄 Rotate"):
    rotated = np.rot90(st.session_state.piece)
    if not check_collision(st.session_state.board, rotated, st.session_state.pos):
        st.session_state.piece = rotated

# Draw board
st.text(draw_board(st.session_state.board, st.session_state.piece, st.session_state.pos))
