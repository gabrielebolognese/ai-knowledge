"""Play against your engine in the terminal.

    python play.py                         # you play White, engine thinks 2 s per move
    python play.py --color black --movetime 5000
    python play.py --eval material         # play the classic engine instead of the network
    python play.py --fen "<FEN>"           # start from any position

Type moves in SAN (Nf3, exd5, O-O, e8=Q) or UCI (g1f3). Other commands:
    undo   take back your last move (and the engine's reply)
    hint   let the engine suggest a move for you
    fen    print the position as FEN
    quit
"""
import argparse

import chess

from eval_material import MaterialEvaluator
from eval_nn import NNEvaluator, find_weights
from search import Searcher, score_to_uci

PIECES = {"P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
          "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"}


def show(board: chess.Board, flip: bool, unicode: bool):
    ranks = range(8) if flip else range(7, -1, -1)
    files = range(7, -1, -1) if flip else range(8)
    print()
    for r in ranks:
        row = []
        for f in files:
            piece = board.piece_at(chess.square(f, r))
            sym = piece.symbol() if piece else "."
            row.append(PIECES.get(sym, sym) if unicode else sym)
        print(f" {r + 1}  " + " ".join(row))
    print("    " + " ".join("abcdefgh"[f] for f in files) + "\n")


def parse_move(board: chess.Board, text: str):
    for parse in (board.parse_san, board.parse_uci):
        try:
            return parse(text)
        except ValueError:
            continue
    return None


def main():
    p = argparse.ArgumentParser(description="Play against the engine")
    p.add_argument("--color", choices=["white", "black"], default="white")
    p.add_argument("--movetime", type=int, default=2000, help="engine thinking time in ms")
    p.add_argument("--eval", choices=["auto", "nn", "material"], default="auto")
    p.add_argument("--weights", default=None, help="NumPy weights (default checkpoints/evaluator.npz)")
    p.add_argument("--fen", default=chess.STARTING_FEN)
    p.add_argument("--ascii", action="store_true", help="letters instead of chess symbols")
    a = p.parse_args()

    weights = find_weights(a.weights)
    if a.eval != "material" and weights is not None and weights.exists():
        evaluator = NNEvaluator(weights, accumulator=True)
    else:
        if a.eval == "nn":
            print("no trained network found (run train.py); using the material evaluator")
        evaluator = MaterialEvaluator()
    print(f"engine evaluator: {evaluator.name}, {a.movetime} ms per move")

    searcher = Searcher(evaluator)
    board = chess.Board(a.fen)
    human = chess.WHITE if a.color == "white" else chess.BLACK

    while not board.is_game_over(claim_draw=True):
        show(board, flip=human == chess.BLACK, unicode=not a.ascii)
        if board.turn == human:
            text = input("your move> ").strip()
            if text == "quit":
                return
            if text == "fen":
                print(board.fen())
                continue
            if text == "undo":
                if len(board.move_stack) >= 2:
                    board.pop()
                    board.pop()
                continue
            if text == "hint":
                r = searcher.search(board, time_limit=a.movetime / 1000)
                print(f"hint: {board.san(r.move)} ({score_to_uci(r.score)})")
                continue
            move = parse_move(board, text)
            if move is None:
                print("not a legal move here; legal moves:", ", ".join(board.san(m) for m in board.legal_moves))
                continue
            board.push(move)
        else:
            r = searcher.search(board, time_limit=a.movetime / 1000)
            nps = int(r.nodes / r.seconds) if r.seconds else 0
            print(f"engine plays {board.san(r.move)}   (depth {r.depth}, {score_to_uci(r.score)}, "
                  f"{r.nodes:,} nodes, {nps:,} nodes/s)")
            board.push(r.move)

    show(board, flip=human == chess.BLACK, unicode=not a.ascii)
    outcome = board.outcome(claim_draw=True)
    print(f"game over: {outcome.termination.name.lower()}, result {outcome.result()}")
    print("PGN moves:", chess.Board(a.fen).variation_san(board.move_stack))


if __name__ == "__main__":
    main()
