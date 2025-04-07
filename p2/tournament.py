from connect4 import run_ur, run_pmcgs, run_uct, check_win, legal_moves, run_uct_pb, run_uct_rave

# Board setup
ROWS, COLUMNS = 6, 7
EMPTY = 'O'

def make_empty_board():
    return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]

def play_game(alg1, alg2, param1, param2):
    board = make_empty_board()
    player = 'R'
    other_player = 'Y'

    while True:
        if player == 'R':
            board, _ = alg1(board, player, param1, verbose=False)
        else:
            board, _ = alg2(board, player, param2, verbose=False)

        if check_win(board, player):
            return player
        if not legal_moves(board):
            return 'D'

        player, other_player = other_player, player

# Algorithms with proper names and parameters
algorithms = [
    ("UR", run_ur, None),
    ("PMCGS500", run_pmcgs, 500),
    ("PMCGS10000", run_pmcgs, 10000),
    ("UCT500", run_uct, 500),
    ("UCT10000", run_uct, 10000)
]

results = {}
games_per_matchup = 100

for name1, alg1, param1 in algorithms:
    results[name1] = {}
    for name2, alg2, param2 in algorithms:
        wins1 = 0
        for _ in range(games_per_matchup):
            winner = play_game(alg1, alg2, param1, param2)
            if winner == 'R':
                wins1 += 1
        win_rate = wins1 / games_per_matchup
        results[name1][name2] = win_rate

# Print the results table
print(f"{'':12}", end="")
for name2, _, _ in algorithms:
    print(f"{name2:12}", end="")
print()

for name1 in results:
    print(f"{name1:12}", end="")
    for name2 in results[name1]:
        print(f"{results[name1][name2]:<12.2f}", end="")
    print()

# --- IMPROVED UCT TEST ---
print("Testing UCT_PB vs UCT10000...")
uct_improved_wins = 0
uct_baseline_wins = 0
draws = 0
num_games = 100

for _ in range(num_games):
    winner = play_game(run_uct_pb, run_uct, 10000, 10000)
    if winner == 'R':
        uct_improved_wins += 1
    elif winner == 'Y':
        uct_baseline_wins += 1
    else:
        draws += 1

print("\nUCT_PB vs UCT10000 Results:")
print(f"UCT_PB wins: {uct_improved_wins}/{num_games}")
print(f"UCT10000 wins: {uct_baseline_wins}/{num_games}")
print(f"Draws: {draws}/{num_games}")


# --- IMPROVED UCT TEST 2 ---
print("Testing UCB_Rave vs UCT10000...")
uct_improved_wins = 0
uct_baseline_wins = 0
draws = 0
num_games = 100

for _ in range(num_games):
    winner = play_game(run_uct_rave, run_uct, 10000, 10000)
    if winner == 'R':
        uct_improved_wins += 1
    elif winner == 'Y':
        uct_baseline_wins += 1
    else:
        draws += 1

print("\nUCT_Rave vs UCT10000 Results:")
print(f"UCT_Rave wins: {uct_improved_wins}/{num_games}")
print(f"UCT10000 wins: {uct_baseline_wins}/{num_games}")
print(f"Draws: {draws}/{num_games}")