"""Smoke tests for all the course's companion code: does every project still run end to end?

    python code/run_smoke_tests.py                  # every project (about 5-10 minutes on a laptop CPU)
    python code/run_smoke_tests.py chess text       # only the projects whose name contains these words
    python code/run_smoke_tests.py --list           # show the commands without running them
    python code/run_smoke_tests.py --big-downloads  # also run steps that download hundreds of MB (EMNIST)

Run it with the course's virtual environment (code/requirements.txt installed). Each step is a real
command a learner would type: it runs as its own subprocess, from the project's folder, with a timeout.
For each project that means the train script in --smoke mode (a tiny but complete version of the real
pipeline: same data loader, same model, same training loop, just fewer examples and steps), then a
quick inference or evaluation entry point that loads the checkpoint the smoke run just saved.

Three advanced-track scripts in code/core/advanced/ run too, on the digits smoke checkpoint.

The chess project also gets a perft(3) from the start position (must be 8,902 positions) and a raw
UCI handshake over stdin/stdout: 'uci' -> 'uciok', 'isready' -> 'readyok',
'position startpos' + 'go depth 3' -> a legal 'bestmove'.

The tkinter drawing apps cannot open a window here, so they run with --check: tkinter is imported and
a drawing goes through the real preprocessing into a model, without a window or a checkpoint.

Network: MNIST (11 MB, torchvision) and the 2-class Quick, Draw! smoke set (0.8 MB) download on the
first run if they are not in the project's data/ folder yet. Everything else is bundled.

The script ends with a PASS / FAIL / SKIP table and exits with 1 if any step failed.
"""
import argparse
import os
import queue
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

CODE = Path(__file__).resolve().parent
PROJECTS = CODE / "projects"
PY = sys.executable


@dataclass
class Step:
    project: str
    name: str
    args: list                      # arguments after `python`
    cwd: Path
    timeout: int = 300              # seconds
    expect: str | None = None       # regex the output must contain
    skip_unless: Path | None = None  # skip (with a reason) when this path does not exist
    skip_reason: str = ""
    func: object = None             # a Python callable instead of a subprocess (returns (ok, output))
    result: dict = field(default_factory=dict)


# ------------------------------------------------------------------------------------- chess extras
START_PERFT_3 = 8_902               # https://www.chessprogramming.org/Perft_Results (initial position)


