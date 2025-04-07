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
    # Get the columns where the top row is empty
    return [col for col in range(COLUMNS) if board[0][col] == EMPTY]

# Make a move
def make_move(board, col, player):
    do_move(board, col, player)
    return board

# Win checkers
def horizontal_win_check(board, player):
    # Check horizontal win
    for row in range(ROWS):
        for col in range(COLUMNS - 3):
            if all(board[row][col + i] == player for i in range(4)):
                return True
    return False

def vertical_win_check(board, player):
    # Check vertical win
    for col in range(COLUMNS):
        for row in range(ROWS - 3):
            if all(board[row + i][col] == player for i in range(4)):
                return True
    return False

def diagonal_win_check(board, player):
    # Check diagonal win (bottom-left to top-right and top-left to bottom-right)
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
    # Check for win conditions
    return (
        horizontal_win_check(board, player) or
        vertical_win_check(board, player) or
        diagonal_win_check(board, player)
    )

# Update file after move
def update_board_player(filename, algorithm, next_player, board):
    # Update the file with the new player and board state
    with open(filename, 'w') as f:
        f.write(f"{algorithm}\n")
        f.write(f"{next_player}\n")
        for row in board:
            f.write(''.join(row) + '\n')
    print(f"Updated {filename} with next player {next_player}.")

# Do/undo move functions (in-place board edits)
def do_move(board, col, player):
    # Place the player's piece in the lowest available row in the column
    for row in reversed(range(ROWS)):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return row  # return the row where the move was placed
    return None  # should not happen if legal_moves used properly

def undo_move(board, col, row):
    # Remove the player's piece from the specified row and column
    if row is not None:
        board[row][col] = EMPTY

def simulate_random_game_verbose(board, current_player, opponent, verbose):
    # Simulate a random game from the current board state
    turn = opponent
    moves_sequence = []

    while True:
        # Get the list of legal (non-full) columns
        moves = legal_moves(board)

        # If there are no legal moves left, it's a draw
        if not moves:
            if verbose:
                print("TERMINAL NODE VALUE: 0")
            return 0
        # Randomly select a move from the available legal moves
        move = random.choice(moves)
        moves_sequence.append(move)

        if verbose:
            print(f"Move selected: {move + 1}")

        # Play the move and get the row where the token landed
        row = do_move(board, move, turn)
        if row is None:
            continue  # Skip if move failed

        if check_win(board, turn):
            # Check if the current player has won
            if verbose:
                print(f"TERMINAL NODE VALUE: {'1' if turn == current_player else '-1'}")
            undo_move(board, move, row)
            return 1 if turn == current_player else -1

        turn = 'Y' if turn == 'R' else 'R'


def run_ur(board, player, param=None, verbose=True):
    # Run the UR algorithm
    legal = legal_moves(board)

    # If no legal moves, return the board unchanged and None as the move
    if not legal:
        if verbose:
            print("No legal moves available.")
        return board, None
    
    # Randomly select one of the legal moves
    move = random.choice(legal)
    if verbose:
        print(f"FINAL Move selected: {move + 1}")

    # Apply the selected move to the board
    board = make_move(board, move, player)
    return board, move


