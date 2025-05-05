"""
Base interface for Dynamic Difficulty Adjustment (DDA) algorithms.
This defines the standard interface that all DDA algorithms must implement.
"""
from abc import ABC, abstractmethod
import random
from typing import Dict, List, Optional, Tuple, Any

# Import Block class for creating blocks
from engine.block import Block


class BaseDDAAlgorithm(ABC):
    """Base class for all DDA algorithms.
    
    Each DDA algorithm must implement the initialize() and maybe_adjust() methods.
    The get_next_blocks() method has a default implementation that uses maybe_adjust()
    to determine whether to adjust the block weights, but algorithms can override it
    with custom behavior.
    """
    
    # Class attribute for dropdown display
    display_name = "Abstract DDA Algorithm"
    
    @property
    def name(self) -> str:
        """Return algorithm name.
        
        Returns:
            str: The name of the algorithm (class name by default)
        """
        return self.__class__.__name__
    
    @abstractmethod
    def initialize(self, config_params: Dict[str, Any]) -> None:
        """Initialize algorithm with configuration parameters.
        
        Args:
            config_params: Dictionary containing configuration parameters
                           specific to this algorithm.
        """
        pass
        
    @abstractmethod
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed.
        
        This is called before each block generation to determine if the
        difficulty should be adjusted based on the current state of the game.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            Optional[List[int]]: New shape weights if adjustment needed, None otherwise
        """
        pass
    
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Generate the next set of blocks for the game.
        
        This default implementation uses maybe_adjust() to determine whether to
        adjust block weights, then uses weighted random selection to choose blocks.
        
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
        shapes_dict = engine_state.config["shapes"]
        shape_names = list(shapes_dict.keys())
        
        # Ensure weights match the number of shapes
        if len(weights) < len(shape_names):
            weights = weights + [0] * (len(shape_names) - len(weights))
        elif len(weights) > len(shape_names):
            weights = weights[:len(shape_names)]
        
        # Select shapes using weighted random choice
        selected_shape_names = [random.choices(shape_names, weights=weights, k=1)[0] for _ in range(count)]
        selected_shapes = [shapes_dict[name] for name in selected_shape_names]
        
        # Convert shapes to blocks
        return [Block(shape) for shape in selected_shapes] 