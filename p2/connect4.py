import sys
import random
import copy
import math

# Game constants
ROWS = 6
COLUMNS = 7
EMPTY = 'O'

# Read input file
def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        algorithm = lines[0]
        player = lines[1]
        board = [list(line) for line in lines[2:2 + ROWS]]
    return algorithm, player, board

# Print board
def print_board(board):
    for row in board:
        print(''.join(row))

# Get legal moves
def legal_moves(board):
    return [col for col in range(COLUMNS) if board[0][col] == EMPTY]

# Make a move
def make_move(board, col, player):
    new_board = copy.deepcopy(board)
    for row in reversed(range(ROWS)):
        if new_board[row][col] == EMPTY:
            new_board[row][col] = player
            return new_board
    return new_board

# Win checkers
def horizontal_win_check(board, player):
    for row in range(ROWS):
        for col in range(COLUMNS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                return True
    return False

def vertical_win_check(board, player):
    for col in range(COLUMNS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == player for i in range(4)):
                return True
    return False

def diagonal_win_check(board, player):
    for row in range(3, ROWS):
        for col in range(COLUMNS - 3):
            if all(board[row - i][col + i] == player for i in range(4)):
                return True
    for row in range(ROWS - 3):
        for col in range(COLUMNS - 3):
            if all(board[row + i][col + i] == player for i in range(4)):
                return True
    return False

def check_win(board, player):
    return (
        horizontal_win_check(board, player) or
        vertical_win_check(board, player) or
        diagonal_win_check(board, player)
    )

# Update file after move
def update_board_player(filename, algorithm, next_player, board):
    with open(filename, 'w') as f:
        f.write(f"{algorithm}\n")
        f.write(f"{next_player}\n")
        for row in board:
            f.write(''.join(row) + '\n')
    print(f"Updated {filename} with next player {next_player}.")

def simulate_random_game_verbose(board, current_player, opponent, verbose):
    temp_board = copy.deepcopy(board)
    turn = opponent  # Because root player already made a move

    moves_sequence = []

    while True:
        moves = legal_moves(temp_board)
        if not moves:
            if verbose:
                print("TERMINAL NODE VALUE: 0")  # Draw
            return 0

        move = random.choice(moves)
        moves_sequence.append(move)

        if verbose:
            print(f"Move selected: {move + 1}")

        temp_board = make_move(temp_board, move, turn)

        if check_win(temp_board, turn):
            if verbose:
                print(f"TERMINAL NODE VALUE: {'1' if turn == current_player else '-1'}")
            return 1 if turn == current_player else -1

        turn = 'Y' if turn == 'R' else 'R'

def make_empty_board():
    return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]

def run_ur(board, player, param=None, verbose=True):
    legal = legal_moves(board)
    if not legal:
        if verbose:
            print("No legal moves available.")
        return board, None

    move = random.choice(legal)
    if verbose:
        print(f"FINAL Move selected: {move + 1}")
    board = make_move(board, move, player)
    return board, move

def run_pmcgs(board, player, param, verbose):
    legal = legal_moves(board)
    stats = {move: {"wi": 0, "ni": 0} for move in legal}

    opponent = 'Y' if player == 'R' else 'R'

    if verbose:
        print(f"Running PMCGS with {param} simulations per move.")
        print(f"Legal moves: {legal}")

    for move in legal:
        if verbose:
            print(f"\nEvaluating move: {move + 1}")
        for _ in range(param):
            sim_board = make_move(copy.deepcopy(board), move, player)

            if stats[move]["ni"] == 0 and verbose:
                print("NODE ADDED\n")

            result = simulate_random_game_verbose(sim_board, player, opponent, verbose)

            # Update stats
            stats[move]["wi"] += result
            stats[move]["ni"] += 1

            if verbose:
                print("Updated values:")
                print(f"wi: {stats[move]['wi']}")
                print(f"ni: {stats[move]['ni']} \n")

    # Final move selection based on highest wi
    best_move = max(legal, key=lambda m: stats[m]["wi"])
    best_value = stats[best_move]["wi"]

    if verbose:
        print("\nColumn values (wi/ni):")
        for col in range(7):
            if col in stats and stats[col]["ni"] > 0:
                avg = stats[col]["wi"] / stats[col]["ni"]
                print(f"Column {col + 1}: {avg:.2f}")
            else:
                print(f"Column {col + 1}: Null")

        print(f"\nFINAL Move selected: {best_move + 1}")

    return make_move(board, best_move, player), best_move

