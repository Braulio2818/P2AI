import sys
import random

#game finite variables
ROWS = 6
COLUMNS = 7
EMPTY = 'O'

#function to read the input file and return the algorithm, player, and board
def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        algorithm = lines[0]
        player = lines[1]
        board = []

        for line in lines[2:2+ROWS]:  #this ensures that only the board lines are read
            row = list(line)
            board.append(row)
    return algorithm, player, board

#function to show the board
def print_board(board):
    for row in board:
        print(''.join(row))

#function to get the possible legal moves
def legal_moves(board): 
    legal = []
    for col in range(COLUMNS):
        if board[0][col] == EMPTY: #if the top of the column is empty then it is a legal move
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
def horizontal_win_check(board, player):
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

def vertical_win_check(board, player):
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

def diagonal_win_check(board, player):
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

#function to check if there is a win on the board, in all possible ways
def check_win(board, player):
    return (
        horizontal_win_check(board, player) or
        vertical_win_check(board, player) or
        diagonal_win_check(board, player)
    )

#function tto update the text file with the new move and prepare the other player for their turn
def update_board_player(filename, algorithm, next_player, board):
    with open(filename, 'w') as f: #we are overwriting the file with the new move on the board as well as the next player and the algorithm
        f.write(f"{algorithm}\n")
        f.write(f"{next_player}\n")
        for row in board:
            f.write(''.join(row) + '\n')
    print(f"Updated {filename} with next player {next_player}.")


if __name__ == "__main__":
    #checks for the correct number of arguments 
    #needs to have 4 anything else will fail
    if(len(sys.argv) != 4):
        print("Usage: python part1Algo1.py <filename> <verbose> <param>")
        sys.exit(1)
    #sets all the variables to the arguments passed in the command line
    filename = sys.argv[1] 
    verbose = sys.argv[2]
    param = int(sys.argv[3])
    
    algo, player, board = read_input(filename) #starts the game by reading the input file

    #if someone already won, the game won't allow another move
    if check_win(board, player):
        print(f"Player {player} has already won!")
        print("Clear board for a new game.")
        sys.exit(0)

    #show current game state
    print(f"Algorithm: {algo}")
    print(f"Player: {player}")
    print("Current board:")
    print_board(board)
    print()

    legal = legal_moves(board)
    print("Legal moves:", legal)

    #running random algorithm
    if algo == "UR":
        legal_moves = legal_moves(board)
        if not legal_moves:
            print("No legal moves available.")
            sys.exit(0)
        else:
            move = random.choice(legal_moves)
            print(f"FINAL Move selected: {move + 1}") #+1 to make it more user friendly
            board = make_move(board, move, player)
            print()

            #check if the player won after the move
            if check_win(board, player):
                print(f"Player {player} wins!")
                print("Board:")
                print_board(board)
                #update the file and exit the game
                update_board_player(filename, algo, player, board)
                sys.exit(0)
            else:
                #Switch to the other player and update the file
                next_player = 'Y' if player == 'R' else 'R'
                update_board_player(filename, algo, next_player, board)

            #show the move after making the move
            print("Board after move:")
            print_board(board)