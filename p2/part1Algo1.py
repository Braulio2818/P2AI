import sys
import random
import copy

#game finite variables
ROWS = 6
COLUMNS = 7
EMPTY = 'O'

#function to read the input file and return the algorithm, player, and board
def read_input(filename):
    print(f"Reading input from: {filename}") 
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        algorithm = lines[0]
        player = lines[1]
        board = []
        for line in lines[2:]:
            row = list(line)
            board.append(row)
    return algorithm, player, board

#function to show the board
def print_board(board):
    for row in board:
        print(''.join(row))

#function to get the possible legal moves
def get_legal_moves(board): 
    legal = []
    for col in range(COLUMNS):
        if board[0][col] == EMPTY:
            legal.append(col)
    return legal

#function to make a move on the board
def make_move(board, col, player):
    #reverse board to make it easier to find the first empty space in the column
    for row in reversed(range(ROWS)):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return board
    return board

#function to check if there is a win on the board
def check_horizontal_win(board, player):
    for row in range(ROWS):
        for col in range(COLUMNS - 3):
            count = 0
            for i in range(4):
                if board[row][col + i] == player:
                    count += 1
                else:
                    break
            if count == 4:
                return True
    return False

def check_vertical_win(board, player):
    for col in range(COLUMNS):
        for row in range(ROWS - 3):
            count = 0
            for i in range(4):
                if board[row + i][col] == player:
                    count += 1
                else:
                    break
            if count == 4:
                return True
    return False

def check_diagonal_win(board, player):
    # Bottom-left to top-right
    for row in range(3, ROWS):
        for col in range(COLUMNS - 3):
            count = 0
            for i in range(4):
                if board[row - i][col + i] == player:
                    count += 1
                else:
                    break
            if count == 4:
                return True

    # Top-left to bottom-right
    for row in range(ROWS - 3):
        for col in range(COLUMNS - 3):
            count = 0
            for i in range(4):
                if board[row + i][col + i] == player:
                    count += 1
                else:
                    break
            if count == 4:
                return True

    return False

def check_win(board, player):
    return (
        check_horizontal_win(board, player) or
        check_vertical_win(board, player) or
        check_diagonal_win(board, player)
    )

#function tto update the text file with the new move and prepare the other player for their turn
def write_board_to_file(filename, algorithm, next_player, board):
    with open(filename, 'w') as f:
        f.write(f"{algorithm}\n")
        f.write(f"{next_player}\n")
        for row in board:
            f.write(''.join(row) + '\n')
    print(f"Updated {filename} with next player {next_player}.")


if __name__ == "__main__":
    #checks for the correct number of arguments 
    if(len(sys.argv) != 4):
        print("Usage: python part1Algo1.py <filename> <verbose> <param>")
        sys.exit(1)
    #sets all the variables to the arguments passed in the command line
    filename = sys.argv[1] 
    verbose = sys.argv[2]
    param = int(sys.argv[3])
    
    algo, player, board = read_input(filename) #starts the game by reading the input file

    if check_win(board, player):
        print(f"Player {player} has already won!")
        sys.exit(0)
    #information printed after every move
    print(f"Algorithm: {algo}")
    print(f"Player: {player}")
    print("Current board:")
    print_board(board)
    legal = get_legal_moves(board)
    print("Legal moves:", legal)

    #running random algorithm
    if algo == "UR":
        legal_moves = get_legal_moves(board)
        if not legal_moves:
            print("No legal moves available.")
            sys.exit(0)
        else:
            move = random.choice(legal_moves)
            print(f"FINAL Move selected: {move + 1}")
            board = make_move(board, move, player)

            if check_win(board, player):
                print(f"Player {player} wins!")
                print("Board:")
                print_board(board)
                sys.exit(0)
            else:
                next_player = 'Y' if player == 'R' else 'R'
                write_board_to_file(filename, algo, next_player, board)

            print("Board after move:")
            print_board(board)