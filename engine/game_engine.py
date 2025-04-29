# engine/game_engine.py
from typing import Dict, List, Tuple, Optional, Set

from engine.board import Board
from engine.block_pool import BlockPool
from engine.block import Block


class GameEngine:
    """Core game loop & scoring logic."""

    def __init__(self, config: Dict):
        self.config = config
        self.board = Board()
        self.score = 0
        self.lines = 0
        self.blocks_placed = 0
        self._game_over = False

        self.pool = BlockPool(
            self.config["shapes"],
            self.config["shape_weights"]
        )
        self._current_block = None
        
        # Preview management
        self._preview_blocks = []  # List of (block, rotation)
        self._selected_preview_index = None
        self._refill_preview()

    @staticmethod
    def compute_line_score(lines: int) -> int:
        """Calculate score based on number of lines cleared.
        
        Args:
            lines: Number of lines cleared
            
        Returns:
            int: Score awarded for clearing those lines
        """
        return 100 * lines + 50 * max(0, lines - 1)  # Base score + combo bonus

    # ───────────────────────── Public API ──────────────────────────

    def get_board_state(self) -> List[List[int]]:
        """Get the current board grid state (read-only)."""
        return [row[:] for row in self.board.grid]
    
    def get_preview_blocks(self) -> List[Tuple[Block, int]]:
        """Get the current preview blocks with their rotations (read-only)."""
        return self._preview_blocks.copy()
    
    def get_selected_preview_index(self) -> Optional[int]:
        """Get the index of the currently selected preview block."""
        return self._selected_preview_index
    
    def select_preview_block(self, index: int) -> bool:
        """Select a block from the preview by index.
        
        Args:
            index: Index of the block to select (0-based)
            
        Returns:
            bool: True if successfully selected, False otherwise
        """
        if 0 <= index < len(self._preview_blocks):
            self._selected_preview_index = index
            return True
        return False
    
    def rotate_selected_block(self, rotations: int = 1) -> bool:
        """Rotate the selected block by the specified number of rotations.
        
        Args:
            rotations: Number of 90-degree clockwise rotations to apply
            
        Returns:
            bool: True if successfully rotated, False if no block selected
        """
        if self._selected_preview_index is None:
            return False
            
        block, current_rotation = self._preview_blocks[self._selected_preview_index]
        new_rotation = (current_rotation + rotations) % 4
        self._preview_blocks[self._selected_preview_index] = (block, new_rotation)
        return True
    
    def get_valid_placements(self, block_index: Optional[int] = None,
                            rotation: Optional[int] = None) -> Set[Tuple[int, int]]:
        """Get all valid (row, col) positions where the specified block can be placed.
        
        Args:
            block_index: Index of the preview block (defaults to selected block)
            rotation: Rotation to apply (defaults to current rotation)
            
        Returns:
            Set of (row, col) tuples where the block can be placed
        """
        if block_index is None:
            block_index = self._selected_preview_index
            
        if block_index is None or not (0 <= block_index < len(self._preview_blocks)):
            return set()
            
        block, curr_rotation = self._preview_blocks[block_index]
        if rotation is None:
            rotation = curr_rotation
            
        # Get the rotated block
        rotated_block = block.rotate_clockwise(rotation)
        
        # Find all valid placements
        valid_positions = set()
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.can_place(rotated_block, r, c):
                    valid_positions.add((r, c))
                    
        return valid_positions
    
    def place_selected_block(self, row: int, col: int) -> bool:
        """Place the currently selected block at the specified position.
        
        Args:
            row: Row position (0-based, from top)
            col: Column position (0-based, from left)
            
        Returns:
            bool: True if successfully placed, False otherwise
        """
        if self._selected_preview_index is None:
            return False
            
        # Get selected block with rotation
        block, rotation = self._preview_blocks[self._selected_preview_index]
        rotated_block = block.rotate_clockwise(rotation)
        
        # Check if can place
        if not self.board.can_place(rotated_block, row, col):
            return False
            
        # Place the block
        self.board.place_block(rotated_block, row, col)
        self.blocks_placed += 1
        
        # Clear lines and update score
        lines = self.board.clear_full_lines()
        self.lines += lines
        
        # Scoring
        if lines:
            self.score += self.compute_line_score(lines)
        else:
            self.score += 1
            
        # Update difficulty if needed
        self._maybe_update_difficulty()
        
        # Remove from preview
        self._preview_blocks.pop(self._selected_preview_index)
        
        # Update selected index or reset if none left
        if not self._preview_blocks:
            self._selected_preview_index = None
            self._refill_preview()
        else:
            self._selected_preview_index = min(self._selected_preview_index, len(self._preview_blocks) - 1)
        
        # Check for game over
        self._check_game_over()
        
        return True
    
    def find_next_placeable_block(self) -> Optional[Tuple[int, int]]:
        """Find the next placeable block in the preview.
        
        Returns:
            Tuple of (block_index, rotation) or None if no block can be placed
        """
        for idx, (block, _) in enumerate(self._preview_blocks):
            for rotation in range(4):
                rotated_block = block.rotate_clockwise(rotation)
                if self._has_valid_placement(rotated_block):
                    return (idx, rotation)
        return None

    @property
    def game_over(self) -> bool:
        """Check if the game is over."""
        return self._game_over
        
    # ───────────────────────── Private methods ──────────────────────────
    
    def _spawn(self) -> Block:
        """Spawn a new block from the pool."""
        self._current_block = self.pool.sample()
        return self._current_block

    def _refill_preview(self, target_count=3):
        """Fill preview with blocks until we have target_count."""
        while len(self._preview_blocks) < target_count:
            self._spawn()
            self._preview_blocks.append((self._current_block, 0))  # (block, rotation)
        
        # If no block is selected, select the first one
        if self._selected_preview_index is None and self._preview_blocks:
            self._selected_preview_index = 0
    
    def _has_valid_placement(self, block: Block) -> bool:
        """Check if a block can be placed anywhere on the board."""
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.can_place(block, r, c):
                    return True
        return False
    
    def _check_game_over(self) -> bool:
        """Check if any block in the preview (in any rotation) can be placed.
        
        Returns:
            bool: True if game is over (no blocks can be placed), False otherwise
        """
        # If no blocks in preview, game is not over yet
        if not self._preview_blocks:
            self._game_over = False
            return False
        
        # Check if any block (in any rotation) can be placed
        for block, _ in self._preview_blocks:
            for rotation in range(4):
                rotated_block = block.rotate_clockwise(rotation)
                if self._has_valid_placement(rotated_block):
                    self._game_over = False
                    return False
        
        # No block can be placed - game over
        self._game_over = True
        return True
    
    def _maybe_update_difficulty(self):
        """Update difficulty based on score thresholds."""
        for thr, new_weights in self.config.get("difficulty_thresholds", []):
            if self.score >= thr:
                self.pool.weights = new_weights
