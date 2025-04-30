# ai/Greedy1.py
from typing import Tuple, Optional

from engine.game_engine import GameEngine
from ai.base_player import BaseAIPlayer


class GreedyAIPlayer(BaseAIPlayer):
    """Greedy heuristic: choose move that clears most lines now."""
    
    @property
    def name(self) -> str:
        return "Greedy"

    def choose_move(self, engine: GameEngine, block_index: int, rotation: int) -> Optional[Tuple[int, int]]:
        """Choose the best placement for a block.
        
        Args:
            engine: The game engine
            block_index: Index of the block to place
            rotation: Rotation to apply to the block
            
        Returns:
            Tuple of (row, col) for best placement or None if no valid placement
        """
        best_move = None
        best_score = -1
        
        # Get all valid placements for this block+rotation
        valid_placements = engine.get_valid_placements(block_index, rotation)
        
        if not valid_placements:
            return None
            
        # Score each placement using our heuristic
        for r, c in valid_placements:
            # Create a copy of the board to simulate placement
            from copy import deepcopy
            tmp_board = deepcopy(engine.board)
            
            # Get the block with rotation
            block_list = engine.get_preview_blocks()
            if not 0 <= block_index < len(block_list):
                continue
                
            block, _ = block_list[block_index]
            rotated_block = block.rotate_clockwise(rotation)
            
            # Place the block
            tmp_board.place_block(rotated_block, r, c)
            
            # Check how many lines would be cleared
            cleared = tmp_board.clear_full_lines()
            score = GameEngine.compute_line_score(cleared)
            
            if score > best_score:
                best_score = score
                best_move = (r, c)
                
        return best_move


# For backwards compatibility - this will maintain compatibility with existing code
AIPlayer = GreedyAIPlayer
