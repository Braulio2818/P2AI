from connect4 import run_ur, run_pmcgs, run_uct, make_empty_board, check_win, legal_moves


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
            return 'D'  # Draw

        # Swap players
        player, other_player = other_player, player

# algorithms = [
#     ("UR", run_ur, None),
#     ("PMCGS500", run_pmcgs, 5),
#     ("PMCGS10000", run_pmcgs, 10),
#     ("UCT500", run_uct, 5),
#     ("UCT10000", run_uct, 10)
# ]

algorithms = [
    ("UR", run_ur, None),
    ("PMCGS5", run_pmcgs, 5),
    ("PMCGS20", run_pmcgs, 20),
    ("UCT5", run_uct, 5),
    ("UCT20", run_uct, 20)
]

results = {}

for name1, alg1, param1 in algorithms:
    results[name1] = {}
    for name2, alg2, param2 in algorithms:
        wins1 = 0
        for _ in range(100):
            winner = play_game(alg1, alg2, param1, param2)
            if winner == 'R':
                wins1 += 1
        win_rate = wins1 / 100
        results[name1][name2] = win_rate

print(f"{'':12}", end="")
for name2, _, _ in algorithms:
    print(f"{name2:12}", end="")
print()

for name1 in results:
    print(f"{name1:12}", end="")
    for name2 in results[name1]:
        print(f"{results[name1][name2]:<12.2f}", end="")
    print()
