# ai/Random.py
import random
from typing import Tuple, Optional

from engine.game_engine import GameEngine
from ai.base_player import BaseAIPlayer


class Random(BaseAIPlayer):
    """Random AI player that chooses a random valid placement."""
    
    @property
    def name(self) -> str:
        return "Random"
    
    @property
    def description(self) -> str:
        return "Chooses a random valid placement from all possibilities."
    
    def choose_move(self, engine: GameEngine, block_index: int) -> Optional[Tuple[int, int]]:
        """Choose a random valid placement for a block.
        
        Args:
            engine: The game engine
            block_index: Index of the block to place
            
        Returns:
            Tuple of (row, col) for random valid placement or None if no valid placement
        """
        # Get all valid placements for this block
        valid_placements = engine.get_valid_placements(block_index)
        
        if not valid_placements:
            return None
            
        # Choose a random placement
        return random.choice(list(valid_placements)) 