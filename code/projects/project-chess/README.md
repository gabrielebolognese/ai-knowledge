# Mini chess engine: alpha-beta search with a neural evaluator

Companion code for the **Mini chess engine** project track of AI Knowledge. It is a small "mini-Stockfish" in Python. A classic alpha-beta search imagines the future, and a 768→256→32→1 neural network that you train yourself on Stockfish evaluations from the free Lichess database judges the positions. The engine speaks UCI, so any chess GUI can load it.

| File | What it does | Lesson |
|---|---|---|
| `eval_material.py` | Material + piece-square tables (the classic baseline evaluator) | Material and piece-square tables |
| `search.py` | Negamax + alpha-beta, MVV-LVA, killer and history ordering, quiescence, iterative deepening with time control, transposition table on python-chess Zobrist keys | Negamax / Move ordering / Iterative deepening |
| `data.py` | Streams the Lichess evaluation database (CC0), filters quiet positions, encodes 768 one-hot features + side-to-move centipawns | A training set from Lichess |
| `model.py` | The 768→256→32→1 PyTorch network (EmbeddingBag first layer, ClippedReLU) and the win-probability loss | Training the evaluator |
| `train.py` | Trains on a CPU and exports NumPy weights | Training the evaluator |
| `eval_nn.py` | The network as a search evaluator in NumPy: cache, NNUE-style incremental accumulator, batched inference | Plugging the network into search |
| `uci.py` | A UCI engine (uci, isready, setoption, ucinewgame, position, go, stop, quit) with the search on a thread | Capstone: UCI and Elo |
| `play.py` | Play against the engine in the terminal | Capstone |
| `bench.py` | Perft check, nodes/second, accumulator check, UCI compliance check, matches with Elo estimates (against the PST engine or Stockfish) | all |
| `sample/lichess_eval_sample.csv` | 4,000 raw records from the Lichess evaluation database (CC0), so the smoke tests work offline | |

## Install

Python 3.11 or newer, then:

```bash
pip install chess numpy            # the engine, play.py, uci.py, bench.py
pip install torch zstandard        # only for training (train.py) and the full download (data.py)
```

The library is called `chess` on PyPI, not `python-chess` (that name is an old shim). If you have no Python set up yet, see the course's optional Setup track.

## Quick start (about one minute)

```bash
python eval_material.py        # checkpoint numbers for the classic evaluator
python search.py               # mate-in-1, mate-in-2, a free queen and Kiwipete at depth 4
python data.py --smoke         # bundled sample -> data/smoke.npz
python train.py --smoke        # ~15 s: trains a tiny net, saves checkpoints/smoke.npz
python bench.py --smoke        # perft, speed, accumulator check, UCI check
python play.py --eval material # play the classic engine
```

## The full pipeline

```bash
python data.py --positions 1000000     # streams ~1.7 M records, keeps ~1 M quiet positions (network-bound, ~20 min)
python train.py --epochs 20            # CPU training, roughly 1 min per epoch per million positions (1 M: ~19 min)
python bench.py --speed                # compare evaluators
python bench.py --match pst --games 100 --movetime 200   # does the network beat the hand-written tables?
python play.py                         # play the network engine
```

`train.py` writes `checkpoints/evaluator.npz`. `uci.py`, `play.py` and `bench.py` pick it up automatically. Without it they fall back to the material evaluator and say so. Data and checkpoints are git-ignored.

## Load the engine in a chess GUI

The engine is a Python script, so a GUI starts it as `python uci.py`. Use the full path to your Python and to `uci.py`. You can also point the GUI at `minifish.bat` (Windows) or `minifish.sh` (macOS/Linux) next to this file: they run the same command with the course's `.venv` Python (three folders up) when it exists, because a GUI does not activate your virtual environment, and fall back to the Python on your PATH.

