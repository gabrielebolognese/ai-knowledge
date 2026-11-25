"""Minimax, negamax and alpha-beta on a tiny tree and on tic-tac-toe.

    python tictactoe_search.py      # no third-party packages needed

Part 1 replays the three-move tree from the lesson and lists which leaves
alpha-beta actually looks at. Part 2 searches tic-tac-toe from the empty board
with plain minimax, negamax, alpha-beta and alpha-beta with move ordering, and
counts the positions each one visits. All four agree on the value (a draw).
"""

# ---------------------------------------------------------------- part 1: the lesson's tree
# The root is a MAX node with three moves; each leads to a MIN node with three leaves.
TREE = {"a": [4, 6, 5], "b": [7, 2, 9], "c": [1, 8, 3]}


def alphabeta_tree(tree, order):
    """Two-ply alpha-beta (MAX at the root, MIN below). Returns (value, leaves seen)."""
    alpha, seen = float("-inf"), []
    for move in order:
        beta = float("inf")                 # best (lowest) score MIN has found in this branch
        for leaf in tree[move]:
            seen.append(f"{move}:{leaf}")
            beta = min(beta, leaf)
            if beta <= alpha:               # MAX already has alpha elsewhere: stop this branch
                break
        alpha = max(alpha, beta)            # the branch is worth at most beta to MAX
    return alpha, seen


# ---------------------------------------------------------------- part 2: tic-tac-toe
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
ORDER = [4, 0, 2, 6, 8, 1, 3, 5, 7]         # centre, then corners, then edges


def winner(b):
    for i, j, k in LINES:
        if b[i] != "." and b[i] == b[j] == b[k]:
            return b[i]
    return None


def moves(b, ordered=False):
    squares = ORDER if ordered else range(9)
    return [s for s in squares if b[s] == "."]


def other(p):
    return "O" if p == "X" else "X"


class Counter:
    nodes = 0


def minimax(b, player, c):
    """Score from X's point of view: +1 X wins, -1 O wins, 0 draw. X maximises, O minimises."""
    c.nodes += 1
    w = winner(b)
    if w:
        return 1 if w == "X" else -1
    ms = moves(b)
    if not ms:
        return 0
    scores = []
    for s in ms:
        b[s] = player
        scores.append(minimax(b, other(player), c))
        b[s] = "."
    return max(scores) if player == "X" else min(scores)


def negamax(b, player, c):
    """Same search, written once: the score is for the side to move, and we flip the sign."""
    c.nodes += 1
    w = winner(b)
    if w:
        return -1                            # the previous move won, so the side to move lost
    ms = moves(b)
    if not ms:
        return 0
    best = -2
    for s in ms:
        b[s] = player
        best = max(best, -negamax(b, other(player), c))
        b[s] = "."
    return best


def alphabeta(b, player, alpha, beta, c, ordered=False):
    """Negamax with an alpha-beta window; returns the same value as negamax."""
    c.nodes += 1
    w = winner(b)
    if w:
        return -1
    ms = moves(b, ordered)
    if not ms:
        return 0
    best = -2
    for s in ms:
        b[s] = player
        score = -alphabeta(b, other(player), -beta, -alpha, c, ordered)
        b[s] = "."
        best = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta:                    # beta cutoff: the opponent will avoid this line
            break
    return best


def best_move(b, player):
    """The first move with the best negamax score (alpha-beta with ordering)."""
    scored = []
    for s in moves(b, ordered=True):
        b[s] = player
        scored.append((-alphabeta(b, other(player), -2, 2, Counter(), True), s))
        b[s] = "."
    return max(scored, key=lambda t: t[0])   # max keeps the first of equal scores


def main():
    print("Part 1: the three-move tree from the lesson")
    for order in (["a", "b", "c"], ["c", "b", "a"]):
        value, seen = alphabeta_tree(TREE, order)
        print(f"  order {''.join(order)}: value {value}, {len(seen)} of 9 leaves seen: {' '.join(seen)}")
    best_case = {"a": [4, 6, 5], "b": [2, 7, 9], "c": [1, 8, 3]}
    value, seen = alphabeta_tree(best_case, ["a", "b", "c"])
    print(f"  best ordering: value {value}, {len(seen)} of 9 leaves seen (3^1 + 3^1 - 1 = 5)")

    print("\nPart 2: tic-tac-toe from the empty board (X to move)")
    rows = []
    for name, run in [
        ("minimax", lambda c: minimax(list("........."), "X", c)),
        ("negamax", lambda c: negamax(list("........."), "X", c)),
        ("alpha-beta", lambda c: alphabeta(list("........."), "X", -2, 2, c)),
        ("alpha-beta + ordering", lambda c: alphabeta(list("........."), "X", -2, 2, c, True)),
    ]:
        c = Counter()
        rows.append((name, run(c), c.nodes))
    for name, value, nodes in rows:
        print(f"  {name:<22} value {value:+d}   positions visited {nodes:>7,}")
    print("  (value 0 = a draw with perfect play)")

    b = list("X...O....")                     # squares 0-8 row by row: X took 0, O took 4
    score, square = best_move(b, "X")
    print(f"\nX holds corner 0 and O the centre 4: X's best move is square {square} (score {score:+d}).")


if __name__ == "__main__":
    main()
