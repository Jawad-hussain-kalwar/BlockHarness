# ai/Random.py
import random
from typing import Tuple, Optional

from engine.game_engine import GameEngine
from ai.base_player import BaseAIPlayer


class RandomAIPlayer(BaseAIPlayer):
    """Random strategy: choose a random valid placement for a block."""
    
    @property
    def name(self) -> str:
        return "Random"
    
    def choose_move(self, engine: GameEngine, block_index: int, rotation: int) -> Optional[Tuple[int, int]]:
        """Choose a random valid placement for a block.
        
        Args:
            engine: The game engine
            block_index: Index of the block to place
            rotation: Rotation to apply to the block
            
        Returns:
            Tuple of (row, col) for random placement or None if no valid placement
        """
        # Get all valid placements for this block+rotation
        valid_placements = engine.get_valid_placements(block_index, rotation)
        
        if not valid_placements:
            return None
            
        # Choose a random placement
        return random.choice(list(valid_placements)) 