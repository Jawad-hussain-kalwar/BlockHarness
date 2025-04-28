
# engine/board.py
class Board:
    """8×8 grid that supports placement and line clears."""

    def __init__(self, rows: int = 8, cols: int = 8) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = [[0] * cols for _ in range(rows)]

    # ────────────────────────── placement helpers ──────────────────────────

    def can_place(self, block, top: int, left: int) -> bool:
        """True if every cell fits inside the board and is currently empty."""
        for r_off, c_off in block.cells:
            r, c = top + r_off, left + c_off
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return False
            if self.grid[r][c]:
                return False
        return True

    def place_block(self, block, top: int, left: int) -> None:
        """Write block cells into the grid (assumes can_place is True)."""
        for r_off, c_off in block.cells:
            self.grid[top + r_off][left + c_off] = 1

    # ───────────────────────────── line clears ─────────────────────────────

    def clear_full_lines(self) -> int:
        """Clear any full rows/cols; return number of lines removed."""
        cleared = 0

        # full rows
        for r in range(self.rows):
            if all(self.grid[r][c] for c in range(self.cols)):
                for c in range(self.cols):
                    self.grid[r][c] = 0
                cleared += 1

        # full cols
        for c in range(self.cols):
            if all(self.grid[r][c] for r in range(self.rows)):
                for r in range(self.rows):
                    self.grid[r][c] = 0
                cleared += 1

        return cleared
