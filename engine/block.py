# engine/block.py
from typing import List, Tuple


class Block:
    """Shape represented by list of (row_offset, col_offset)."""

    def __init__(self, cells: List[Tuple[int, int]]) -> None:
        self.cells = cells

    @property
    def width(self) -> int:
        return max(c for _, c in self.cells) + 1

    @property
    def height(self) -> int:
        return max(r for r, _ in self.cells) + 1
