from abc import ABC, abstractmethod
import random
from typing import Dict, List, Optional

# Import Block class for creating blocks
from engine.block import Block


class BaseDDAAlgorithm(ABC):
    """Base class for all DDA algorithms."""
    
    # Class attribute for dropdown display
    display_name = "Abstract DDA Algorithm"
    
    @abstractmethod
    def initialize(self, config_params: Dict) -> None:
        """Initialize algorithm with configuration parameters."""
        pass
        
    @abstractmethod
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            Optional[List[int]]: New shape weights if adjustment needed, None otherwise
        """
        pass
    
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Default implementation that uses maybe_adjust() and weighted random selection.
        DDA algorithms should override this with their own implementation.
        
        Args:
            engine_state: The current game engine state
            count: Number of blocks to generate (default 3)
            
        Returns:
            List[Block]: The specific blocks to be spawned in the preview tray
        """
        # Get weights adjustment if any
        weights = self.maybe_adjust(engine_state)
        
        # If no adjustment, use default weights from engine
        if weights is None:
            weights = engine_state.config.get("shape_weights", [1] * len(engine_state.config["shapes"]))
        
        # Select 'count' blocks using weighted random choice
        shapes = engine_state.config["shapes"]
        selected_shapes = [random.choices(shapes, weights=weights, k=1)[0] for _ in range(count)]
        
        # Convert shapes to blocks
        return [Block(shape) for shape in selected_shapes]
        
    @property
    def name(self) -> str:
        """Return algorithm name."""
        return self.__class__.__name__ 