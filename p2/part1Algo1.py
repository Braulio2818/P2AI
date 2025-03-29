import sys
import random
import copy

ROWS = 6
COLUMNS = 7
EMPTY = 'O'

def read_input(filename):
    print(f"Reading input from: {filename}")  # debug
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        print(f"Read {len(lines)} lines")  # debug
        algorithm = lines[0]
        player = lines[1]
        board = [list(line) for line in lines[2:]]
        print("Parsed board successfully")  # debug
    return algorithm, player, board

def print_board(board):
    for row in board:
        print(''.join(row))

def get_legal_moves(board):
    legal = []
    for col in range(COLUMNS):
        if board[0][col] == EMPTY:
            legal.append(col)
    return legal

def make_move(board, col, player):
    for row in reversed(range(ROWS)):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return board
    return board

if __name__ == "__main__":
    print("Script started.")  # debug
    filename = sys.argv[1]
    verbose = sys.argv[2]
    param = int(sys.argv[3])
    
    print("Calling read_input")  # debug
    algo, player, board = read_input(filename)

    print(f"Algorithm: {algo}")
    print(f"Player: {player}")
    print("Current board:")
    print_board(board)
    legal = get_legal_moves(board)
    print("Legal moves:", legal)
