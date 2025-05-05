from typing import Dict, List, Optional
import random
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry
from engine.block import Block


class StaticDDA(BaseDDAAlgorithm):
    """DDA algorithm that maintains constant weights for all blocks."""
    
    display_name = "Static"
    
    def __init__(self):
        """Initialize the static DDA algorithm."""
        self.weights = []
    
    def initialize(self, config_params: Dict) -> None:
        """Initialize with fixed weights configuration.
        
        Args:
            config_params: Dictionary containing configuration parameters.
                Expected to have a 'weights' key with a list of initial weights.
        """
        # Extract weights from config, or use a default set of equal weights
        self.weights = config_params.get("weights", [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Static DDA never adjusts weights.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            None, as static DDA never adjusts weights
        """
        return None
        
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Get the next blocks based on static weights.
        
        Args:
            engine_state: The current game engine state
            count: Number of blocks to generate
            
        Returns:
            List[Block]: The specific blocks to be spawned
        """
        # Get shapes and use static weights for selection
        shapes = engine_state.config["shapes"]
        
        # Ensure weights match the number of shapes
        weights = self.weights
        if len(weights) != len(shapes):
            # If weights don't match, use truncated or extended version
            if len(weights) < len(shapes):
                # Extend with zeros
                weights = weights + [0] * (len(shapes) - len(weights))
            else:
                # Truncate
                weights = weights[:len(shapes)]
                
        # Select blocks using static weights
        selected_shapes = []
        for _ in range(count):
            if sum(weights) > 0:
                # Use weighted selection if weights are not all zero
                shape = random.choices(shapes, weights=weights, k=1)[0]
            else:
                # Fall back to uniform selection if all weights are zero
                shape = random.choice(shapes)
            selected_shapes.append(shape)
            
        # Convert shapes to blocks
        return [Block(shape) for shape in selected_shapes]


# Register the static DDA algorithm
registry.register("StaticDDA", StaticDDA) 