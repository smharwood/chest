"""
Alternate rules...
as in, there are none
"""
from chess_core import ChessGame

class ChessGameAlt(ChessGame):
    """A two-player chess game, but with alternate rules that a four-year-old finds funny"""

    def _get_pseudo_moves(self, row, col):
        """Any piece can move to any empty square or capture any opponent piece."""
        piece = self.board[row][col]
        if not piece:
            return []
        _, color = piece
        moves = []
        for r in range(8):
            for c in range(8):
                if r == row and c == col:
                    continue
                target = self.board[r][c]
                if target is None or target[1] != color:
                    moves.append((r, c))
        return moves