def run_pmcgs(board, player, param, verbose):
    # Run the PMCGS algorithm
    legal = legal_moves(board)
    # Initialize stats: wi = total win score, ni = number of simulations
    stats = {move: {"wi": 0, "ni": 0} for move in legal}
    opponent = 'Y' if player == 'R' else 'R'
    if verbose:
        print(f"Running PMCGS with {param} simulations per move.")
        print(f"Legal moves: {legal}")

    # Loop over each legal move to evaluate it
    for move in legal:
        ## Simulate the move and update stats
        if verbose:
            print(f"\nEvaluating move: {move + 1}")

        # Perform 'param' number of random simulations for each move
        for _ in range(param):
            # Simulate the move
            row = do_move(board, move, player)
            if row is None:
                continue  # Skip if move failed
            if stats[move]["ni"] == 0 and verbose:
                print("NODE ADDED\n")

            # Simulate a full random game from this position
            result = simulate_random_game_verbose(board, player, opponent, verbose)
            undo_move(board, move, row)
            # Update statistics: win result (+1, 0, -1)
            stats[move]["wi"] += result
            stats[move]["ni"] += 1
            if verbose:
                print("Updated values:")
                print(f"wi: {stats[move]['wi']}")
                print(f"ni: {stats[move]['ni']} \n")
    # After all simulations, choose the move with the highest total win score
    best_move = max(legal, key=lambda m: stats[m]["wi"])

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
    # Run the UCT algorithm
    legal = legal_moves(board)

    # Initialize statistics for each legal move
    stats = {move: {"wins": 0, "plays": 0} for move in legal}
    opponent = 'Y' if player == 'R' else 'R'
    C = math.sqrt(2)# UCT exploration constant
    if verbose:
        print(f"Running UCT with {param} simulations total.")
        print(f"Legal moves: {legal}")
    for sim in range(param):
        # Calculate UCB scores for each legal move
        total_plays = sum(stats[move]["plays"] for move in legal) + 1
        ucb_scores = {}
        for move in legal:
            # Calculate UCB score for each move
            w = stats[move]["wins"]
            n = stats[move]["plays"]
            ucb_scores[move] = float("inf") if n == 0 else (w / n) + C * math.sqrt(math.log(total_plays) / n)

        # Select the move with the highest (or lowest, depending on player) UCB score
        best_move = max(legal, key=lambda m: ucb_scores[m]) if player == 'R' else min(legal, key=lambda m: ucb_scores[m])
        # Perform the move and simulate the game
        if verbose:
            print(f"\nwi: {stats[best_move]['wins']}")
            print(f"ni: {stats[best_move]['plays']}")
            for i in range(7):
                if i in stats:
                    w, n = stats[i]["wins"], stats[i]["plays"]
                    v = (w / n) if n > 0 else 0.0
                    print(f"V{i+1}: {v:.2f}" if i in legal else f"V{i+1}: Null")
                else:
                    print(f"V{i+1}: Null")
            print(f"Move selected: {best_move + 1}")
        #Apply the selected move
        row = do_move(board, best_move, player)
        if row is None:
            continue  # Skip if move failed
        # Simulate a random game from this state
        winner = simulate_random_game_verbose(board, player, opponent, verbose)
        undo_move(board, best_move, row)
        #Update statistics
        stats[best_move]["plays"] += 1
        if winner == player:
            # Update win count for the best move
            stats[best_move]["wins"] += 1
        if verbose:
            print("Updated values:")
            print(f"wi: {stats[best_move]['wins']}")
            print(f"ni: {stats[best_move]['plays']}")
    # After all simulations, determine the move with the best win rate
    final_move = None
    best_value = float('-inf') if player == 'R' else float('inf')
    for move in legal:
        # Calculate win rate for each move
        w, n = stats[move]["wins"], stats[move]["plays"]
        value = w / n if n > 0 else 0.0
        if (player == 'R' and value > best_value) or (player == 'Y' and value < best_value):
            best_value = value
            final_move = move
    if verbose:
        for i in range(7):
            if i in stats:
                w, n = stats[i]["wins"], stats[i]["plays"]
                v = w / n if n > 0 else 0.0
                print(f"Column {i+1}: {v:.2f}")
            else:
                print(f"Column {i+1}: Null")
        print(f"FINAL Move selected: {final_move + 1}")
    return make_move(board, final_move, player), final_move