- **[Cute Chess](https://cutechess.com/)** (free, Windows/macOS/Linux; [releases](https://github.com/cutechess/cutechess/releases)): *Tools → Settings → Engines → +*. Set **Command** to `python uci.py` (or the path to `minifish.bat`), set **Working Directory** to this folder and **Protocol** to UCI. Then *Game → New*, choose the engine as one player and a time control such as 2 min + 1 s.
- **[Arena](http://www.playwitharena.de/)** (free, Windows): *Engines → Install New Engine*, select `minifish.bat` and confirm the UCI protocol.
- **[En Croissant](https://encroissant.org/)** (free, open source, Windows/macOS/Linux): *Engines → Add new → Local*, then pick `minifish.bat` (Windows) or `minifish.sh` (macOS/Linux, run `chmod +x minifish.sh` first).
- **[fastchess](https://github.com/Disservin/fastchess)** (command line, for matches): `fastchess -engine cmd=minifish.bat name=MiniFish -engine cmd=stockfish name=SF option.UCI_LimitStrength=true option.UCI_Elo=1320 -each tc=60+0.6 -rounds 50 -repeat -concurrency 2`. Check the protocol first with `fastchess --compliance minifish.bat`.

UCI options: `Eval` (auto / nn / material), `EvalFile` (default `checkpoints/evaluator.npz`), `Accumulator` (incremental first layer, on by default), `Move Overhead` (ms kept in reserve, default 100), `Hash` (transposition-table entries).

## Testing against Stockfish

Download Stockfish from [stockfishchess.org/download](https://stockfishchess.org/download/). Then:

```bash
python bench.py --match stockfish --stockfish path/to/stockfish --sf-skill 0 --games 20
python bench.py --match stockfish --stockfish path/to/stockfish --sf-elo 1320 --games 50
```

`--sf-elo` uses Stockfish's `UCI_LimitStrength` + `UCI_Elo` (minimum 1320), which Stockfish calibrates against the CCRL 40/4 rating list. The result is an estimate on that engine scale, not a FIDE or Lichess rating. `Skill Level` is not calibrated in Elo, so a Skill Level match only tells you how you compare with that particular opponent.

## Honest expectations

- **Speed:** python-chess move generation is pure Python, so this engine searches thousands of nodes per second. Stockfish searches tens of millions per second on a desktop CPU. Expect depth 4-6 at a few seconds per move.
- **Strength:** the engine plays legal, tactically aware chess and finds short mates, but **it will lose every game against full-strength Stockfish.** Weakened Stockfish (Skill Level 0, UCI_Elo 1320) is the realistic yardstick. Measure your own numbers with `bench.py` and report them with their error bars: 100 games give about ±70 Elo.
- **The network:** it plays legal, sensible chess, but in our tests it was **weaker than the hand-written tables**. Measured on one laptop at 0.2-0.3 s per move:

  | Engine | Opponent | Result | Elo difference (95 % interval) |
  |---|---|---|---|
  | NN, 1 M Lichess positions | material + PST engine | +8 =0 −22 (30 games) | −176 (−366 to −53) |
  | NN, 2 M Lichess positions | material + PST engine | +6 =5 −19 (30 games) | −161 (−316 to −51) |
  | material + PST engine | Stockfish 19, UCI_Elo 1320 | +7 =2 −1 (10 games) | +241 (+66 to no upper bound) |
  | NN, 1 M Lichess positions | Stockfish 19, UCI_Elo 1320 | +4 =2 −4 (10 games) | 0 (−217 to +217) |

  Smaller nets undervalue material in the unbalanced positions a search explores, because human-game analyses rarely contain them (removing a rook cost 48 cp in the 300 k net's eyes, 221 cp at 1 M and 593 cp at 2 M). At 2 M positions material is roughly right, but positional judgement in unfamiliar positions and a slower search (about 5,000-6,000 vs 7,000-12,000 nodes/s) still cost it games. Things that help: more data (5 M positions or more), positions from your own engine's games scored by Stockfish through python-chess `engine.analyse`, and richer NNUE-style features. These are small samples: run your own matches and report the error bars.

## Licences

The course code is MIT. It imports [python-chess](https://github.com/niklasf/python-chess) (GPL-3.0). If you distribute a combined program, check the GPL terms. The Lichess databases, including the bundled sample, are released under CC0 ([database.lichess.org](https://database.lichess.org/)).
