# engine/board.py
from typing import Set, Tuple, List

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

    def find_full_lines(self) -> Set[Tuple[int, int]]:
        """Find all cells that are part of full rows or columns.
        
        Returns:
            Set of (row, col) tuples that are part of full lines.
        """
        cells_to_clear = set()
        
        # Find full rows
        for r in range(self.rows):
            if all(self.grid[r][c] for c in range(self.cols)):
                for c in range(self.cols):
                    cells_to_clear.add((r, c))
        
        # Find full cols
        for c in range(self.cols):
            if all(self.grid[r][c] for r in range(self.rows)):
                for r in range(self.rows):
                    cells_to_clear.add((r, c))
                    
        return cells_to_clear
    
    def clear_cells(self, cells: Set[Tuple[int, int]]) -> None:
        """Clear specific cells from the grid.
        
        Args:
            cells: Set of (row, col) tuples to clear
        """
        for r, c in cells:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = 0

    def clear_full_lines(self) -> int:
        """Clear any full rows/cols; return number of lines removed."""
        cells_to_clear = self.find_full_lines()
        
        # Count lines (rows + columns)
        cleared_rows = set()
        cleared_cols = set()
        
        for r, c in cells_to_clear:
            cleared_rows.add(r)
            cleared_cols.add(c)
        
        # Clear cells
        self.clear_cells(cells_to_clear)
        
        # Return total number of lines cleared
        return len(cleared_rows) + len(cleared_cols)