def run_uct_rave(board, player, param, verbose):
    legal = legal_moves(board)
    # UCT stats: tracks win/play counts per move
    stats = {move: {"wins": 0, "plays": 0} for move in legal}
    # RAVE stats: global statistics updated for all moves seen in rollouts
    rave_stats = {move: {"wins": 0, "plays": 0} for move in legal}
    opponent = 'Y' if player == 'R' else 'R'
    C = math.sqrt(2)
    beta_const = 300  # Controls RAVE influence

    preferred_columns = [3, 2, 4, 1, 5, 0, 6]  # center-favoring heuristic

    def rollout(sim_board, turn):
        """
        Run a rollout simulation using center-biased move selection on a copied board.
        Returns result (+1, -1, or 0) and move history for RAVE updates.
        """
        move_history = []
        max_steps = ROWS * COLUMNS
        for _ in range(max_steps):
            moves = legal_moves(sim_board)
            if not moves:
                return 0, move_history  # Draw
            # Prefer center columns if available, else random
            move = next((m for m in preferred_columns if m in moves), random.choice(moves))
            row = do_move(sim_board, move, turn)
            move_history.append((move, row))
            # If current turn player wins, return result
            if check_win(sim_board, turn):
                return 1 if turn == player else -1, move_history
            turn = 'Y' if turn == 'R' else 'R'
        return 0, move_history # Draw if no winner after max moves

    for sim in range(param):
        total_plays = sum(stats[m]["plays"] for m in legal) + 1

        ucb_scores = {}
        #Calculate combined UCT-RAVE score for each move

        for move in legal:
            wi = stats[move]["wins"]
            ni = stats[move]["plays"]
            wi_rave = rave_stats[move]["wins"]
            ni_rave = rave_stats[move]["plays"]
            # Weighting factor to interpolate between UCT and RAVE
            beta = ni_rave / (ni + ni_rave + beta_const)
            # UCT win rate estimate
            v_uct = (wi / ni) if ni > 0 else 0
            # RAVE win rate estimate
            v_rave = (wi_rave / ni_rave) if ni_rave > 0 else 0
            # UCT-RAVE combined score
            ucb_scores[move] = (1 - beta) * v_uct + beta * v_rave + C * math.sqrt(math.log(total_plays) / (ni + 1e-6))

        # Choose best move based on combined score
        best_move = max(ucb_scores, key=ucb_scores.get)
        row = do_move(board, best_move, player)
        if row is None:
            continue  # Skip illegal moves

        # Run simulation on a separate copy of the board
        sim_board = [r[:] for r in board]
        result, move_history = rollout(sim_board, opponent)

        undo_move(board, best_move, row)  # Only undo root move

        stats[best_move]["plays"] += 1
        if result == 1:
            stats[best_move]["wins"] += 1

        # Update RAVE stats for all moves seen in rollout
        for m, _ in move_history:
            if m in rave_stats:
                rave_stats[m]["plays"] += 1
                if result == 1:
                    rave_stats[m]["wins"] += 1

        # Print progress update every 100 simulations
        if verbose and (sim + 1) % 100 == 0:
            print(f"Simulation {sim + 1}/{param} complete")

    # Select final move based on win rate
    final_move = max(legal, key=lambda m: stats[m]["wins"] / stats[m]["plays"] if stats[m]["plays"] > 0 else -1)

    if verbose:
        print("\nFinal move stats:")
        for move in range(COLUMNS):
            if move in stats and stats[move]["plays"] > 0:
                v = stats[move]["wins"] / stats[move]["plays"]
                print(f"Column {move + 1}: {v:.2f}")
            else:
                print(f"Column {move + 1}: Null")
        print(f"FINAL Move selected: {final_move + 1}")

    return make_move(board, final_move, player), final_move



def run_uct_pb(board, player, param, verbose):
    legal = legal_moves(board)
    # Initialize win and play statistics for each move
    stats = {move: {"wins": 0, "plays": 0} for move in legal}
    opponent = 'Y' if player == 'R' else 'R'
    C = math.sqrt(2)

    # Define a simple heuristic: bias toward center column (index 3)
    def heuristic(col):
        # Favor central columns (index 3 is center in 0-based indexing)
        return 1 - abs(3 - col) / 3  # range [0, 1]

    # Run the specified number of simulations
    for sim in range(param):
        total_plays = sum(stats[m]["plays"] for m in legal) + 1
        ucb_scores = {}
        # Compute UCB score + positional bias for each move
        for move in legal:
            w = stats[move]["wins"]
            n = stats[move]["plays"]
            # UCB formula: average win rate + exploration term
            ucb = (w / n if n > 0 else 0) + C * math.sqrt(math.log(total_plays) / (n + 1e-6))
            # Add positional bias (favoring center) scaled by a small factor (0.1)
            bias = heuristic(move)
            ucb_scores[move] = ucb + 0.1 * bias  # 0.1 is bias weight

        # Select the move with the highest combined UCB + bias score
        best_move = max(ucb_scores, key=ucb_scores.get)
        # Apply the move to the board
        row = do_move(board, best_move, player)
        if row is None:
            continue

        # Simulate a random game starting from the new state
        winner = simulate_random_game_verbose(board, player, opponent, verbose=False)
        undo_move(board, best_move, row)
        # Update statistics for the selected move
        stats[best_move]["plays"] += 1
        if winner == player:
            stats[best_move]["wins"] += 1
    # After simulations, choose the move with the highest average win rate
    final_move = max(legal, key=lambda m: stats[m]["wins"] / stats[m]["plays"] if stats[m]["plays"] > 0 else 0)
    if verbose:
        print(f"\nUCT-PB Move selected: {final_move + 1}")
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
    elif algorithm == "UCT-RAVE":
        board, move = run_uct_rave(board, player, param, verbose)
    elif algorithm == "UCT-PB":
        board, move = run_uct_pb(board, player, param, verbose)
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