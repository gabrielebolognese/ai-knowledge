"""A minimal UCI engine: load it in Cute Chess, Arena, En Croissant or fastchess.

    python uci.py            # then type: uci, isready, position startpos moves e2e4, go movetime 1000, quit

UCI (Universal Chess Interface) is the plain-text protocol between chess GUIs
and engines, over stdin/stdout. Specification (April 2006, Huber & Meyer-Kahlen):
https://backscattering.de/chess/uci/  Overview: https://www.chessprogramming.org/UCI

GUI -> engine (supported here)
    uci                        identify, list options, answer 'uciok'
    isready                    answer 'readyok' (also while searching)
    setoption name <id> value <x>
    ucinewgame                 clear the transposition table and history
    position startpos|fen <fen> [moves <m1> <m2> ...]
    go [wtime btime winc binc movestogo movetime depth nodes infinite]
    stop                       finish the search now and send 'bestmove'
    quit
Engine -> GUI
    id name / id author, option ..., uciok, readyok,
    info depth .. score cp|mate .. nodes .. nps .. time .. pv ..,  bestmove <move>

Extras for humans (not part of UCI): 'd' prints the board, 'eval' prints the evaluation.

The search runs on a background thread so the main thread keeps reading
commands: that is what makes 'stop' and 'isready' work during a search.
"""
import sys
import threading
from pathlib import Path

import chess

from eval_material import MaterialEvaluator
from search import Searcher, score_to_uci

ENGINE_NAME = "AIK MiniFish 1.0"
AUTHOR = "AI Knowledge course"
HERE = Path(__file__).parent

_out_lock = threading.Lock()


def send(line: str):
    with _out_lock:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


def load_evaluator(kind: str, eval_file: str, accumulator: bool):
    """'nn' or 'material' or 'auto' (= nn when a weights file exists, else material)."""
    path = Path(eval_file)
    if not path.is_absolute():
        path = HERE / path
    if kind in ("nn", "auto") and path.exists():
        try:
            from eval_nn import NNEvaluator
            return NNEvaluator(path, accumulator=accumulator)
        except Exception as e:  # a broken file should not kill the engine
            send(f"info string could not load {path}: {e}; using material eval")
    elif kind == "nn":
        send(f"info string {path} not found (run train.py); using material eval")
    return MaterialEvaluator()


def time_budget(board: chess.Board, args: dict, overhead_ms: int) -> float | None:
    """Seconds to think. None = no time limit (depth, nodes or infinite searches)."""
    if "movetime" in args:
        return max(0.01, (int(args["movetime"]) - overhead_ms) / 1000)
    mine = "wtime" if board.turn == chess.WHITE else "btime"
    inc_key = "winc" if board.turn == chess.WHITE else "binc"
    if mine not in args:
        return None
    left = int(args[mine])
    inc = int(args.get(inc_key, 0))
    moves_to_go = int(args.get("movestogo", 30))
    # Spend 1/movestogo of the clock plus most of the increment, never more than
    # half of what is left, and always keep a safety margin for Python's start-up/GC.
    budget = left / max(1, moves_to_go) + 0.75 * inc
    budget = min(budget, left / 2) - overhead_ms
    return max(0.01, budget / 1000)


