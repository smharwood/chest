"""
Core chess rules
"""
import pyxel

# Constants
BOARD_SIZE = 8
CELL_SIZE = 32
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE  # 256

# Colors (pyxel palette indices)
COL_LIGHT_SQ = 15  # peach
COL_DARK_SQ = 4  # brown
COL_SELECT = 10  # yellow
COL_VALID = 11  # lime
COL_CHECK = 8  # red
COL_WHITE_PIECE = 7  # white
COL_WHITE_OUTLINE = 13  # gray
COL_BLACK_PIECE = 0  # black
COL_BLACK_OUTLINE = 5  # dark blue
COL_BG = 0
COL_TEXT = 7

# Piece types
KING = "K"
QUEEN = "Q"
ROOK = "R"
BISHOP = "B"
KNIGHT = "N"
PAWN = "P"

WHITE = "white"
BLACK = "black"


class ChessGame:
    """A two-player chess game"""
    def __init__(self):
        pyxel.init(SCREEN_SIZE, SCREEN_SIZE, title="Chess", display_scale=3, fps=30)
        pyxel.mouse(True)

        self.board = [[None] * 8 for _ in range(8)]
        self.turn = WHITE
        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.game_result = ""
        self.in_check = False
        self.en_passant_target = None  # (row, col) square that can be captured en passant
        self.king_moved = {WHITE: False, BLACK: False}
        self.rook_moved = {WHITE: [False, False], BLACK: [False, False]}  # [queenside, kingside]
        self.last_move = None  # ((from_r, from_c), (to_r, to_c))

        self._setup_board()
        pyxel.run(self.update, self.draw)

    def _setup_board(self):
        # Black pieces (top, rows 0-1)
        back_row = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for c in range(8):
            self.board[0][c] = (back_row[c], BLACK)
            self.board[1][c] = (PAWN, BLACK)
        # White pieces (bottom, rows 6-7)
        for c in range(8):
            self.board[7][c] = (back_row[c], WHITE)
            self.board[6][c] = (PAWN, WHITE)

    # ── Drawing ──────────────────────────────────────────────

    def draw(self):
        pyxel.cls(COL_BG)
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        self._draw_status()
        if self.game_over:
            self._draw_game_over()

    def _draw_board(self):
        for r in range(8):
            for c in range(8):
                x, y = c * CELL_SIZE, r * CELL_SIZE
                col = COL_LIGHT_SQ if (r + c) % 2 == 0 else COL_DARK_SQ
                pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, col)

    def _draw_highlights(self):
        # Highlight king in check
        if self.in_check:
            kr, kc = self._find_king(self.turn)
            x, y = kc * CELL_SIZE, kr * CELL_SIZE
            pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, COL_CHECK)

        # Highlight selected square
        if self.selected:
            r, c = self.selected
            x, y = c * CELL_SIZE, r * CELL_SIZE
            pyxel.rect(x, y, CELL_SIZE, CELL_SIZE, COL_SELECT)

        # Highlight valid moves
        for r, c in self.valid_moves:
            x, y = c * CELL_SIZE, r * CELL_SIZE
            cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
            if self.board[r][c] is not None:
                # Capture: draw corner triangles
                pyxel.rectb(x, y, CELL_SIZE, CELL_SIZE, COL_VALID)
                pyxel.rectb(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2, COL_VALID)
            else:
                # Empty: draw dot
                pyxel.circ(cx, cy, 4, COL_VALID)

    def _draw_pieces(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece:
                    self._draw_piece(r, c, piece[0], piece[1])

    def _draw_piece(self, row, col, piece_type, color):
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        fill = COL_WHITE_PIECE if color == WHITE else COL_BLACK_PIECE
        outline = COL_WHITE_OUTLINE if color == WHITE else COL_BLACK_OUTLINE

        if piece_type == PAWN:
            self._draw_pawn(x, y, fill, outline)
        elif piece_type == ROOK:
            self._draw_rook(x, y, fill, outline)
        elif piece_type == KNIGHT:
            self._draw_knight(x, y, fill, outline)
        elif piece_type == BISHOP:
            self._draw_bishop(x, y, fill, outline)
        elif piece_type == QUEEN:
            self._draw_queen(x, y, fill, outline)
        elif piece_type == KING:
            self._draw_king(x, y, fill, outline)

    def _draw_pawn(self, cx, cy, fill, outline):
        # Base
        pyxel.rect(cx - 6, cy + 6, 13, 4, outline)
        pyxel.rect(cx - 5, cy + 7, 11, 2, fill)
        # Stem
        pyxel.rect(cx - 3, cy + 1, 7, 6, outline)
        pyxel.rect(cx - 2, cy + 2, 5, 4, fill)
        # Head
        pyxel.circ(cx, cy - 4, 5, outline)
        pyxel.circ(cx, cy - 4, 4, fill)

    def _draw_rook(self, cx, cy, fill, outline):
        # Base
        pyxel.rect(cx - 8, cy + 6, 17, 5, outline)
        pyxel.rect(cx - 7, cy + 7, 15, 3, fill)
        # Body
        pyxel.rect(cx - 6, cy - 3, 13, 10, outline)
        pyxel.rect(cx - 5, cy - 2, 11, 8, fill)
        # Battlements
        for dx in [-6, -1, 4]:
            pyxel.rect(cx + dx, cy - 9, 5, 7, outline)
            pyxel.rect(cx + dx + 1, cy - 8, 3, 5, fill)

    def _draw_knight(self, cx, cy, fill, outline):
        # Base
        pyxel.rect(cx - 7, cy + 6, 15, 5, outline)
        pyxel.rect(cx - 6, cy + 7, 13, 3, fill)
        # Body
        pyxel.rect(cx - 5, cy - 2, 11, 9, outline)
        pyxel.rect(cx - 4, cy - 1, 9, 7, fill)
        # Head/neck
        pyxel.rect(cx - 5, cy - 9, 8, 8, outline)
        pyxel.rect(cx - 4, cy - 8, 6, 6, fill)
        # Nose
        pyxel.rect(cx - 8, cy - 7, 5, 5, outline)
        pyxel.rect(cx - 7, cy - 6, 3, 3, fill)
        # Eye
        pyxel.pset(cx - 2, cy - 6, outline)

    def _draw_bishop(self, cx, cy, fill, outline):
        # Base
        pyxel.rect(cx - 7, cy + 6, 15, 5, outline)
        pyxel.rect(cx - 6, cy + 7, 13, 3, fill)
        # Body
        pyxel.tri(cx - 7, cy + 6, cx + 7, cy + 6, cx, cy - 5, outline)
        pyxel.tri(cx - 5, cy + 5, cx + 5, cy + 5, cx, cy - 3, fill)
        # Top ball
        pyxel.circ(cx, cy - 8, 3, outline)
        pyxel.circ(cx, cy - 8, 2, fill)
        # Slit
        pyxel.line(cx, cy - 1, cx, cy + 3, outline)

    def _draw_queen(self, cx, cy, fill, outline):
        # Base
        pyxel.rect(cx - 8, cy + 6, 17, 5, outline)
        pyxel.rect(cx - 7, cy + 7, 15, 3, fill)
        # Body
        pyxel.rect(cx - 6, cy - 1, 13, 8, outline)
        pyxel.rect(cx - 5, cy, 11, 6, fill)
        # Crown points
        for dx in [-7, -3, 1, 5]:
            pyxel.tri(cx + dx, cy - 1, cx + dx + 3, cy - 1, cx + dx + 1, cy - 8, outline)
            pyxel.tri(cx + dx + 1, cy - 2, cx + dx + 2, cy - 2, cx + dx + 1, cy - 6, fill)
        # Crown balls
        for dx in [-6, -2, 2, 6]:
            pyxel.circ(cx + dx, cy - 9, 2, outline)
            pyxel.circ(cx + dx, cy - 9, 1, fill)

    def _draw_king(self, cx, cy, fill, outline):
        # Base
        pyxel.rect(cx - 8, cy + 6, 17, 5, outline)
        pyxel.rect(cx - 7, cy + 7, 15, 3, fill)
        # Body
        pyxel.rect(cx - 6, cy - 1, 13, 8, outline)
        pyxel.rect(cx - 5, cy, 11, 6, fill)
        # Crown points
        pyxel.tri(cx - 7, cy - 1, cx - 3, cy - 1, cx - 5, cy - 6, outline)
        pyxel.tri(cx + 3, cy - 1, cx + 7, cy - 1, cx + 5, cy - 6, outline)
        pyxel.tri(cx - 6, cy - 2, cx - 4, cy - 2, cx - 5, cy - 5, fill)
        pyxel.tri(cx + 4, cy - 2, cx + 6, cy - 2, cx + 5, cy - 5, fill)
        # Cross on top
        pyxel.rect(cx - 1, cy - 12, 3, 9, outline)
        pyxel.rect(cx - 4, cy - 9, 9, 3, outline)
        pyxel.rect(cx, cy - 11, 1, 7, fill)
        pyxel.rect(cx - 3, cy - 8, 7, 1, fill)

    def _draw_status(self):
        if self.game_over:
            return
        msg = f"{'White' if self.turn == WHITE else 'Black'}'s turn"
        if self.in_check:
            msg += " - CHECK!"
        # Draw text with background
        tw = len(msg) * 4
        tx = (SCREEN_SIZE - tw) // 2
        pyxel.rect(tx - 2, 0, tw + 4, 9, COL_BG)
        pyxel.text(tx, 2, msg, COL_TEXT)

    def _draw_game_over(self):
        # Semi-transparent overlay
        for y in range(0, SCREEN_SIZE, 2):
            for x in range(0, SCREEN_SIZE, 2):
                pyxel.pset(x, y, COL_BG)
        # Result text
        tw = len(self.game_result) * 4
        tx = (SCREEN_SIZE - tw) // 2
        pyxel.rect(tx - 4, SCREEN_SIZE // 2 - 8, tw + 8, 18, COL_BG)
        pyxel.rectb(tx - 4, SCREEN_SIZE // 2 - 8, tw + 8, 18, COL_TEXT)
        pyxel.text(tx, SCREEN_SIZE // 2 - 3, self.game_result, COL_TEXT)
        # Restart hint
        hint = "Press R to restart"
        hw = len(hint) * 4
        hx = (SCREEN_SIZE - hw) // 2
        pyxel.text(hx, SCREEN_SIZE // 2 + 12, hint, COL_TEXT)

    # ── Input / Update ───────────────────────────────────────

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self._restart()
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            col = pyxel.mouse_x // CELL_SIZE
            row = pyxel.mouse_y // CELL_SIZE
            if 0 <= row < 8 and 0 <= col < 8:
                self._handle_click(row, col)

    def _handle_click(self, row, col):
        # If a valid move square is clicked, execute the move
        if self.selected and (row, col) in self.valid_moves:
            self._make_move(self.selected, (row, col))
            self.selected = None
            self.valid_moves = []
            return

        # Try to select a piece
        piece = self.board[row][col]
        if piece and piece[1] == self.turn:
            self.selected = (row, col)
            self.valid_moves = self._get_legal_moves(row, col)
        else:
            self.selected = None
            self.valid_moves = []

    def _restart(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.turn = WHITE
        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.game_result = ""
        self.in_check = False
        self.en_passant_target = None
        self.king_moved = {WHITE: False, BLACK: False}
        self.rook_moved = {WHITE: [False, False], BLACK: [False, False]}
        self.last_move = None
        self._setup_board()

    # ── Move Execution ───────────────────────────────────────

    def _make_move(self, from_sq, to_sq):
        fr, fc = from_sq
        tr, tc = to_sq
        piece = self.board[fr][fc]
        piece_type, color = piece

        # Track rook/king movement for castling
        if piece_type == KING:
            self.king_moved[color] = True
            # Castling: move the rook too
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
            if tr == (0 if cap_color == BLACK else 7):
                if tc == 0:
                    self.rook_moved[cap_color][0] = True
                elif tc == 7:
                    self.rook_moved[cap_color][1] = True

        # En passant capture
        if piece_type == PAWN and (tr, tc) == self.en_passant_target:
            self.board[fr][tc] = None  # Remove captured pawn

        # Update en passant target
        if piece_type == PAWN and abs(tr - fr) == 2:
            self.en_passant_target = ((fr + tr) // 2, fc)
        else:
            self.en_passant_target = None

        # Move the piece
        self.board[tr][tc] = piece
        self.board[fr][fc] = None

        # Pawn promotion
        if piece_type == PAWN:
            if (color == WHITE and tr == 0) or (color == BLACK and tr == 7):
                self.board[tr][tc] = (QUEEN, color)

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

    # ── Move Generation ──────────────────────────────────────

    def _get_pseudo_moves(self, row, col):
        """Get all moves without checking if they leave king in check."""
        piece = self.board[row][col]
        if not piece:
            return []
        piece_type, color = piece
        moves = []

        if piece_type == PAWN:
            moves = self._pawn_moves(row, col, color)
        elif piece_type == KNIGHT:
            moves = self._knight_moves(row, col, color)
        elif piece_type == BISHOP:
            moves = self._sliding_moves(row, col, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)])
        elif piece_type == ROOK:
            moves = self._sliding_moves(row, col, color, [(-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece_type == QUEEN:
            moves = self._sliding_moves(row, col, color, [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)])
        elif piece_type == KING:
            moves = self._king_moves(row, col, color)

        return moves

    def _get_legal_moves(self, row, col):
        """Get moves that don't leave own king in check."""
        piece = self.board[row][col]
        if not piece:
            return []
        color = piece[1]
        pseudo = self._get_pseudo_moves(row, col)
        legal = []
        for mr, mc in pseudo:
            if self._is_move_safe(row, col, mr, mc, color):
                legal.append((mr, mc))
        return legal

    def _is_move_safe(self, fr, fc, tr, tc, color):
        """Test if making a move leaves own king safe."""
        # Save state
        src = self.board[fr][fc]
        dst = self.board[tr][tc]
        ep_captured = None

        # Handle en passant capture for simulation
        if src[0] == PAWN and (tr, tc) == self.en_passant_target:
            ep_captured = self.board[fr][tc]
            self.board[fr][tc] = None

        # Make temporary move
        self.board[tr][tc] = src
        self.board[fr][fc] = None

        safe = not self._is_in_check(color)

        # Restore
        self.board[fr][fc] = src
        self.board[tr][tc] = dst
        if ep_captured is not None:
            self.board[fr][tc] = ep_captured

        return safe

    def _pawn_moves(self, row, col, color):
        moves = []
        direction = -1 if color == WHITE else 1
        start_row = 6 if color == WHITE else 1

        # Forward one
        nr = row + direction
        if 0 <= nr < 8 and self.board[nr][col] is None:
            moves.append((nr, col))
            # Forward two from start
            nr2 = row + 2 * direction
            if row == start_row and self.board[nr2][col] is None:
                moves.append((nr2, col))

        # Captures
        for dc in [-1, 1]:
            nc = col + dc
            nr = row + direction
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                if target and target[1] != color:
                    moves.append((nr, nc))
                # En passant
                if (nr, nc) == self.en_passant_target:
                    moves.append((nr, nc))

        return moves

    def _knight_moves(self, row, col, color):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                if target is None or target[1] != color:
                    moves.append((nr, nc))
        return moves

    def _sliding_moves(self, row, col, color, directions):
        moves = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = self.board[nr][nc]
                if target is None:
                    moves.append((nr, nc))
                elif target[1] != color:
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc
        return moves

    def _king_moves(self, row, col, color):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target is None or target[1] != color:
                        moves.append((nr, nc))

        # Castling
        if not self.king_moved[color] and not self._is_in_check(color):
            base_row = 7 if color == WHITE else 0
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

    # ── Check Detection ──────────────────────────────────────

    def _find_king(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p[0] == KING and p[1] == color:
                    return (r, c)
        return (0, 0)  # Should never happen

    def _is_in_check(self, color):
        kr, kc = self._find_king(color)
        return self._is_square_attacked(kr, kc, color)

    def _is_square_attacked(self, row, col, color):
        """Check if a square is attacked by any piece of the opponent."""
        opp = BLACK if color == WHITE else WHITE

        # Knight attacks
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                p = self.board[nr][nc]
                if p and p[0] == KNIGHT and p[1] == opp:
                    return True

        # Pawn attacks
        pawn_dir = 1 if opp == WHITE else -1  # Look toward where opp pawns sit
        for dc in [-1, 1]:
            pr, pc = row + pawn_dir, col + dc
            if 0 <= pr < 8 and 0 <= pc < 8:
                p = self.board[pr][pc]
                if p and p[0] == PAWN and p[1] == opp:
                    return True

        # King attacks
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    p = self.board[nr][nc]
                    if p and p[0] == KING and p[1] == opp:
                        return True

        # Sliding attacks (rook/queen on straights, bishop/queen on diagonals)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                p = self.board[nr][nc]
                if p:
                    if p[1] == opp and p[0] in (ROOK, QUEEN):
                        return True
                    break
                nr += dr
                nc += dc

        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                p = self.board[nr][nc]
                if p:
                    if p[1] == opp and p[0] in (BISHOP, QUEEN):
                        return True
                    break
                nr += dr
                nc += dc

        return False

    def _has_any_legal_move(self, color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p[1] == color:
                    if self._get_legal_moves(r, c):
                        return True
        return False