def run_uct(board, player, param, verbose):
    import math
    legal = legal_moves(board)
    stats = {move: {"wins": 0, "plays": 0} for move in legal}
    opponent = 'Y' if player == 'R' else 'R'
    C = math.sqrt(2)

    if verbose:
        print(f"Running UCT with {param} simulations total.")
        print(f"Legal moves: {legal}")

    for sim in range(param):
        total_plays = sum(stats[move]["plays"] for move in legal) + 1

        ucb_scores = {}
        for move in legal:
            w = stats[move]["wins"]
            n = stats[move]["plays"]
            if n == 0:
                ucb_scores[move] = float("inf")
            else:
                ucb_scores[move] = (w / n) + C * math.sqrt(math.log(total_plays) / n)

        # Select move using UCB (maximize for R, minimize for Y)
        if player == 'R':
            best_move = max(legal, key=lambda m: ucb_scores[m])
        else:
            best_move = min(legal, key=lambda m: ucb_scores[m])

        # Verbose output for root statistics
        if verbose:
            print(f"\nwi: {stats[best_move]['wins']}")
            print(f"ni: {stats[best_move]['plays']}")
            for i in range(7):
                if i in stats:
                    w = stats[i]["wins"]
                    n = stats[i]["plays"]
                    v = (w / n) if n > 0 else 0.0
                    print(f"V{i+1}: {v:.2f}" if i in legal else f"V{i+1}: Null")
                else:
                    print(f"V{i+1}: Null")
            print(f"Move selected: {best_move + 1}")

        # Simulate game with verbose rollout
        sim_board = make_move(board, best_move, player)
        winner = simulate_random_game_verbose(sim_board, player, opponent, verbose)

        stats[best_move]["plays"] += 1
        if winner == player:
            stats[best_move]["wins"] += 1

        if verbose:
            print("Updated values:")
            print(f"wi: {stats[best_move]['wins']}")
            print(f"ni: {stats[best_move]['plays']}")

    # Final move selection based on win ratio
    final_move = None
    best_value = float('-inf') if player == 'R' else float('inf')
    for move in legal:
        w, n = stats[move]["wins"], stats[move]["plays"]
        value = w / n if n > 0 else 0.0
        if (player == 'R' and value > best_value) or (player == 'Y' and value < best_value):
            best_value = value
            final_move = move

    # Print final stats
    if verbose:
        for i in range(7):
            if i in stats:
                w = stats[i]["wins"]
                n = stats[i]["plays"]
                if n > 0:
                    v = w / n
                    print(f"Column {i+1}: {v:.2f}")
                else:
                    print(f"Column {i+1}: 0.00")
            else:
                print(f"Column {i+1}: Null")
        print(f"FINAL Move selected: {final_move + 1}")

    return make_move(board, final_move, player), final_move

# --- Main program ---
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python part1Algo2.py <filename> <verbose> <param>")
        sys.exit(1)

    filename = sys.argv[1]
    verbose = sys.argv[2].lower() == "true"
    param = int(sys.argv[3])

    algorithm, player, board = read_input(filename)

    if check_win(board, player):
        print(f"Player {player} has already won!")
        print("Clear board for a new game.")
        sys.exit(0)

    if verbose:
        print(f"Algorithm: {algorithm}")
        print(f"Player: {player}")
        print(f"Param: {param}")
        print("Current board:")
        print_board(board)
        print("Legal moves:", legal_moves(board))
        print()

    # Choose algorithm
    if algorithm == "UR":
        board, move = run_ur(board, player, param, verbose)
    elif algorithm == "PMCGS":
        board, move = run_pmcgs(board, player, param, verbose)
    elif algorithm == "UCT":
        board, move = run_uct(board, player, param, verbose)
    else:
        print(f"Unknown algorithm: {algorithm}")
        sys.exit(1)

    print(f"Move selected: {move + 1}")
    print()

    if check_win(board, player):
        print(f"Player {player} wins!")
        print_board(board)
        update_board_player(filename, algorithm, player, board)
        sys.exit(0)
    else:
        next_player = 'Y' if player == 'R' else 'R'
        update_board_player(filename, algorithm, next_player, board)

    print("Board after move:")
    print_board(board)