def uci_handshake(cwd: Path, timeout: int):
    """Talk to uci.py through raw pipes, exactly as a chess GUI does, and check every answer."""
    import chess

    log = []
    proc = subprocess.Popen([PY, "uci.py"], cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines: queue.Queue = queue.Queue()
    threading.Thread(target=lambda: [lines.put(s.rstrip("\n")) for s in proc.stdout], daemon=True).start()

    def send(cmd):
        log.append(f"> {cmd}")
        proc.stdin.write(cmd + "\n")
        proc.stdin.flush()

    def wait_for(pattern, seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            try:
                line = lines.get(timeout=max(0.05, end - time.monotonic()))
            except queue.Empty:
                break
            log.append(f"< {line}")
            if re.search(pattern, line):
                return line
        raise TimeoutError(f"no line matching {pattern!r} within {seconds} s")

    ok = False
    try:
        send("uci")
        wait_for(r"^uciok$", 30)
        # Use the network the smoke run just trained, so the handshake exercises the NN evaluator.
        send("setoption name EvalFile value checkpoints/smoke.npz")
        send("setoption name Eval value nn")
        send("isready")
        wait_for(r"^readyok$", 30)
        send("ucinewgame")
        send("position startpos")
        send("go depth 3")
        best = wait_for(r"^bestmove ", timeout).split()[1]
        legal = chess.Move.from_uci(best) in chess.Board().legal_moves
        log.append(f"bestmove {best} is {'legal' if legal else 'ILLEGAL'} in the start position")
        send("position startpos moves e2e4 e7e5")
        send("go depth 3")
        best2 = wait_for(r"^bestmove ", timeout).split()[1]
        board = chess.Board()
        for m in ("e2e4", "e7e5"):
            board.push_uci(m)
        legal2 = chess.Move.from_uci(best2) in board.legal_moves
        log.append(f"bestmove {best2} is {'legal' if legal2 else 'ILLEGAL'} after 1.e4 e5")
        loaded_nn = not any("could not load" in s or "not found" in s for s in log)
        log.append("NN evaluator loaded" if loaded_nn else "NN evaluator NOT loaded")
        send("quit")
        proc.wait(timeout=15)
        ok = legal and legal2 and loaded_nn and proc.returncode == 0
    except Exception as e:  # report, never hang
        log.append(f"ERROR: {e}")
    finally:
        if proc.poll() is None:
            proc.kill()
    return ok, "\n".join(log)


def launcher_check(cwd: Path, timeout: int):
    """Start the GUI launcher (minifish.bat on Windows, minifish.sh elsewhere) the way a chess GUI does."""
    cmd = ["cmd.exe", "/c", str(cwd / "minifish.bat")] if os.name == "nt" else ["sh", str(cwd / "minifish.sh")]
    try:
        p = subprocess.run(cmd, cwd=cwd, input="uci\nisready\nquit\n", capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"{cmd[-1]} timed out after {timeout} s"
    out = (p.stdout + p.stderr).strip()
    return ("uciok" in out and "readyok" in out), f"$ {' '.join(cmd)}\n{out}"


# ------------------------------------------------------------------------------------------- steps
def steps(big_downloads: bool):
    d = PROJECTS / "project-digits-letters"
    q = PROJECTS / "project-doodles"
    t = PROJECTS / "project-text"
    c = PROJECTS / "project-code-autocomplete"
    ch = PROJECTS / "project-chess"
    adv = CODE / "core" / "advanced"
    emnist = d / "data" / "EMNIST"
    return [
        Step("setup", "verify_setup.py", ["setup/verify_setup.py"], CODE, 120, r"All checks passed\."),
        Step("samples", "neuron.py", ["samples/neuron.py"], CODE, 60),
        Step("samples", "gradient_descent.py", ["samples/gradient_descent.py"], CODE, 60),

        Step("digits-letters", "train --smoke (CNN, MNIST)", ["train.py", "--smoke"], d, 600, r"test accuracy"),
        Step("digits-letters", "train --smoke --model mlp", ["train.py", "--smoke", "--model", "mlp"], d, 600,
             r"test accuracy"),
        Step("digits-letters", "train --smoke --dataset letters", ["train.py", "--smoke", "--dataset", "letters"],
             d, 900, r"test accuracy",
             skip_unless=None if big_downloads else emnist,
             skip_reason="EMNIST is a 562 MB download: run with --big-downloads, or download it once with "
                         "python data.py --dataset letters"),
        Step("digits-letters", "evaluate --smoke", ["evaluate.py", "--ckpt", "checkpoints/mnist-cnn-smoke.pt",
                                                    "--smoke", "--no-plots"], d, 300, r"accuracy"),
        Step("digits-letters", "preprocess --check (200 redrawn images)",
             ["preprocess.py", "--check", "--ckpt", "checkpoints/mnist-cnn-smoke.pt", "--n", "200"], d, 300),
        Step("digits-letters", "draw_app --check (tkinter, no window)", ["draw_app.py", "--check"], d, 120,
             r"check passed"),
        Step("digits-letters", "draw_app --selftest", ["draw_app.py", "--selftest", "--ckpt",
                                                      "checkpoints/mnist-cnn-smoke.pt"], d, 120, r"seven\s+->"),

        # Advanced-track scripts that build on the digits project (they reuse its smoke checkpoint and data).
        Step("core-advanced", "tictactoe_search.py", ["tictactoe_search.py"], adv, 120, r"a draw with perfect play"),
        Step("core-advanced", "quantize_cnn.py (digits smoke CNN)",
             ["quantize_cnn.py", "--checkpoint", str(d / "checkpoints" / "mnist-cnn-smoke.pt")], adv, 300,
             r"int8-Linear\s+accuracy"),
        Step("core-advanced", "transfer_digits_to_letters.py (200 letters, 1 epoch)",
             ["transfer_digits_to_letters.py", "--checkpoint", str(d / "checkpoints" / "mnist-cnn-smoke.pt"),
              "--train-size", "200", "--test-size", "500", "--epochs", "1"], adv, 600, r"finetune .*test accuracy",
             skip_unless=None if big_downloads else emnist,
             skip_reason="needs the 562 MB EMNIST download (see the letters step above)"),

        Step("doodles", "download --smoke (0.8 MB)", ["download.py", "--smoke"], q, 300),
        Step("doodles", "train --smoke", ["train.py", "--smoke"], q, 600, r"test"),
        Step("doodles", "evaluate --smoke", ["evaluate.py", "--ckpt", "checkpoints/doodles-smoke.pt", "--smoke",
                                             "--no-plots"], q, 300, r"accuracy"),
        Step("doodles", "draw_app --check (tkinter, no window)", ["draw_app.py", "--check"], q, 120,
             r"check passed"),
        Step("doodles", "draw_app --selftest", ["draw_app.py", "--selftest", "--ckpt",
                                               "checkpoints/doodles-smoke.pt"], q, 120, r"star \(5 points\)\s+->"),

        Step("text", "bigram --smoke", ["bigram.py", "--smoke"], t, 300, r"smoke test passed"),
        Step("text", "mlp_lm --smoke", ["mlp_lm.py", "--smoke"], t, 300, r"smoke test passed"),
        Step("text", "char_rnn --smoke", ["char_rnn.py", "--smoke"], t, 300, r"smoke test passed"),
        Step("text", "train_classifier --smoke (bag)", ["train_classifier.py", "--smoke"], t, 300,
             r"smoke test passed"),
        Step("text", "train_classifier --smoke --model bilstm", ["train_classifier.py", "--smoke", "--model",
                                                                 "bilstm"], t, 600, r"smoke test passed"),
        Step("text", "generate (MLP names)", ["generate.py", "--model", "checkpoints/mlp-smoke.pt", "--num", "5"],
             t, 120),
        Step("text", "generate (GRU names)", ["generate.py", "--model", "checkpoints/rnn-names-smoke.pt",
                                              "--num", "5"], t, 120),
        Step("text", "classify (bag)", ["classify.py", "--model", "checkpoints/bag-smoke.pt",
                                        "What a wonderful, moving film.", "The battery died after one day."],
             t, 120, r"(positive|negative)[\s\S]*(positive|negative)"),

        Step("code-autocomplete", "model.py self-test", ["model.py"], c, 300),
        Step("code-autocomplete", "train --smoke", ["train.py", "--smoke"], c, 1200, r"smoke test OK"),
        Step("code-autocomplete", "complete (char-smoke)",
             ["complete.py", "--ckpt", "checkpoints/char-smoke.pt", "--prompt", "def add(a, b):\\n",
              "--max-new", "60", "--seed", "0"], c, 300),
        Step("code-autocomplete", "complete --quantize (int8)",
             ["complete.py", "--ckpt", "checkpoints/char-smoke.pt", "--prompt", "for i in range(",
              "--max-new", "40", "--seed", "0", "--stop", "line", "--quantize"], c, 300),
        Step("code-autocomplete", "evaluate (5 functions)",
             ["evaluate.py", "--ckpt", "checkpoints/char-smoke.pt", "--n", "5", "--max-new", "120", "--show", "1"],
             c, 600, r"pars"),

        Step("chess", "data --smoke (bundled Lichess sample)", ["data.py", "--smoke"], ch, 300),
        Step("chess", "train --smoke", ["train.py", "--smoke"], ch, 600),
        Step("chess", f"perft(3) start position = {START_PERFT_3:,}",
             ["-c", "import chess, bench; n = bench.perft(chess.Board(), 3); print('perft(3) =', n); "
                    f"raise SystemExit(0 if n == {START_PERFT_3} else 1)"], ch, 120, rf"perft\(3\) = {START_PERFT_3}"),
        Step("chess", "UCI handshake (uci/isready/position/go depth 3)", [], ch, 120,
             func=lambda: uci_handshake(ch, 120)),
        Step("chess", "GUI launcher (minifish.bat / minifish.sh)", [], ch, 60, func=lambda: launcher_check(ch, 60)),
        Step("chess", "eval_nn on the smoke net", ["eval_nn.py", "--weights", "checkpoints/smoke.npz"], ch, 120),
        Step("chess", "search depth 3 (material eval)", ["search.py", "--depth", "3"], ch, 300, r"best "),
        Step("chess", "search depth 2 (smoke NN eval)", ["search.py", "--depth", "2", "--nn", "checkpoints/smoke.npz"],
             ch, 300, r"best "),
        Step("chess", "bench --smoke (perft, speed, accumulator, UCI)", ["bench.py", "--smoke"], ch, 900,
             r"smoke passed"),
    ]


def run(step: Step) -> dict:
    if step.skip_unless is not None and not step.skip_unless.exists():
        return {"status": "SKIP", "seconds": 0.0, "output": step.skip_reason}
    t0 = time.perf_counter()
    if step.func is not None:
        ok, out = step.func()
        return {"status": "PASS" if ok else "FAIL", "seconds": time.perf_counter() - t0, "output": out}
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", MPLBACKEND="Agg")
    try:
        p = subprocess.run([PY, *step.args], cwd=step.cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=step.timeout, env=env)
        out = (p.stdout + ("\n" + p.stderr if p.stderr.strip() else "")).strip()
        ok = p.returncode == 0
        why = "" if ok else f"exit code {p.returncode}"
        if ok and step.expect and not re.search(step.expect, out):
            ok, why = False, f"output does not match {step.expect!r}"
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""))
        ok, why = False, f"timed out after {step.timeout} s"
    res = {"status": "PASS" if ok else "FAIL", "seconds": time.perf_counter() - t0, "output": out}
    if why:
        res["why"] = why
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("only", nargs="*", help="run only projects whose name contains one of these words")
    ap.add_argument("--list", action="store_true", help="print the steps without running them")
    ap.add_argument("--big-downloads", action="store_true", help="also run steps that need large downloads")
    ap.add_argument("--verbose", "-v", action="store_true", help="print every step's full output")
    a = ap.parse_args()

    todo = [s for s in steps(a.big_downloads) if not a.only or any(w in s.project for w in a.only)]
    if a.list:
        for s in todo:
            cmd = "(in-process UCI handshake)" if s.func else "python " + " ".join(s.args)
            print(f"{s.project:<18} {s.cwd.relative_to(CODE.parent).as_posix():<38} {cmd}")
        return
    print(f"Python {sys.version.split()[0]} at {PY}")
    try:
        import torch
        print(f"torch {torch.__version__}, {torch.get_num_threads()} CPU threads")
    except ImportError:
        print("torch is not installed in this environment: see code/requirements.txt")

    t_all = time.perf_counter()
    for i, s in enumerate(todo, 1):
        print(f"[{i:>2}/{len(todo)}] {s.project}: {s.name} ...", end=" ", flush=True)
        s.result = run(s)
        r = s.result
        print(f"{r['status']} ({r['seconds']:.1f} s)" + (f" - {r['why']}" if r.get("why") else ""), flush=True)
        if r["status"] == "FAIL" or a.verbose:
            tail = "\n".join(r["output"].splitlines()[-40:])
            print("      " + tail.replace("\n", "\n      "), flush=True)

    width = max(len(f"{s.project}: {s.name}") for s in todo)
    print("\n" + "=" * (width + 22))
    print(f"{'step':<{width}}  {'result':<6}  {'time':>8}")
    print("-" * (width + 22))
    for s in todo:
        print(f"{s.project + ': ' + s.name:<{width}}  {s.result['status']:<6}  {s.result['seconds']:>7.1f}s")
    print("-" * (width + 22))
    counts = {k: sum(s.result["status"] == k for s in todo) for k in ("PASS", "FAIL", "SKIP")}
    print(f"{counts['PASS']} passed, {counts['FAIL']} failed, {counts['SKIP']} skipped "
          f"in {time.perf_counter() - t_all:.0f} s")
    for s in todo:
        if s.result["status"] == "SKIP":
            print(f"skipped {s.project}: {s.name}: {s.result['output']}")
    sys.exit(1 if counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
