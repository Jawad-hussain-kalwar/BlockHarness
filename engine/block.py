# engine/block.py
from typing import List, Tuple


class Block:
    """A collection of cells representing a tetromino-like block."""

    def __init__(self, cells: List[Tuple[int, int]]) -> None:
        self.cells = cells
        self.height = max([r for r, _ in cells]) + 1 if cells else 0
        self.width = max([c for _, c in cells]) + 1 if cells else 0

    def rotate_clockwise(self, rotations: int = 1) -> 'Block':
        """Rotate the block clockwise by the specified number of rotations (0-3).
        
        Args:
            rotations: Number of 90-degree clockwise rotations to apply (0-3)
            
        Returns:
            A new Block instance with the rotated cells
        """
        rotations = rotations % 4  # Normalize to 0-3
        
        if rotations == 0:
            return Block(self.cells)
            
        # Apply rotation to create a new block
        rotated_cells = []
        for r, c in self.cells:
            if rotations == 1:  # 90 degrees clockwise
                rotated_cells.append((c, -r + self.height - 1))
            elif rotations == 2:  # 180 degrees
                rotated_cells.append((-r + self.height - 1, -c + self.width - 1))
            elif rotations == 3:  # 270 degrees clockwise
                rotated_cells.append((-c + self.width - 1, r))
                
        return Block(rotated_cells)
