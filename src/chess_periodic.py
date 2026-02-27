"""
Chess with periodic boundary conditions (torus topology).
Pieces can wrap around all edges of the board.
"""
from chess_core import ChessGame, WHITE, BLACK, KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN, BOARD_SIZE

def _wrap(n):
    return n % BOARD_SIZE


class ChessGamePeriodic(ChessGame):
    """Chess on a torus — all board edges wrap around."""
    def __init__(self):
        super().__init__(title="Toroidal Chess")

    def _setup_board(self):
        # Pieces advanced by two squares toward the center
        # Black pieces: back row 0→2, pawns 1→3
        back_row = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for c in range(8):
            self.board[2][c] = (back_row[c], BLACK)
            self.board[3][c] = (PAWN, BLACK)
        # White pieces: back row 7→5, pawns 6→4
        for c in range(8):
            self.board[5][c] = (back_row[c], WHITE)
            self.board[4][c] = (PAWN, WHITE)

    # ── Move Generation (with wrapping) ───────────────────────

    def _pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == WHITE else 1
        start_row = 4 if color == WHITE else 3

        # Forward one
        nr = _wrap(row + direction)
        if self.board[nr][col] is None:
            moves.append((nr, col))
            # Forward two from start
            if row == start_row:
                nr2 = _wrap(row + 2 * direction)
                if self.board[nr2][col] is None:
                    moves.append((nr2, col))

        # Captures
        nr = _wrap(row + direction)
        for dc in [-1, 1]:
            nc = _wrap(col + dc)
            target = self.board[nr][nc]
            if target and target[1] != color:
                moves.append((nr, nc))
            if (nr, nc) == self.en_passant_target:
                moves.append((nr, nc))

        return moves

    def _knight_moves(self, row, col, color):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            nr, nc = _wrap(row + dr), _wrap(col + dc)
            target = self.board[nr][nc]
            if target is None or target[1] != color:
                moves.append((nr, nc))
        return moves

    def _sliding_moves(self, row, col, color, directions):
        moves = []
        for dr, dc in directions:
            nr, nc = row, col
            for _ in range(7):  # max 7 steps before returning to origin
                nr, nc = _wrap(nr + dr), _wrap(nc + dc)
                if nr == row and nc == col:
                    break  # wrapped back to start
                target = self.board[nr][nc]
                if target is None:
                    moves.append((nr, nc))
                elif target[1] != color:
                    moves.append((nr, nc))
                    break
                else:
                    break
        return moves

    def _king_moves(self, row, col, color):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = _wrap(row + dr), _wrap(col + dc)
                target = self.board[nr][nc]
                if target is None or target[1] != color:
                    moves.append((nr, nc))

        # Castling (no wrapping — uses absolute positions)
        if not self.king_moved[color] and not self._is_in_check(color):
            base_row = 5 if color == WHITE else 2
            if row == base_row and col == 4:
                # Kingside
                if (not self.rook_moved[color][1]
                        and self.board[base_row][5] is None
                        and self.board[base_row][6] is None
                        and self.board[base_row][7] == (ROOK, color)
                        and not self._is_square_attacked(base_row, 5, color)
                        and not self._is_square_attacked(base_row, 6, color)):
                    moves.append((base_row, 6))
                # Queenside
                if (not self.rook_moved[color][0]
                        and self.board[base_row][3] is None
                        and self.board[base_row][2] is None
                        and self.board[base_row][1] is None
                        and self.board[base_row][0] == (ROOK, color)
                        and not self._is_square_attacked(base_row, 3, color)
                        and not self._is_square_attacked(base_row, 2, color)):
                    moves.append((base_row, 2))

        return moves

    # ── Check Detection (with wrapping) ───────────────────────

    def _is_square_attacked(self, row, col, color):
        """Check if a square is attacked by any opponent piece, with wrapping."""
        opp = BLACK if color == WHITE else WHITE

        # Knight attacks
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = _wrap(row + dr), _wrap(col + dc)
            p = self.board[nr][nc]
            if p and p[0] == KNIGHT and p[1] == opp:
                return True

        # Pawn attacks
        pawn_dir = 1 if opp == WHITE else -1  # Look toward where opp pawns sit
        # pawn_dir = -1 if opp == WHITE else 1
        pr = _wrap(row + pawn_dir)
        for dc in [-1, 1]:
            pc = _wrap(col + dc)
            p = self.board[pr][pc]
            if p and p[0] == PAWN and p[1] == opp:
                return True

        # King attacks
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = _wrap(row + dr), _wrap(col + dc)
                p = self.board[nr][nc]
                if p and p[0] == KING and p[1] == opp:
                    return True

        # Sliding attacks — straights (rook/queen)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row, col
            for _ in range(7):
                nr, nc = _wrap(nr + dr), _wrap(nc + dc)
                if nr == row and nc == col:
                    break
                p = self.board[nr][nc]
                if p:
                    if p[1] == opp and p[0] in (ROOK, QUEEN):
                        return True
                    break

        # Sliding attacks — diagonals (bishop/queen)
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row, col
            for _ in range(7):
                nr, nc = _wrap(nr + dr), _wrap(nc + dc)
                if nr == row and nc == col:
                    break
                p = self.board[nr][nc]
                if p:
                    if p[1] == opp and p[0] in (BISHOP, QUEEN):
                        return True
                    break

        return False

    # ── Move Execution (with wrapping adjustments) ────────────

    def _make_move(self, from_sq, to_sq):
        fr, fc = from_sq
        tr, tc = to_sq
        piece = self.board[fr][fc]
        piece_type, color = piece

        # Track rook/king movement for castling
        if piece_type == KING:
            self.king_moved[color] = True
            # Castling: move the rook too (non-wrapping, absolute positions)
            if abs(tc - fc) == 2:
                if tc > fc:  # Kingside
                    self.board[fr][7] = None
                    self.board[fr][5] = (ROOK, color)
                    self.rook_moved[color][1] = True
                else:  # Queenside
                    self.board[fr][0] = None
                    self.board[fr][3] = (ROOK, color)
                    self.rook_moved[color][0] = True

        if piece_type == ROOK:
            if fc == 0:
                self.rook_moved[color][0] = True
            elif fc == 7:
                self.rook_moved[color][1] = True

        # If a rook is captured in its starting position, mark it as moved
        captured = self.board[tr][tc]
        if captured and captured[0] == ROOK:
            cap_color = captured[1]
            if tr == (2 if cap_color == BLACK else 5):
                if tc == 0:
                    self.rook_moved[cap_color][0] = True
                elif tc == 7:
                    self.rook_moved[cap_color][1] = True

        # En passant capture — the captured pawn is on the same row as the
        # moving pawn, at the target column
        if piece_type == PAWN and (tr, tc) == self.en_passant_target:
            self.board[fr][tc] = None

        # Update en passant target
        # With wrapping, a two-square pawn advance is detected by row distance
        row_diff = (tr - fr) % BOARD_SIZE
        if piece_type == PAWN and row_diff in (2, BOARD_SIZE - 2):
            direction = -1 if color == WHITE else 1
            self.en_passant_target = (_wrap(fr + direction), fc)
        else:
            self.en_passant_target = None

        # Move the piece
        self.board[tr][tc] = piece
        self.board[fr][fc] = None

        # No pawn promotion in periodic mode

        self.last_move = (from_sq, to_sq)

        # Switch turn
        self.turn = BLACK if self.turn == WHITE else WHITE

        # Check game state
        self.in_check = self._is_in_check(self.turn)
        if not self._has_any_legal_move(self.turn):
            self.game_over = True
            if self.in_check:
                winner = "White" if self.turn == BLACK else "Black"
                self.game_result = f"Checkmate! {winner} wins!"
            else:
                self.game_result = "Stalemate! It's a draw."
