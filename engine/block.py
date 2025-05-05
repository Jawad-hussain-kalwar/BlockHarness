# engine/block.py
from typing import List, Tuple


class Block:
    """A collection of cells representing a tetromino-like block."""

    def __init__(self, cells: List[Tuple[int, int]]) -> None:
        self.cells = cells
        self.height = max([r for r, _ in cells]) + 1 if cells else 0
        self.width = max([c for _, c in cells]) + 1 if cells else 0
