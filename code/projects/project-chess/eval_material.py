"""Material + piece-square-table evaluation: the classic baseline.

    python eval_material.py            # prints a few checkpoint evaluations

This is Tomasz Michniewski's "Simplified Evaluation Function" from the
Chessprogramming Wiki: piece values in centipawns (100 = one pawn) plus one
piece-square table (PST) per piece type, with a separate king table for the
endgame.  https://www.chessprogramming.org/Simplified_Evaluation_Function

evaluate(board) is the single swap point of the engine: search.py calls it at
the leaves, and the neural evaluator in eval_nn.py has exactly the same
signature, so swapping one for the other changes nothing else.

Scores are always from the point of view of the SIDE TO MOVE (negamax needs
this): +50 means "the player whose turn it is is half a pawn better".
"""
import chess

# Piece values in centipawns (Simplified Evaluation Function).
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,  # both sides always have one; mate is handled by search, not eval
}

# Piece-square tables from White's point of view, written the way you look at
# a diagram: the first row is rank 8, the last row is rank 1 (a-file on the left).
# fmt: off
PAWN_PST = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_PST = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_PST = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_PST = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
QUEEN_PST = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_MIDDLE_PST = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20,
]
KING_END_PST = [
   -50,-40,-30,-20,-20,-30,-40,-50,
   -30,-20,-10,  0,  0,-10,-20,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 30, 40, 40, 30,-10,-30,
   -30,-10, 20, 30, 30, 20,-10,-30,
   -30,-30,  0,  0,  0,  0,-30,-30,
   -50,-30,-30,-30,-30,-30,-30,-50,
]
# fmt: on

PST = {
    chess.PAWN: PAWN_PST,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST,
    chess.QUEEN: QUEEN_PST,
}


def pst_index(square: int, color: bool) -> int:
    """Map a python-chess square (a1 = 0 ... h8 = 63) to an index in the tables above.

    The tables list rank 8 first, so a WHITE piece needs its rank flipped (square ^ 56).
    A BLACK piece sees the board upside down, so its own square is already the right
    index: Black's pawns get the "rank 7 = 50" bonus when they reach rank 2.
    """
    return square ^ 56 if color == chess.WHITE else square


def is_endgame(board: chess.Board) -> bool:
    """Michniewski's rule: no queens, or every side with a queen has at most one minor piece."""
    for color in (chess.WHITE, chess.BLACK):
        if board.pieces_mask(chess.QUEEN, color):
            minors = chess.popcount(board.pieces_mask(chess.KNIGHT, color) | board.pieces_mask(chess.BISHOP, color))
            rooks = board.pieces_mask(chess.ROOK, color)
            if rooks or minors > 1:
                return False
    return True


def material_white(board: chess.Board) -> int:
    """Material only, from White's point of view (no tables)."""
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += value * (
            chess.popcount(board.pieces_mask(piece_type, chess.WHITE))
            - chess.popcount(board.pieces_mask(piece_type, chess.BLACK))
        )
    return score


def evaluate_white(board: chess.Board) -> int:
    """Material + piece-square tables, from White's point of view."""
    king_table = KING_END_PST if is_endgame(board) else KING_MIDDLE_PST
    score = 0
    for color, sign in ((chess.WHITE, 1), (chess.BLACK, -1)):
        for piece_type in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING):
            table = king_table if piece_type == chess.KING else PST[piece_type]
            value = PIECE_VALUES[piece_type]
            for sq in chess.scan_forward(board.pieces_mask(piece_type, color)):
                score += sign * (value + table[pst_index(sq, color)])
    return score


def evaluate(board: chess.Board, key=None) -> int:
    """Side-to-move score in centipawns. `key` (a position hash) is ignored here;
    the neural evaluator uses it for its cache, so both share one signature."""
    s = evaluate_white(board)
    return s if board.turn == chess.WHITE else -s


class MaterialEvaluator:
    """Object wrapper so search.py can treat both evaluators the same way."""

    name = "material+pst"

    def evaluate(self, board: chess.Board, key=None) -> int:
        return evaluate(board)


if __name__ == "__main__":
    start = chess.Board()
    print(f"start position (White to move):       {evaluate(start):+d} cp   (expected +0)")
    no_knight = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R1BQKBNR w KQkq - 0 1")
    print(f"White without the b1 knight, material: {material_white(no_knight):+d} cp (expected -320)")
    print(f"same position, material + PST:         {evaluate(no_knight):+d} cp (expected -280: the b1 knight's table value was -40)")
    after_e4 = chess.Board()
    after_e4.push_san("e4")
    print(f"after 1.e4, Black to move:             {evaluate(after_e4):+d} cp  (expected -40: White's pawn gained 40, seen from Black)")
    mirrored = after_e4.mirror()
    print(f"colour-mirrored copy, White to move:   {evaluate(mirrored):+d} cp  (must equal the line above)")
    assert evaluate(start) == 0
    assert material_white(no_knight) == -320
    assert evaluate(mirrored) == evaluate(after_e4)
    print("all checks passed")