class Engine:
    def __init__(self):
        self.options = {"Eval": "auto", "EvalFile": "checkpoints/evaluator.npz",
                        "Accumulator": True, "Move Overhead": 100, "Hash": 1_000_000}
        self.board = chess.Board()
        self.searcher = Searcher(load_evaluator("auto", self.options["EvalFile"], True))
        self.thread: threading.Thread | None = None
        self.infinite_done = threading.Event()

    # ------------------------------------------------------------- commands
    def cmd_uci(self):
        send(f"id name {ENGINE_NAME}")
        send(f"id author {AUTHOR}")
        send("option name Eval type combo default auto var auto var nn var material")
        send(f"option name EvalFile type string default {self.options['EvalFile']}")
        send("option name Accumulator type check default true")
        send("option name Move Overhead type spin default 100 min 0 max 5000")
        send("option name Hash type spin default 1000000 min 1000 max 20000000")
        send("uciok")

    def cmd_setoption(self, tokens):
        # setoption name <id with spaces> [value <x>]
        line = " ".join(tokens[1:])
        name, _, value = line.partition(" value ")
        name = name.removeprefix("name ").strip()
        value = value.strip()
        if name == "Move Overhead":
            self.options[name] = int(value)
        elif name == "Hash":
            self.options[name] = int(value)
            self.searcher.tt_size = int(value)
        elif name == "Accumulator":
            self.options[name] = value.lower() == "true"
        elif name in ("Eval", "EvalFile"):
            self.options[name] = value
        else:
            send(f"info string unknown option {name}")
            return
        if name in ("Eval", "EvalFile", "Accumulator"):
            self.wait()
            self.searcher.ev = load_evaluator(self.options["Eval"], self.options["EvalFile"], self.options["Accumulator"])
            send(f"info string evaluator: {self.searcher.ev.name}")

    def cmd_position(self, tokens):
        if len(tokens) < 2:
            return
        if tokens[1] == "startpos":
            board, rest = chess.Board(), tokens[2:]
        elif tokens[1] == "fen":
            if "moves" in tokens:
                k = tokens.index("moves")
                fen, rest = " ".join(tokens[2:k]), tokens[k:]
            else:
                fen, rest = " ".join(tokens[2:]), []
            board = chess.Board(fen)
        else:
            return
        if rest and rest[0] == "moves":
            for mv in rest[1:]:
                board.push_uci(mv)
        self.board = board

    def cmd_go(self, tokens):
        self.wait()
        args, i = {}, 1
        while i < len(tokens):
            t = tokens[i]
            if t in ("infinite", "ponder"):
                args[t] = True
                i += 1
            elif i + 1 < len(tokens):
                args[t] = tokens[i + 1]
                i += 2
            else:
                i += 1
        infinite = "infinite" in args
        limit = None if infinite else time_budget(self.board, args, self.options["Move Overhead"])
        depth = int(args.get("depth", 64))
        nodes = int(args["nodes"]) if "nodes" in args else None
        self.infinite_done.clear()
        board = self.board.copy()

        def info(d):
            pv = " ".join(m.uci() for m in d["pv"])
            send(f"info depth {d['depth']} score {score_to_uci(d['score'])} nodes {d['nodes']} "
                 f"nps {d['nps']} time {int(d['seconds'] * 1000)} pv {pv}")

        def run():
            try:
                result = self.searcher.search(board, max_depth=depth, time_limit=limit, node_limit=nodes, info=info)
                move = result.move
            except Exception as e:  # never leave the GUI without a bestmove
                send(f"info string search error: {e!r}")
                legal = list(board.legal_moves)
                move = legal[0] if legal else None
            if infinite:
                self.infinite_done.wait()   # 'go infinite' must not answer before 'stop'
            send(f"bestmove {move.uci() if move else '0000'}")

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        self.searcher.stop()
        self.infinite_done.set()
        self.wait()

    def wait(self):
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    # ------------------------------------------------------------- the loop
    def loop(self, stream=sys.stdin):
        for raw in stream:
            tokens = raw.strip().split()
            if not tokens:
                continue
            cmd = tokens[0]
            if cmd == "uci":
                self.cmd_uci()
            elif cmd == "isready":
                send("readyok")
            elif cmd == "setoption":
                self.cmd_setoption(tokens)
            elif cmd == "ucinewgame":
                self.wait()
                self.searcher.clear()
                if hasattr(self.searcher.ev, "cache"):
                    self.searcher.ev.cache.clear()
                self.board = chess.Board()
            elif cmd == "position":
                self.wait()
                self.cmd_position(tokens)
            elif cmd == "go":
                self.cmd_go(tokens)
            elif cmd == "stop":
                self.stop()
            elif cmd == "ponderhit":
                pass
            elif cmd == "quit":
                self.stop()
                break
            elif cmd == "d":
                send(str(self.board) + f"\nfen {self.board.fen()}")
            elif cmd == "eval":
                send(f"info string {self.searcher.ev.name}: {self.searcher.ev.evaluate(self.board)} cp (side to move)")
            else:
                send(f"info string unknown command: {cmd}")


if __name__ == "__main__":
    Engine().loop()
