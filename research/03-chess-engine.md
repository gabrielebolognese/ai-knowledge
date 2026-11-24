# Research 03: Chess engines with neural networks (the "mini-Stockfish" project)

> **Purpose.** This is the research brief for the hardest project in the course: a chess engine that **searches** with alpha-beta and **evaluates** positions with a small neural network the learner trains. It covers (a) the concepts, distilled with micro-step math and analogies, (b) a learner build path a CPU laptop can finish, (c) the optional NNUE-style accumulator upgrade, (d) expected strength and runtime, and (e) a bibliography.
>
> **Research date:** 2026-11-24. Facts about Stockfish, the Lichess database and python-chess were checked against the official pages on that date. Stockfish's network architecture changes every few months, so the course should cite the architecture history page instead of hard-coding sizes. All quoted numbers have a source link next to them. Numbers marked **(estimate)** are my engineering estimates, not published figures. The course must present them as estimates and teach the learner to measure their own.
>
> **Note on the Chessprogramming Wiki.** In November 2026 the wiki pages carry a banner saying they are a temporary read-only recovery copy. The content is intact and the URLs below work. If the wiki moves, the page titles stay the same.

---

## 0. The one-paragraph picture (for the course intro)

A chess engine has two halves. **Search** imagines the future: "if I play this, they play that, then I play this…". It builds a tree of possible move sequences. **Evaluation** looks at one frozen position at the end of a branch and guesses who is better, as a number in *centipawns* (100 cp ≈ one pawn). Classic engines hand-wrote the evaluation ("a knight is worth 3 pawns, a rook on an open file gets a bonus…"). Modern Stockfish replaced that with a neural network called **NNUE** ([Stockfish FAQ](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html), [CPW: NNUE](https://www.chessprogramming.org/NNUE)). Our learner engine keeps the classic search (alpha-beta) and swaps in a tiny network trained on positions that Stockfish already evaluated. Lichess publishes those positions for free under CC0 ([database.lichess.org](https://database.lichess.org/)).

**Analogy for the whole project:** search is the *lookahead* of a hiker choosing paths at forks. Evaluation is the hiker's *gut feeling* about how good the view is from any spot. A better gut feeling (the neural net) means you need to walk fewer paths to choose well. A faster walker (better search) can check more paths with the same gut feeling.

---

## (a) Concepts, distilled

Each concept below has: **what it is**, **analogy**, **micro-step math** (where relevant), and **what the learner implements**.

### a1. Board representation and move generation

**What.** The program needs a data structure for "where every piece is, whose turn it is, castling rights, the en-passant square, and the move counters". It also needs a function that lists every **legal** move. Serious engines use **bitboards**: one 64-bit integer per piece type, one bit per square. "One 64-bit word or register covers the whole board" ([CPW: Bitboards](https://www.chessprogramming.org/Bitboards)). Simpler engines use a "mailbox" array of 64 (or 120) squares ([CPW: Board Representation](https://www.chessprogramming.org/Board_Representation)). The position is written as text in **FEN** (Forsyth-Edwards Notation), e.g. `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1` ([CPW: FEN](https://www.chessprogramming.org/Forsyth-Edwards_Notation)).

**Analogy.** Bitboards are like 12 transparent overlays on the board, one per piece kind (white pawns, black knights…). Asking "which squares do white pawns attack?" means sliding one overlay one row up and diagonally. That is a single CPU instruction instead of a loop.

**Recommendation for learners: do not write a move generator first.** Writing one is a rite of passage, but it costs weeks of debugging around castling, en passant, pins and promotions. Use **python-chess**. It is a mature, GPL-3 library (`pip install chess`, imported as `chess`, the current docs state "Requires Python 3.11+"; changelog's newest dated entry read was v1.11.2, Feb 2025, so check PyPI before pinning) with `Board`, `legal_moves`, `push`/`pop`, `is_capture`, `gives_check`, `piece_map`, `outcome` and `fen()` ([python-chess docs](https://python-chess.readthedocs.io/en/latest/), [core API](https://python-chess.readthedocs.io/en/latest/core.html), [PyPI: chess](https://pypi.org/project/chess/)). An *optional* bonus lesson can have learners write their own generator and verify it with **perft**. Perft counts leaf nodes of the legal-move tree to a fixed depth and compares the counts with known values. For the start position the counts are 20; 400; 8,902; 197,281; 4,865,609; 119,060,324 for depths 1–6. "Kiwipete" `r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -` gives 48; 2,039; 97,862; 4,085,603 for depths 1–4 ([CPW: Perft Results](https://www.chessprogramming.org/Perft_Results), [CPW: Perft](https://www.chessprogramming.org/Perft)).

### a2. Evaluation 101: material and piece-square tables

**What.** A static evaluation function `eval(position) → centipawns`. The simplest useful one counts material. The [Simplified Evaluation Function](https://www.chessprogramming.org/Simplified_Evaluation_Function) by Tomasz Michniewski uses P = 100, N = 320, B = 330, R = 500, Q = 900, K = 20000. It adds **piece-square tables** (PSTs), small bonuses or penalties per piece per square, e.g. knights like the centre ([CPW: Piece-Square Tables](https://www.chessprogramming.org/Piece-Square_Tables)). "Most modern programs, influenced by Fruit, use two sets of tables" (opening and endgame) and blend them by game phase (same page; see [CPW: Tapered Eval](https://www.chessprogramming.org/Tapered_Eval)).

**Micro-step math.**
1. Material score for White: `M_w = 100·#P + 320·#N + 330·#B + 500·#R + 900·#Q`.
2. Same for Black: `M_b`.
3. Positional bonus: `S_w = Σ PST[piece][square]` over White pieces. Mirror the square for Black pieces.
4. White-relative score: `E_white = (M_w + S_w) − (M_b + S_b)`.
5. **Side-to-move relative** score, which negamax needs (a3): `E = E_white if White to move else −E_white`.

**Analogy.** Material is counting the money in each player's wallet. PSTs are "location, location, location": the same house (piece) is worth more in a good neighbourhood (square).

**Teaching link.** A PST is literally a **linear model**: one weight per (piece, square) pair, 768 weights total. That is the bridge to the neural network in a8. The NN keeps exactly the same 768 inputs but adds hidden layers, so it can learn *combinations* ("bishop pair", "king safety with queens on").

### a3. Minimax and negamax

**What.** Minimax: at my turn I pick the move that **maximizes** the score. At your turn you pick the one that **minimizes** it. Recurse to a depth, then call `eval` at the leaves ([CPW: Minimax](https://www.chessprogramming.org/Minimax)). **Negamax** is the same algorithm written once, using the identity `max(a, b) = −min(−a, −b)`. It requires the evaluation to be relative to the side to move ([CPW: Negamax](https://www.chessprogramming.org/Negamax)).

**Micro-step math.**
1. Define `V(p)` = value of position `p` *for the player to move*.
2. If `p` is a leaf, `V(p) = eval(p)` (side-to-move relative).
3. Otherwise `V(p) = max over moves m of ( −V(p after m) )`.
4. Why the minus? A position that is +3 for *my opponent* (they are to move there) is −3 *for me*.

**Analogy.** Two people take turns choosing between doors. Each always assumes the other will choose the door worst for them. Negamax is "flip the sign and repeat", like looking at the same scoreboard from the other side of the table.

**Cost.** With branching factor `b` (≈ 30–40 legal moves in a middlegame) and depth `d`, minimax visits `b^d` leaves. 35^4 ≈ 1.5 million, 35^6 ≈ 1.8 billion. This is why we need pruning.

### a4. Alpha-beta pruning

**What.** Alpha-beta returns *the same answer* as minimax while skipping branches that cannot affect the result: "Remarkably, it does this without any potential of overlooking a better move" ([CPW: Alpha-Beta](https://www.chessprogramming.org/Alpha-Beta)). It keeps a window `[α, β]`. `α` is the score I am already guaranteed elsewhere. `β` is the most my opponent will allow (they already have a refutation elsewhere). If a move scores `≥ β`, the opponent would never let us reach this node, so we stop searching it. That stop is a **beta cutoff**. The classic analysis is Knuth & Moore, *An Analysis of Alpha-Beta Pruning*, Artificial Intelligence 6(4), 1975 ([DOI](https://doi.org/10.1016/0004-3702%2875%2990019-3)).

**Micro-step math (why ordering matters).**
1. Worst case (moves searched in the worst order): no pruning, `b^d` leaves.
2. Best case (best move always searched first): `b^⌈d/2⌉ + b^⌊d/2⌋ − 1` leaves ([CPW: Alpha-Beta](https://www.chessprogramming.org/Alpha-Beta)).
3. Plug in `b = 40, d = 6`: minimax has 40^6 = 4,096,000,000 leaves. Perfect alpha-beta has 40^3 + 40^3 − 1 = 127,999 leaves (the same page gives this example).
4. Rule of thumb: perfect ordering roughly **doubles the reachable depth** for the same work, because `b^(d/2)` at depth `d` costs about what `b^d'` costs at `d' = d/2`.

**Analogy.** You are shopping for the cheapest flight. You already found one for €100 (α). The next airline's *first* quoted fare is €140 and it can only go up from there, so you leave that website without reading the rest. Alpha-beta is "stop reading a menu once you know you won't order from it".

**Code shape (learner version, fail-soft negamax):**

```python
INF, MATE = 10**9, 100_000

def negamax(board, depth, alpha, beta, ply):
    if depth == 0:
        return qsearch(board, alpha, beta, ply)          # see a6
    moves = order_moves(board, list(board.legal_moves))   # see a5
    if not moves:                                         # no legal move
        return -MATE + ply if board.is_check() else 0     # mated / stalemate
    if board.is_repetition(2) or board.halfmove_clock >= 100:
        return 0
    best = -INF
    for move in moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha, ply + 1)
        board.pop()
        if score > best:
            best = score
        if score > alpha:
            alpha = score
        if alpha >= beta:          # beta cutoff: opponent avoids this line
            break
    return best
```

`-MATE + ply` makes the engine prefer the *fastest* mate and the *slowest* loss. `board.is_repetition(2)` treats a single repetition inside the search as a draw, a common simplification.

### a5. Move ordering: hash move, MVV-LVA, killers, history

**What.** Alpha-beta is only as good as its ordering (a4, step 2). Standard order: **(1) TT/hash move** (a7). Per the TT page, "In Stockfish, 75% of cutoffs produced in a position with hash moves are caused by the hash move" ([CPW: Transposition Table](https://www.chessprogramming.org/Transposition_Table)). **(2) Good captures by MVV-LVA**, "Most Valuable Victim – Least Valuable Aggressor": try PxQ before QxP ([CPW: MVV-LVA](https://www.chessprogramming.org/MVV-LVA)). **(3) Killer moves**: quiet moves that caused a cutoff at the same ply in a sibling branch, "typically containing two or three moves per ply" ([CPW: Killer Heuristic](https://www.chessprogramming.org/Killer_Heuristic)). **(4) History heuristic**: a table `history[from][to]` that adds `depth²` every time a quiet move causes a cutoff, invented by Jonathan Schaeffer in 1983 ([CPW: History Heuristic](https://www.chessprogramming.org/History_Heuristic)). **(5) Everything else.** When MVV-LVA misjudges a defended victim, engines use static exchange evaluation ([CPW: SEE](https://www.chessprogramming.org/Static_Exchange_Evaluation)).

**Micro-step math (MVV-LVA score).** `score(capture) = 10 · value(victim) − value(attacker)`. PxQ = 10·900 − 100 = 8,900. QxP = 10·100 − 900 = 100. Sort captures by descending score.

**Analogy.** The detective interviews the most likely suspect first. If they confess (cutoff), the rest of the line-up goes home.

### a6. Quiescence search and the horizon effect

**What.** If the search stops at depth `d` in the middle of a capture sequence ("I take your queen…"), eval says "+9!" without seeing the recapture one ply later. That is the **horizon effect**. Quiescence search "is needed to avoid the horizon effect": at the leaves, keep searching **captures only** (optionally promotions and checks) until the position is quiet ([CPW: Quiescence Search](https://www.chessprogramming.org/Quiescence_Search), [CPW: Horizon Effect](https://www.chessprogramming.org/Horizon_Effect)). The **stand-pat** score, the static eval, acts as a lower bound. The side to move may decline all captures, so "doing nothing" is always an option, except when in check, where standing pat is not allowed (same page). The page also advises: "it's crucial to introduce simple capture ordering such as MVV-LVA before implementing qsearch."

**Analogy.** A photographer doesn't take the photo mid-sneeze. Quiescence waits until the "action" (captures) settles before freezing the frame for evaluation.

```python
def qsearch(board, alpha, beta, ply):
    stand_pat = evaluate(board)              # side-to-move relative
    if stand_pat >= beta:
        return stand_pat
    alpha = max(alpha, stand_pat)
    for move in mvv_lva_sorted(c for c in board.legal_moves if board.is_capture(c)):
        board.push(move)
        score = -qsearch(board, -beta, -alpha, ply + 1)
        board.pop()
        if score >= beta:
            return score
        alpha = max(alpha, score)
    return alpha
```

(This learner version stands pat even when in check. That is a documented simplification. The "advanced" lesson adds check evasions.)

### a7. Iterative deepening, Zobrist hashing, transposition tables

**Iterative deepening (ID).** Search depth 1, then 2, then 3… until time runs out. When interrupted, play the best move of the last *completed* iteration. ID is "the basic time management strategy in depth-first searches", and the earlier iterations seed move ordering ([CPW: Iterative Deepening](https://www.chessprogramming.org/Iterative_Deepening)). It sounds wasteful, but with branching factor `b` the shallower iterations together cost only about `1/(b−1)` of the last one.

*Micro-step math:* the total work for depths 1…d is `b + b² + … + b^d = b(b^d − 1)/(b − 1)`. Dividing by the last term `b^d` gives ≈ `b/(b−1)`. For an effective branching factor of 6 that is 6/5, i.e. **20 % overhead**, usually repaid by better ordering.

**Analogy:** a student who answers every exam question roughly, then goes back to refine. When the bell rings, they always have an answer sheet.

**Zobrist hashing.** Give every (piece, square) pair a random 64-bit number, plus numbers for side-to-move, castling and en passant. A position's hash is the XOR of the numbers of everything present. Moving a piece is two XORs (out of the old square, into the new one), because XOR undoes itself. Invented by Albert Zobrist (1970, *A New Hashing Method with Application for Game Playing*, U. Wisconsin TR #88) ([CPW: Zobrist Hashing](https://www.chessprogramming.org/Zobrist_Hashing)). With 64-bit keys collisions are rare. With 32-bit keys they become likely after about 2^16 positions (same page, birthday bound). python-chess provides `chess.polyglot.zobrist_hash(board)` ([python-chess: polyglot](https://python-chess.readthedocs.io/en/latest/polyglot.html)). In Python it is cheaper to use the built-in `board._transposition_key()` or to maintain your own incremental hash. Measure first.

**Analogy:** every position gets a fingerprint that you can update by "dabbing" two fingers instead of rescanning the whole hand.

**Transposition table (TT).** A dictionary `hash → (depth, score, flag, best_move)`. Different move orders often reach the same position (*transpositions*), so we reuse earlier results. Flags: **EXACT** (score inside the window, a PV node), **LOWERBOUND** (a beta cutoff happened, so the true score is ≥ the stored value), **UPPERBOUND** (all moves failed low, so the true score is ≤ the stored value). Cutoff rules: use an EXACT entry directly. Use a LOWERBOUND entry if `score ≥ β`. Use an UPPERBOUND entry if `score ≤ α`. In every case the stored depth must be at least the current remaining depth ([CPW: Transposition Table](https://www.chessprogramming.org/Transposition_Table)). The first TT was in Greenblatt's Mac Hack VI (same page). Mate scores must be stored relative to the node (add/subtract `ply`) so they stay correct when retrieved at another ply.

**Analogy:** a notebook of "positions I've already solved, how deeply, and whether my answer was exact or only 'at least'/'at most'".

### a8. Pruning and reductions (stretch goals)

- **Null-move pruning:** "In almost all chess positions, making a null move (passing a turn) is worse than the best legal move." So if *passing* still scores `≥ β` at reduced depth (R = 2 or 3), prune. Avoid it when in check or in king-and-pawn endings because of zugzwang ([CPW: Null Move Pruning](https://www.chessprogramming.org/Null_Move_Pruning)). *Analogy:* "Even if I let you move twice in a row you can't hurt me, so this position is already great."
- **Principal Variation Search (PVS):** search the first move with the full window and the rest with a zero window `[α, α+1]`. Re-search only if one beats α. "Modern chess programs find fail-highs on the first move around 90% of the time" ([CPW: PVS](https://www.chessprogramming.org/Principal_Variation_Search)).
- **Late Move Reductions (LMR):** search late, quiet moves at reduced depth and re-search if they surprise. It "became very popular in 2005 after Fruit and Glaurung" ([CPW: LMR](https://www.chessprogramming.org/Late_Move_Reductions)).
- **Aspiration windows:** start iteration `d` with a window of about ¼–½ pawn around the score of iteration `d−1`, and widen on failure ([CPW: Aspiration Windows](https://www.chessprogramming.org/Aspiration_Windows)).

For a Python learner engine, null move + PVS + LMR are optional. They help, but each one adds bugs that are hard to see. The course should present them in the "advanced" module with a strict A/B test (section d4) for each.

### a9. From hand-written eval to a neural evaluator

**The leap.** Replace `evaluate(board)` with `net(features(board))`. Train the net to imitate a strong teacher's evaluations: Stockfish scores from the Lichess evaluation database. This is plain **supervised regression**, the same skill as the digit/letter projects, applied to a chess-shaped input.

**Input encoding (768 one-hot).** For each of 2 colours × 6 piece types × 64 squares there is one input that is 1 if that piece is on that square and 0 otherwise. That gives 768 inputs, with at most 32 active. This "A" feature set is exactly the simple example in the official NNUE doc ([nnue-pytorch: NNUE doc](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)), also listed on [CPW: NNUE](https://www.chessprogramming.org/NNUE). **Side-to-move perspective:** if Black is to move, flip the board vertically and swap colours, so the net always sees the position "from the mover's chair" and outputs a side-to-move-relative score, exactly what negamax wants.

```python
import chess

def features(board: chess.Board) -> list[int]:
    """768 one-hot indices from the side to move's point of view."""
    stm, out = board.turn, []
    for sq, pc in board.piece_map().items():
        s = sq if stm == chess.WHITE else chess.square_mirror(sq)
        own = (pc.color == stm)
        out.append((0 if own else 384) + (pc.piece_type - 1) * 64 + s)
    return out
```

**Architecture (recommended): 768 → 256 → 32 → 1.**
- Layer 1: `h1 = clamp(W1·x + b1, 0, 1)`, W1 is 256×768. This clamped activation is **ClippedReLU**, which NNUE uses ([NNUE doc](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)).
- Layer 2: `h2 = clamp(W2·h1 + b2, 0, 1)`, W2 is 32×256.
- Output: `y = W3·h2 + b3`, a single number in "scaled centipawns".
- Parameters: 768·256 + 256 + 256·32 + 32 + 32 + 1 = **205,089**. That is tiny: it trains on a laptop CPU and the weights are under 1 MB.

**Micro-step math: why layer 1 is cheap even in Python.** `x` is 0/1 with ≤ 32 ones, so `W1·x` is just *the sum of ≤ 32 columns of W1*. No 768-wide multiplication is needed. This is the seed of the NNUE idea (section c).

**Target: centipawns squashed to win probability (WDL space).** Centipawns are unbounded (+1500 and +3000 are both "winning"), and a squared error on raw cp would obsess over big numbers that don't matter. The NNUE doc converts the score with a sigmoid: `wdl_space_eval = sigmoid(cp / scaling_factor)`, with `scaling_factor = 410  # this depends on the engine, and maybe even on the data`, and notes "Stockfish uses values around 400" ([NNUE doc: loss functions](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)).

*Micro-steps:*
1. `cp = 0` → `sigmoid(0) = 0.50` (equal).
2. `cp = +100` (one pawn) → `sigmoid(100/400) = sigmoid(0.25) ≈ 0.562`.
3. `cp = +400` → `sigmoid(1) ≈ 0.731`.
4. `cp = +1200` → `sigmoid(3) ≈ 0.953`. Beyond this, extra centipawns barely move the target, which is exactly what we want.

This is the same idea as **Texel's tuning method**. Peter Österlund fitted evaluation weights by minimizing `E = (1/N) Σ (R_i − Sigmoid(q_i))²`, where `R` is the game result (0, ½, 1) and `Sigmoid(s) = 1/(1 + 10^(−K·s/400))` with a fitted constant `K` ([CPW: Texel's Tuning Method](https://www.chessprogramming.org/Texel%27s_Tuning_Method)).

**WDL blending.** The NNUE doc blends the engine score with the actual game result: `wdl_value = lambda_ * wdl_space_eval + (1 - lambda_) * game_result`, and uses a loss with a power above 2. "Stockfish networks had good training results with an exponent of 2.6" ([NNUE doc](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)). **Important caveat for our data:** the Lichess *evaluation* database contains positions and evaluations only, **no game results** ([database.lichess.org](https://database.lichess.org/), format section). The course therefore offers two options:
- **Default (λ = 1):** pure eval imitation from the eval DB. Simple and enough for the project.
- **Optional blending:** take positions from the Lichess *games* database. Games that were computer-analysed carry `[%eval …]` comments in the PGN, and every game has a result tag, so learners get (FEN, eval, result) triples and can use λ ≈ 0.7–0.9 **(estimate, tune by A/B test)**. A lighter alternative is to convert cp into a WDL triple with python-chess `Score.wdl(model="sf")` ([python-chess: engine](https://python-chess.readthedocs.io/en/latest/engine.html)) and use expected score `W + D/2` as the target. That gives a calibrated *shape* but adds no new information.

**Analogy.** Imitating Stockfish's evals is like learning to price houses by copying an expert appraiser. Blending in the game result is like also checking what the houses actually sold for.

### a10. AlphaZero and Leela: the other way to put a network in an engine

**AlphaZero** (Silver et al., DeepMind; [arXiv 1712.01815](https://arxiv.org/abs/1712.01815), 2017; [Science 2018](https://www.science.org/doi/10.1126/science.aar6404)) learned chess from **self-play only**. It used a deep residual network with a **policy** head (which moves look promising) and a **value** head (who is winning), driving **Monte-Carlo Tree Search** with the PUCT rule instead of alpha-beta. The paper reports that it outperformed Stockfish "after just 4 hours" of training and searched "just 80 thousand positions per second in chess… compared to 70 million for Stockfish". Training used 5,000 first-generation TPUs for self-play and 64 second-generation TPUs for training ([arXiv HTML](https://arxiv.org/html/1712.01815v1)). **Leela Chess Zero (Lc0)** is the open-source, GPL-3 community project "inspired by DeepMind's AlphaZero project". It uses PUCT search with a network that provides "both value and policy" ([lczero.org](https://lczero.org/), [Lc0 technical explanation](https://lczero.org/dev/wiki/technical-explanation-of-leela-chess-zero/), [GitHub: LeelaChessZero/lc0](https://github.com/LeelaChessZero/lc0)).

*Micro-step math (PUCT).* At each node choose the move maximising `Q(s,a) + U(s,a)`, with `U(s,a) = c_puct · P(s,a) · √N(s) / (1 + N(s,a))`. Here `Q` is the average value found so far through move `a`, `P` is the policy prior, and the `N` are visit counts. Read it as **exploit** (high `Q`) plus **explore** (high prior, few visits) ([AlphaZero paper](https://arxiv.org/abs/1712.01815)).

**Why the course does *not* build this as the main project.** AlphaZero-style training needs millions of self-play games played by a large network, which means GPU/TPU-scale compute. The NNUE-style path (a small net, supervised on existing evals, inside alpha-beta) trains in minutes to hours on a CPU. It is also what Stockfish itself does. AlphaZero/Lc0 appears as an "advanced reading" lesson with the PUCT math and an optional toy MCTS on tic-tac-toe.

**Cross-pollination worth mentioning.** Stockfish 18 was trained on "over 100 billion positions of Lc0 evaluation data" ([Stockfish 18 blog](https://stockfishchess.org/blog/2026/stockfish-18/)), and Stockfish 19's data was rescored with "a strong Leela net" ([Stockfish 19 blog](https://stockfishchess.org/blog/2026/stockfish-19/)). The two families now teach each other.

### a11. NNUE in Stockfish: what the official docs say

- **Origin.** NNUE ("ƎUИИ", Efficiently Updatable Neural Network) was "introduced in 2018 by Yu Nasu" for computer shogi ([CPW: NNUE](https://www.chessprogramming.org/NNUE); paper: Nasu 2018, Ziosoft Computer Shogi Club; unofficial English translation by Dominik Klein at [github.com/asdfjkl/nnue](https://github.com/asdfjkl/nnue); overview: [Wikipedia: Efficiently updatable neural network](https://en.wikipedia.org/wiki/Efficiently_updatable_neural_network)). Nodchip ported it to Stockfish as a proof of concept. The large gain arrived with **Stockfish 12** in summer 2020 ([CPW: NNUE](https://www.chessprogramming.org/NNUE); [Stockfish 12 blog](https://stockfishchess.org/blog/2020/introducing-nnue-evaluation/)).
- **Design goals.** A wide, *sparse* first layer whose output (the **accumulator**) is updated incrementally move by move, followed by a few tiny dense layers, all in integer SIMD on the **CPU**. The FAQ notes Stockfish "uses the CPU only for chess evaluation", and that NNUE is stronger "but is significantly slower" per node than the old hand-crafted eval ([Stockfish FAQ](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html)).
- **Feature sets** ([NNUE doc](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)):
  - **A (768)**: piece × colour × square. The doc's simple example network is `A[768]->8->8->1`.
  - **HalfKP**: `(our_king_square, piece_square, piece_type, piece_color)` for non-king pieces, giving 64·64·5·2 = **40,960** inputs per perspective. That is "P taken 64 times, once for each king square". Its weakness: any king move changes every feature for that side, forcing a full refresh.
  - **HalfKA / HalfKAv2 / HalfKAv2_hm**: kings included as pieces. HalfKAv2_hm adds horizontal mirroring of the king half-board. The Stockfish source defines its size as 64·11·64/2 = **22,528** inputs ([Stockfish source at tag sf_19: half_ka_v2_hm.h](https://github.com/official-stockfish/Stockfish/blob/sf_19/src/nnue/features/half_ka_v2_hm.h), `Dimensions = SQUARE_NB * PS_NB / 2` with `PS_NB = 11 * SQUARE_NB`). On the master branch after SF19 this file has already been replaced by `k32h3.h`, which is why the course must cite a tag, not master.
  - Newer additions: **Full_Threats** (threat inputs) and **PP_3Wide** (pawn-pair) feature sets are listed in the same doc.
- **Architecture history** (official page: [NNUE architecture history](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue_architecture_history.html)):
  - **SFNNv1** is the "Stockfish 12 architecture" (2020-08-06). The NNUE doc describes Stockfish's move "from `256x2->32->32->1` to `1024x2->8->32->1`".
  - **SFNNv6–v9** grew L1 from 1024 to 1536, 2048, 2560 and finally 3072.
  - **SFNNv10** added FullThreats inputs and cut L1 back to 1024. It shipped in **Stockfish 18** (2026-01-31), whose blog says threat inputs "allow the engine to 'see' which pieces are threatened more naturally" ([Stockfish 18](https://stockfishchess.org/blog/2026/stockfish-18/)).
  - **Stockfish 19** (2026-09-05) ships **SFNNv16**, "reducing binary size by removing redundant threat features while increasing strength by introducing new pawn-pair features". It retires the secondary small net introduced in 16.1 and adds quantization-aware training, with "an Elo gain of up to 44 points" vs SF18 ([Stockfish 19](https://stockfishchess.org/blog/2026/stockfish-19/), [GitHub releases](https://github.com/official-stockfish/Stockfish/releases)).
  - **Development nets after SF19** replace HalfKAv2_hm with new king-bucketing schemes (K32Q2, then K32H3) and use up to 32 layer stacks (history page, SFNNv18–v20). **Course rule:** describe the *principles* (sparse inputs, perspective accumulators, tiny dense head, integer inference) and link the history page for current sizes. Never state "Stockfish's net is N×M" without a version and date.
- **Quantization** ([NNUE doc: Quantization](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)): the feature transformer uses **int16** weights, biases and accumulator, scaled by **127**, so ClippedReLU's float range 0..1 becomes 0..127. Hidden layers use **int8** weights with scale **64** (so the largest representable float weight is 127/64 ≈ 1.98), int32 biases and accumulation. The scale is a power of two, so rescaling is a bit shift. The output is scaled so that Stockfish's internal units come out (the doc mentions an output range of about −10000..10000). Training must clamp weights to these ranges so the quantized net matches the float one.
- **Trainers.** Official: [official-stockfish/nnue-pytorch](https://github.com/official-stockfish/nnue-pytorch) (GPU/CUDA-oriented, with a C++ data loader). Community: [bullet](https://github.com/jw1912/bullet) (Rust, CUDA/CPU, used by many engines such as Viridithas and Stormphrax). Learners do **not** need either: our 205k-parameter net trains in plain PyTorch on a CPU.

---

## (b) Recommended learner build path (CPU laptop)

The path is split into **10 milestones**, each a lesson with a runnable checkpoint in `code/projects/chess/`. Every milestone ends with a test the learner can run in seconds (`--smoke`). The engine plays legal chess from milestone 3 onward, so learners always have something that works.

| # | Milestone | New concept | Checkpoint test | Time (estimate) |
|---|---|---|---|---|
| 1 | Board & moves with python-chess | FEN, legal moves, push/pop | perft(3) from start = 8,902 through python-chess | 1 h |
| 2 | Material + PST eval | static eval, side-to-move sign | eval(start) = 0. Removing a white knight gives −320 from White's view | 1–2 h |
| 3 | Negamax + alpha-beta | recursion, pruning | finds mate-in-2 puzzles at depth 4. Same best move as plain minimax at depth 3 on 20 test FENs | 2–3 h |
| 4 | Move ordering | MVV-LVA, killers, history | node count at depth 4 drops ≥ 5× vs unordered (measured) | 1–2 h |
| 5 | Quiescence | horizon effect | does not "win" a defended pawn with the queen in the 5 horizon-trap test FENs | 1 h |
| 6 | Iterative deepening + TT | time control, Zobrist, bounds | respects `movetime`. TT hit rate > 0 and same best move with/without TT | 2–3 h |
| 7 | Dataset from the Lichess eval DB | streaming, filtering, encoding | 1–2 M (FEN, cp) pairs saved as compact index arrays | 1 h + download |
| 8 | Train the 768→256→32→1 evaluator | WDL-space loss, ClippedReLU | validation loss falls. Net says start ≈ 0 to +50 cp, queen-up ≫ 0 | 1–3 h CPU |
| 9 | Plug the net into search | NumPy inference, accumulator-lite | NN engine beats the PST engine in a 100-game match (a positive Elo with a 95 % CI) | 1–2 h |
| 10 | UCI wrapper + testing vs Stockfish | UCI protocol, fastchess, Elo/SPRT | passes `fastchess --compliance`. Elo estimate with error bars vs Stockfish `UCI_Elo` anchors | 2–4 h + match time |

### b1. Milestones 1–6: the classic engine

- **python-chess move gen.** `board = chess.Board()`, `board.legal_moves`, `board.push(m)`, `board.pop()`. The learner also writes a 10-line perft with python-chess to *see* the exponential tree ([core docs](https://python-chess.readthedocs.io/en/latest/core.html)).
- **Material eval** (a2), then PSTs. Keep `evaluate(board)` as the **single swap point** for the later NN.
- **Negamax + alpha-beta** (a3–a4). Count nodes, because every later optimisation is judged by "same move, fewer nodes".
- **Move ordering + quiescence + iterative deepening + TT** (a5–a7). Use a Python `dict` for the TT, keyed by the Zobrist hash, capped at ~1–2 M entries (clear it on `ucinewgame`).
- **Mate and draw handling:** stalemate = 0, repetition/50-move = 0, checkmate = `−MATE + ply`.
- **Testing:** a small set of tactical FENs from the Lichess puzzle database (CC0; 6,193,530 rated puzzles as of 2026-11-11, CSV with `FEN, Moves, Rating, Themes…`; the first move in `Moves` is the opponent's move that sets up the puzzle) ([database.lichess.org](https://database.lichess.org/)). Learners measure "% of 1200–1600-rated puzzles solved at 1 s/move" after each milestone. Good puzzles teach as well as test.

### b2. Milestone 7: dataset from the Lichess evaluation database

**Source.** `lichess_db_eval.jsonl.zst`: "417,862,375 chess positions evaluated with Stockfish" (page updated 2026-11-11), released, like all Lichess database exports, under **CC0** ([database.lichess.org](https://database.lichess.org/), [lichess-org/database on GitHub](https://github.com/lichess-org/database)). Format: one JSON object per line, with `fen` (pieces, side, castling, en passant only, no move counters) and `evals`, a list ordered by number of PVs. Each eval has `knodes`, `depth` and `pvs`. Each PV has `cp` (omitted if mate is certain) or `mate`, and `line` in UCI_Chess960 format. Official advice: "If you only want one PV, we recommend selecting the evaluation with the highest depth, and use its first PV." Mirrors in Parquet form exist on Hugging Face ([Lichess/chess-position-evaluations](https://huggingface.co/datasets/Lichess/chess-position-evaluations)). Their split files let learners download a slice instead of the whole archive.

**Don't download the whole file.** Stream it and stop after N positions. HTTP streaming plus the `zstandard` package ([python-zstandard docs](https://python-zstandard.readthedocs.io/)) means you only download what you decompress:

```python
import io, json, requests, zstandard as zstd   # pip install requests zstandard

URL = "https://database.lichess.org/lichess_db_eval.jsonl.zst"

def stream_positions(limit):
    with requests.get(URL, stream=True, timeout=60) as r:
        r.raise_for_status()
        reader = zstd.ZstdDecompressor().stream_reader(r.raw)
        for i, line in enumerate(io.TextIOWrapper(reader, encoding="utf-8")):
            if i >= limit:
                break
            rec = json.loads(line)
            best = max(rec["evals"], key=lambda e: e["depth"])
            pv = best["pvs"][0]
            cp = pv["cp"] if "cp" in pv else (3000 if pv["mate"] > 0 else -3000)
            yield rec["fen"], max(-3000, min(3000, cp)), pv["line"].split()[0]
```

**Filtering (quiet positions).** Our search evaluates mostly *quiet* leaves (quiescence resolves captures), so train on quiet positions. Skip positions where the side to move is in check, or where the best move (first PV move) is a capture or promotion. The official trainer does a similar filter of capture and in-check positions during data loading (see the "smart FEN skipping" option in [nnue-pytorch](https://github.com/official-stockfish/nnue-pytorch)). **Sign convention:** Lichess `cp` is from **White's** point of view (standard for Lichess analysis), so convert it to side-to-move: `cp_stm = cp if white_to_move else −cp`. *The course's smoke test asserts this on a known position (start position ≈ small positive for White) so a sign bug cannot hide.*

**Size.** 1 M positions is enough for a first net. 2–5 M gives a better one. Store each position as ≤ 32 `int16` feature indices plus an `int16` cp, about 66 bytes, so 2 M positions ≈ 130 MB in RAM/`.npz`. The download for 2 M positions is on the order of a few hundred MB **(estimate)**. **Bias warning for the lesson:** these are positions Lichess users chose to analyse, mostly from human games, at varying depths and Stockfish versions. That is fine for learning, but it is not a curated training set like Stockfish's.

### b3. Milestone 8: train the evaluator in PyTorch (CPU)

```python
import torch, torch.nn as nn

SCALE = 400.0                         # cp -> WDL space (NNUE doc uses ~400-410)

class Evaluator(nn.Module):
    def __init__(self, n_in=768, h1=256, h2=32):
        super().__init__()
        self.ft = nn.EmbeddingBag(n_in, h1, mode="sum")   # = sparse Linear(768, 256), no bias
        self.ft_bias = nn.Parameter(torch.zeros(h1))
        self.l1 = nn.Linear(h1, h2)
        self.out = nn.Linear(h2, 1)

    def forward(self, idx, offsets):                   # idx: all active features, flattened
        h = torch.clamp(self.ft(idx, offsets) + self.ft_bias, 0.0, 1.0)   # ClippedReLU
        h = torch.clamp(self.l1(h), 0.0, 1.0)
        return self.out(h).squeeze(-1)                 # "cp / SCALE" units

def loss_fn(pred, cp_stm, result=None, lam=1.0, power=2.6):
    target = torch.sigmoid(cp_stm / SCALE)
    if result is not None:                             # optional WDL blending (a9)
        target = lam * target + (1 - lam) * result
    return (torch.sigmoid(pred) - target).abs().pow(power).mean()
```

- `nn.EmbeddingBag(mode="sum")` computes exactly "sum the columns of the active features" without building a 768-wide dense tensor ([PyTorch: EmbeddingBag](https://docs.pytorch.org/docs/stable/generated/torch.nn.EmbeddingBag.html)). Adam with lr 1e-3, batch 1024–4096, and 10–30 epochs is a sensible default ([PyTorch: Adam](https://docs.pytorch.org/docs/stable/generated/torch.optim.Adam.html)). Hold out 5 % for validation.
- **Teaching the loss:** power 2 = MSE in WDL space. The doc's power 2.6 puts more weight on big misses ([NNUE doc](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)). Learners can A/B test 2.0 vs 2.6 as an exercise.
- **Sanity checks the course provides:** start position ≈ 0…+50 cp; mirrored positions give equal and opposite scores (the stm-flip guarantees this by construction); "white up a queen" ≫ +500; the validation loss curve is plotted.
- **CPU cost (estimate).** One epoch over 2 M positions is ≈ 2 M × (2·32·256 + 2·256·32 + …) ≈ 70 GFLOP forward and ~3× that with backward, so **about 1–3 minutes per epoch** on a 4–8-core laptop with PyTorch CPU. **20 epochs ≈ 20–60 min.** The companion `--smoke` mode trains on 20 k positions for 1 epoch in seconds.

### b4. Milestone 9: plug into search (fast inference in Python)

Calling PyTorch once per node is the classic learner trap: per-call overhead is tens of microseconds, which wrecks nodes-per-second **(estimate; measure with `timeit`)**. Instead:
1. Export the weights to NumPy (`W1: 768×256`, `b1`, `W2: 256×32`, `b2`, `W3`, `b3`).
2. Evaluate with `h = np.clip(W1[idx].sum(0) + b1, 0, 1)`, then `h2 = np.clip(h @ W2 + b2, 0, 1)`, then `cp = (h2 @ W3 + b3) * SCALE`.
3. Cache evals in the TT entry, or a small dict keyed by the Zobrist hash, because qsearch re-evaluates many positions.
4. Optional: the accumulator (section c) keeps `W1·x + b1` up to date move by move, so step 2's sum becomes 2–4 vector adds per move.

Also keep **mate scores outside the net**. The net only replaces `evaluate()`. Checkmate and stalemate detection stays in search.

### b5. Milestone 10: UCI wrapper

UCI (Universal Chess Interface, Huber & Meyer-Kahlen, 2000–2006) is the text protocol every GUI and tester speaks over stdin/stdout ([UCI spec, April 2006](https://backscattering.de/chess/uci/), [CPW: UCI](https://www.chessprogramming.org/UCI)). GUI → engine: `uci`, `isready`, `ucinewgame`, `position [startpos | fen …] moves …`, `go wtime btime winc binc movestogo depth nodes movetime infinite`, `stop`, `quit`. Engine → GUI: `id name/author`, `uciok`, `readyok`, `info depth … score cp … nodes … nps … pv …`, `bestmove <move>`. Moves are long algebraic (`e2e4`, `e7e8q`). Per the spec, `isready` must be answered with `readyok` even while searching, and `bestmove` "must always be sent if the engine stops searching".

```python
import sys, chess

def uci_loop(search):                          # search(board, time_s) -> chess.Move
    board = chess.Board()
    for line in sys.stdin:
        tok = line.split()
        if not tok: continue
        if tok[0] == "uci":
            print("id name MiniFish-NN\nid author Learner\nuciok", flush=True)
        elif tok[0] == "isready":
            print("readyok", flush=True)
        elif tok[0] == "ucinewgame":
            board = chess.Board()              # also clear TT / killers / history
        elif tok[0] == "position":
            if tok[1] == "startpos":
                board, rest = chess.Board(), tok[2:]
            else:                               # "position fen <6 fields> [moves ...]"
                board, rest = chess.Board(" ".join(tok[2:8])), tok[8:]
            if rest and rest[0] == "moves":
                for mv in rest[1:]:
                    board.push_uci(mv)
        elif tok[0] == "go":
            args = dict(zip(tok[1::2], tok[2::2]))
            if "movetime" in args:
                t = int(args["movetime"]) / 1000
            else:
                left = int(args.get("wtime" if board.turn else "btime", 10000))
                inc = int(args.get("winc" if board.turn else "binc", 0))
                t = max(0.05, left / 30_000 + inc / 2_000)   # simple time management
            print(f"bestmove {search(board, t).uci()}", flush=True)
        elif tok[0] == "quit":
            break
```

(A full version prints `info` lines per iteration and runs the search on a thread so `stop` works. The course companion code does this.) On Windows, testers launch the engine through a tiny `.bat` file (`@python -I engine.py`) or via `cmd=python args="engine.py"`.

### b6. Testing vs Stockfish at low strength and estimating Elo

**Opponent.** Stockfish (GPL-3, free; [stockfishchess.org/download](https://stockfishchess.org/download/)). Weakening options from the official command reference: `Skill Level` (0–20), `UCI_LimitStrength` + `UCI_Elo` (**min 1320, max 3190**). UCI_Elo is "calibrated at a time control of 120s+1s and anchored to CCRL 40/4" and "takes precedence over Skill Level" ([Stockfish UCI & commands](https://official-stockfish.github.io/docs/stockfish-wiki/UCI-Protocol-and-Stockfish-Commands.html), [Stockfish FAQ](https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html)). For opponents weaker than 1320, use `Skill Level 0` and/or limit nodes. **Teach the caveat:** a CCRL-anchored number is *not* a FIDE or Lichess rating. The FAQ says comparing against FIDE Elo "has become virtually impossible".

**Match runner.** [fastchess](https://github.com/Disservin/fastchess) (MIT, C++, "a chess cli tool to run engine vs engine matches") or [cutechess-cli](https://github.com/cutechess/cutechess) (GPL-3). Example (fastchess syntax from its [man page](https://github.com/Disservin/fastchess/blob/master/man.md)):

```
fastchess -engine cmd=minifish.bat name=MiniFish ^
          -engine cmd=stockfish.exe name=SF1320 option.UCI_LimitStrength=true option.UCI_Elo=1320 ^
          -each tc=60+0.6 -rounds 50 -repeat -concurrency 2 ^
          -openings file=8moves_v3.pgn format=pgn order=random -pgnout file=match.pgn
```

`-repeat` plays each opening with both colours, which cancels opening bias. Opening books come from [official-stockfish/books](https://github.com/official-stockfish/books). First check the protocol with `fastchess --compliance minifish.bat` (fastchess README).

**Elo from a match score (micro-steps).** Source: [CPW: Match Statistics](https://www.chessprogramming.org/Match_Statistics), [Wikipedia: Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system).
1. Score `s = (wins + draws/2) / games`. Example: 100 games, 40 W, 20 D, 40 L, so `s = 0.50`.
2. Expected score for a rating gap `Δ`: `E = 1 / (1 + 10^(−Δ/400))`.
3. Invert: `Δ = 400 · log10( s / (1 − s) )`. For s = 0.50, Δ = 0. For s = 0.64, Δ ≈ +100. For s = 0.76, Δ ≈ +200.
4. Error bar: the standard error of `s` is at most `√(s(1−s)/N)` (draws make it smaller). For N = 100 and s = 0.5 that is 0.05, so a 95 % interval of ±0.098 in score, which is about **±70 Elo** near 50 %. **Lesson: 100 games can only tell big differences apart.**
5. Rating your engine: `my_elo ≈ anchor_elo + Δ`, e.g. 1320 + Δ. Use 2–3 anchors (1320, 1500, 1700) and a range where the score is between 20 % and 80 %.
6. **LOS** (likelihood of superiority): `LOS = ½[1 + erf((W − L) / √(2W + 2L))]`. Draws drop out (same CPW page).

**SPRT (for A/B testing changes).** Do not run a fixed number of games. The Sequential Probability Ratio Test stops as soon as the evidence is strong enough, with four parameters `elo0, elo1, alpha, beta`. CPW calls it "generally regarded as the most important process in modern engine development" and gives the fastchess example `-sprt elo0=0 elo1=5 alpha=0.05 beta=0.05`. Stockfish's fishtest uses tighter bounds such as [0, 2] ([CPW: SPRT](https://www.chessprogramming.org/Sequential_Probability_Ratio_Test), [Fishtest](https://tests.stockfishchess.org/tests), [Fishtest wiki](https://github.com/official-stockfish/fishtest/wiki)). For a learner engine with big jumps (e.g. "add quiescence"), use `elo0=0 elo1=20` or `elo0=0 elo1=50` so tests finish in tens to a few hundred games **(recommendation)**. *Analogy:* a coin-fairness test where you keep flipping only until you're confident, instead of committing to 10,000 flips up front.

**Analysis helper.** python-chess can drive Stockfish directly to *analyse* positions: `chess.engine.SimpleEngine.popen_uci("stockfish")`, `engine.analyse(board, chess.engine.Limit(depth=12))`, `info["score"]` → `PovScore`, `.wdl(model="sf")` ([python-chess: engine](https://python-chess.readthedocs.io/en/latest/engine.html)). This is useful for the "label your own positions" bonus exercise. It is slow (≈ 0.1–1 s per position at modest depth, **estimate**), which is why we use the pre-labelled Lichess DB instead.

---

## (c) Optional upgrade: the NNUE-style accumulator

**Idea.** Layer 1's output `a = W1·x + b1` depends only on *which features are on*. A move changes only a handful of features, so update `a` instead of recomputing it ([NNUE doc: Accumulator](https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html)).

**Micro-step math.**
1. Full refresh: `a = b1 + Σ_{i ∈ active} W1[:, i]` (≤ 32 column adds).
2. A quiet move (knight g1→f3) turns off feature `(own knight, g1)` and turns on `(own knight, f3)`: `a' = a − W1[:, old] + W1[:, new]`. That is **2 column operations instead of ~32**.
3. Capture: 3 operations (mover off/on, victim off). Castling: 4 (king and rook move). Promotion: pawn off, new piece on, plus a victim if it captures. The doc: for the simple A set, "any move can only change at most 4 inputs (castling), and the average should be below 3".
4. Unmake = pop the previous accumulator from a stack (store one 256-vector per ply), or apply the reverse update.

**Two perspectives.** Real NNUE keeps **two** accumulators per position: one from White's view and one from Black's. It concatenates them as `[a_side_to_move, a_other]` before the next layer, so the net knows whose turn it is without flipping the board. For the 768 learner net that means: change the architecture to `(768 → 256) × 2 perspectives → concat 512 → 32 → 1`, sharing W1 between perspectives (the doc's `FeatureSet[N]->M*2->K->1` pattern). Then a move updates both accumulators incrementally. Our single-perspective "flip the board" net cannot be updated incrementally across a side change, because every feature flips. **That is the concrete reason Stockfish uses two perspectives.** This is a great "aha" for the lesson.

**King buckets (HalfKP/HalfKA).** Making the features depend on the king square lets the net learn "this piece matters differently depending on where my king is", which is king safety. The cost is that a king move refreshes that perspective's accumulator. The doc notes that one perspective "may happen that one is updated while the other needs a full refresh". Stockfish mitigates this with refresh caches (Finny tables, see [CPW: NNUE](https://www.chessprogramming.org/NNUE) and the source). For a learner, HalfKP-style inputs mean 40,960 × 256 ≈ 10.5 M first-layer weights. That is trainable on CPU, but it needs far more data than our 2 M positions to beat the 768 net **(estimate)**, so it is an "explore further" item.

**Quantization (stretch).** Convert W1/b1 to int16 ×127 and W2 to int8 ×64, as described in a11. In Python this is mostly *educational*: NumPy int16 adds are not dramatically faster than float32 at this size. The real win comes with a compiled language (C/C++/Rust with SIMD), which is what makes Stockfish fast. The lesson can show the 30-line NumPy quantized forward pass and check that it matches the float output within a few cp.

**Measured benefit in Python (estimate).** The accumulator turns "sum ~25 rows of 256 floats" into "2–4 row updates" per node. Since python-chess move generation and Python overhead dominate, expect roughly a **1.2–2× nps** gain, not the order-of-magnitude gain seen in C++. The course should say this honestly and frame the accumulator as *the idea that makes NNUE possible*, not a big Python speed-up.

---

## (d) Expected strength and runtime on a CPU laptop

> All numbers in this section are **estimates** for CPython 3.12+ on a 2020s 4–8-core laptop, unless a source is linked. Strength is in **CCRL-like Elo as anchored by Stockfish's UCI_Elo** (b6), not FIDE or Lichess. The course must present these as ranges and have learners measure their own with the b6 method.

### d1. Speed

| Engine stage | Nodes/second (CPython) | Typical depth at 1 s/move |
|---|---|---|
| Material + PST, alpha-beta, no ordering | 5–15 k | 3 |
| + MVV-LVA/killers + quiescence + ID + TT | 5–12 k (but far fewer nodes needed) | 4–5 (+ qsearch) |
| + NN eval in NumPy (no accumulator) | 3–8 k | 4 |
| + accumulator + eval cache | 4–10 k | 4–5 |
| Same engine under PyPy (material/PST only) | 2–5× CPython | +1 ply |

**Measured anchor point (research machine, 2026-11-24):** the a4/a6 snippets in this document (material-only eval via `piece_map()`, MVV-LVA capture ordering, quiescence) with python-chess 1.11.2 on CPython 3.13 searched the start position to depth 4 in **2,763 nodes / 0.37 s ≈ 7.5 k nodes/s**. The same script verified perft(3) = 8,902, the stm-flip symmetry of `features()`, and found the back-rank mate `a1a8` in `6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1`. The ranges above are scaled from this one measurement. Context for these figures: python-chess move generation is pure Python, so its speed bounds every Python engine. Sunfish, a ~111-line Python engine, says PyPy is "worth on the order of 100 Elo at fast time controls" ([Sunfish](https://github.com/thomasahle/sunfish)). PyTorch and NumPy do not run under PyPy, so the NN engine stays on CPython. For comparison, AlphaZero's paper quotes Stockfish at about 70 million positions per second on 64 threads ([arXiv](https://arxiv.org/html/1712.01815v1)). A Python engine is ~4 orders of magnitude slower per thread, and that is fine for learning.

### d2. Strength (estimates, to be measured in the course's own test runs)

| Stage | Expected Elo (vs SF `UCI_Elo` anchors, 60+0.6) |
|---|---|
| Material only, depth 3, no qsearch | 800–1100 (too weak for the 1320 anchor; use Skill Level 0 + node limits) |
| + PST + ordering + quiescence + ID + TT | 1300–1600 |
| + trained 768→256→32→1 NN eval (2 M positions) | +50 to +250 over the PST engine (≈ 1400–1800) |
| + null move, PVS, LMR (carefully A/B-tested) | +100 to +200 more |

**Reasoning behind the estimates.** (1) Sunfish, with a simple PST eval and a decent search, reports that its 4 kB NNUE variant measured "about +200 Elo over classic at tournament time controls" ([Sunfish README](https://github.com/thomasahle/sunfish)). That is a published, comparable data point for "small NN vs PST in a Python engine". (2) At the same nps, a better eval converts directly into Elo, but a slower eval costs depth (≈ 50–100 Elo per ply at these levels, **estimate**). That is why the NN gain ranges from small to substantial depending on inference speed. (3) The lowest Stockfish anchor is 1320, so a working PST engine with quiescence should land near it. That is a motivating first milestone ("beat Stockfish's weakest setting").

**What "done" looks like for the project (acceptance criteria for companion code):**
- Plays legal games under fastchess with no crashes or illegal moves over 100 games (`--compliance` passes).
- The NN engine beats the PST engine with a positive Elo estimate in a 100–200-game match.
- The learner produces an Elo estimate with a 95 % interval against at least one Stockfish anchor.

### d3. Runtime budget for the whole project (estimate)

| Task | Time on a CPU laptop |
|---|---|
| Stream + filter + encode 2 M positions | 15–40 min (network-bound) |
| Train 20 epochs | 20–60 min |
| `--smoke` versions of every milestone | < 1 min each |
| 100-game match at 60+0.6, 2 concurrent games | ≈ 1–1.5 h (each game ≈ 1.5–2 min) |
| 100-game match at 10+0.1 (quick check) | ≈ 15–20 min |

### d4. Pitfalls the lessons must warn about

1. **Sign bugs** (white-relative vs side-to-move-relative cp). The smoke test asserts that the mirrored position gives a negated score.
2. **Mate scores stored in the TT without ply adjustment** lead to wrong mate distances or blunders.
3. **Repetition blindness**: draws by repetition must use the game history, which `board.move_stack` handles in python-chess.
4. **Evaluating non-quiet positions with the NN**: the net was trained on quiet positions, so it can be wildly wrong mid-capture. Quiescence must come before the NN.
5. **Testing with too few games**: ±70 Elo at 100 games (b6). Use SPRT or more games.
6. **Time losses** in Python: always keep a safety margin (Stockfish's own `Move Overhead` option defaults to 10 ms, per the [command reference](https://official-stockfish.github.io/docs/stockfish-wiki/UCI-Protocol-and-Stockfish-Commands.html)). Start the learner engine with 50–100 ms because Python start-up and GC pauses are slower.
7. **Licensing**: python-chess, Stockfish and Lc0 are GPL-3. The course's own engine code (MIT) only *imports* python-chess. If the course's engine is ever distributed as a combined work, check GPL compatibility ([GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html)). The Lichess data is CC0, so it can be used and shared freely.

---

## (e) Bibliography

Grouped by topic. All links were checked on 2026-11-24 unless noted.

### Search and classic engine techniques (Chessprogramming Wiki)
1. Alpha-Beta: https://www.chessprogramming.org/Alpha-Beta
2. Minimax: https://www.chessprogramming.org/Minimax
3. Negamax: https://www.chessprogramming.org/Negamax
4. Quiescence Search: https://www.chessprogramming.org/Quiescence_Search
5. Horizon Effect: https://www.chessprogramming.org/Horizon_Effect
6. Iterative Deepening: https://www.chessprogramming.org/Iterative_Deepening
7. Transposition Table: https://www.chessprogramming.org/Transposition_Table
8. Zobrist Hashing: https://www.chessprogramming.org/Zobrist_Hashing
9. MVV-LVA: https://www.chessprogramming.org/MVV-LVA
10. Static Exchange Evaluation: https://www.chessprogramming.org/Static_Exchange_Evaluation
11. Killer Heuristic: https://www.chessprogramming.org/Killer_Heuristic
12. History Heuristic: https://www.chessprogramming.org/History_Heuristic
13. Null Move Pruning: https://www.chessprogramming.org/Null_Move_Pruning
14. Principal Variation Search: https://www.chessprogramming.org/Principal_Variation_Search
15. Late Move Reductions: https://www.chessprogramming.org/Late_Move_Reductions
16. Aspiration Windows: https://www.chessprogramming.org/Aspiration_Windows
17. Bitboards: https://www.chessprogramming.org/Bitboards
18. Board Representation: https://www.chessprogramming.org/Board_Representation
19. FEN: https://www.chessprogramming.org/Forsyth-Edwards_Notation
20. Perft: https://www.chessprogramming.org/Perft and Perft Results: https://www.chessprogramming.org/Perft_Results
21. Piece-Square Tables: https://www.chessprogramming.org/Piece-Square_Tables
22. Simplified Evaluation Function: https://www.chessprogramming.org/Simplified_Evaluation_Function
23. Tapered Eval: https://www.chessprogramming.org/Tapered_Eval
24. Texel's Tuning Method: https://www.chessprogramming.org/Texel%27s_Tuning_Method
25. UCI (CPW): https://www.chessprogramming.org/UCI
26. Knuth, D. E. & Moore, R. W. (1975). *An Analysis of Alpha-Beta Pruning.* Artificial Intelligence 6(4), 293–326. https://doi.org/10.1016/0004-3702%2875%2990019-3
27. Zobrist, A. L. (1970). *A New Hashing Method with Application for Game Playing.* Tech. Rep. 88, Univ. of Wisconsin, cited via CPW (above).

### NNUE and Stockfish
28. CPW: NNUE: https://www.chessprogramming.org/NNUE
29. Official NNUE doc (nnue-pytorch wiki): https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue.html
30. nnue-pytorch wiki home: https://official-stockfish.github.io/docs/nnue-pytorch-wiki/README.html
31. NNUE architecture history: https://official-stockfish.github.io/docs/nnue-pytorch-wiki/docs/nnue_architecture_history.html
32. nnue-pytorch trainer: https://github.com/official-stockfish/nnue-pytorch
33. Stockfish source, HalfKAv2_hm features: https://github.com/official-stockfish/Stockfish/blob/sf_19/src/nnue/features/half_ka_v2_hm.h (pinned to the Stockfish 19 tag; master replaced it with k32h3.h)
34. Stockfish repository and releases: https://github.com/official-stockfish/Stockfish and https://github.com/official-stockfish/Stockfish/releases
35. Stockfish 12 / NNUE announcement: https://stockfishchess.org/blog/2020/introducing-nnue-evaluation/
36. Stockfish 18 release notes (2026-01-31): https://stockfishchess.org/blog/2026/stockfish-18/
37. Stockfish 19 release notes (2026-09-05): https://stockfishchess.org/blog/2026/stockfish-19/
38. Stockfish FAQ: https://official-stockfish.github.io/docs/stockfish-wiki/Stockfish-FAQ.html
39. Stockfish UCI options and commands: https://official-stockfish.github.io/docs/stockfish-wiki/UCI-Protocol-and-Stockfish-Commands.html
40. Stockfish download: https://stockfishchess.org/download/
41. Nasu, Y. (2018). *Efficiently Updatable Neural-Network-based Evaluation Functions for Computer Shogi.* Ziosoft Computer Shogi Club. Unofficial English translation (D. Klein): https://github.com/asdfjkl/nnue
42. Wikipedia: Efficiently updatable neural network: https://en.wikipedia.org/wiki/Efficiently_updatable_neural_network
43. bullet NNUE trainer: https://github.com/jw1912/bullet

### AlphaZero and Leela
44. Silver, D. et al. (2017). *Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm.* https://arxiv.org/abs/1712.01815 (HTML: https://arxiv.org/html/1712.01815v1)
45. Silver, D. et al. (2018). *A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play.* Science 362(6419), 1140–1144. https://www.science.org/doi/10.1126/science.aar6404
46. Leela Chess Zero: https://lczero.org/
47. Lc0 technical explanation (last updated 2021, dated): https://lczero.org/dev/wiki/technical-explanation-of-leela-chess-zero/
48. Lc0 source: https://github.com/LeelaChessZero/lc0

### Libraries, protocol and data
49. python-chess documentation: https://python-chess.readthedocs.io/en/latest/
50. python-chess core API: https://python-chess.readthedocs.io/en/latest/core.html
51. python-chess polyglot (Zobrist): https://python-chess.readthedocs.io/en/latest/polyglot.html
52. python-chess engine (UCI client, WDL models): https://python-chess.readthedocs.io/en/latest/engine.html
53. PyPI `chess`: https://pypi.org/project/chess/
54. UCI protocol specification (April 2006): https://backscattering.de/chess/uci/
55. Lichess open database (games, evaluations, puzzles, CC0): https://database.lichess.org/
56. lichess-org/database (generator source): https://github.com/lichess-org/database
57. Lichess position evaluations on Hugging Face: https://huggingface.co/datasets/Lichess/chess-position-evaluations
58. python-zstandard: https://python-zstandard.readthedocs.io/
59. PyTorch `nn.EmbeddingBag`: https://docs.pytorch.org/docs/stable/generated/torch.nn.EmbeddingBag.html
60. PyTorch `optim.Adam`: https://docs.pytorch.org/docs/stable/generated/torch.optim.Adam.html

### Testing and rating
61. fastchess: https://github.com/Disservin/fastchess (manual: https://github.com/Disservin/fastchess/blob/master/man.md)
62. cutechess / cutechess-cli: https://github.com/cutechess/cutechess
63. Stockfish opening books: https://github.com/official-stockfish/books
64. CPW: Match Statistics (Elo, LOS): https://www.chessprogramming.org/Match_Statistics
65. CPW: SPRT: https://www.chessprogramming.org/Sequential_Probability_Ratio_Test
66. Fishtest (Stockfish's distributed testing): https://tests.stockfishchess.org/tests and wiki https://github.com/official-stockfish/fishtest/wiki
67. Wikipedia: Elo rating system: https://en.wikipedia.org/wiki/Elo_rating_system

### Reference engines worth reading
68. Sunfish (small Python engine, with NNUE variant): https://github.com/thomasahle/sunfish
69. GNU GPL v3 text (licences of python-chess / Stockfish / Lc0): https://www.gnu.org/licenses/gpl-3.0.en.html

---

## Appendix: notes for the content writers

- **Lesson order inside the chess track:** a1 → a2 → a3 → a4 → a5 → a6 → a7 → milestone match ("beat SF 1320?") → a9 + b2 + b3 → b4 → b5/b6 → (c) optional → a8 and a10 as advanced reading.
- **Prerequisites from other tracks:** recursion (beginner Python), the linear model → MLP → loss → Adam chain (beginner/intermediate ML), sigmoid and log-odds (math foundations; links to research/01-foundations.md).
- **Analogy bank:** hiker and gut feeling (search vs eval), flight shopping (alpha-beta), detective's line-up (ordering), the photographer who waits for the sneeze to pass (quiescence), the exam answered roughly then refined (ID), fingerprint dabbing (Zobrist), the notebook of solved positions (TT), "move twice and still can't hurt me" (null move), the appraiser vs actual sale prices (eval vs result blending), keeping a running bank balance instead of re-adding every receipt (accumulator), the coin-flip test that stops early (SPRT).
- **Do not claim** specific current Stockfish layer sizes without citing a version and the history page. **Do not claim** Elo numbers for the learner engine as facts. Present them as the estimates above and show how to measure them.
