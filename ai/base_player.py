from typing import Tuple, Optional
from abc import ABC, abstractmethod

from engine.game_engine import GameEngine


class BaseAIPlayer(ABC):
    """Base abstract class for all AI players.
    
    All AI player implementations should inherit from this class
    and implement the choose_move method.
    """
    
    def __init__(self):
        """Initialize the AI player."""
        pass
    
    @property
    def name(self) -> str:
        """Get the name of the AI player.
        
        The default implementation uses the class name, but subclasses
        can override this to provide a more meaningful display name.
        """
        return self.__class__.__name__
    
    @property
    def description(self) -> str:
        """Get a description of the AI player's strategy.
        
        This should be overridden by subclasses to provide a description
        of the AI player's strategy.
        """
        return "No description provided."
    
    @abstractmethod
    def choose_move(self, engine: GameEngine, block_index: int) -> Optional[Tuple[int, int]]:
        """Choose the best placement for a block.
        
        Args:
            engine: The game engine
            block_index: Index of the block to place
            
        Returns:
            Tuple of (row, col) for best placement or None if no valid placement
        """
        pass