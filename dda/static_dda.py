from typing import Dict, List, Optional, Tuple
import random
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry
from engine.block import Block
from config.defaults import DEFAULT_WEIGHTS


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
        # Get shapes count to ensure we have enough weights
        shapes_count = len(config_params.get("shapes", {}))
        
        # Use centralized defaults rather than hardcoded values
        # Get weights from config or use defaults
        weights = config_params.get("weights", DEFAULT_WEIGHTS)
        
        # Extend weights if there are more shapes than weights
        if shapes_count > len(weights):
            self.weights = weights + [0] * (shapes_count - len(weights))
        else:
            self.weights = weights[:shapes_count]
    
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
        shapes_dict = engine_state.config["shapes"]
        shape_names = list(shapes_dict.keys())
        
        # Ensure weights match the number of shapes
        weights = self.weights
        if len(weights) != len(shape_names):
            # If weights don't match, use truncated or extended version
            if len(weights) < len(shape_names):
                # Extend with zeros
                weights = weights + [0] * (len(shape_names) - len(weights))
            else:
                # Truncate
                weights = weights[:len(shape_names)]
                
        # Select blocks using static weights
        selected_shapes = []
        for _ in range(count):
            if sum(weights) > 0:
                # Use weighted selection if weights are not all zero
                shape_name = random.choices(shape_names, weights=weights, k=1)[0]
                shape = shapes_dict[shape_name]
            else:
                # Fall back to uniform selection if all weights are zero
                shape_name = random.choice(shape_names)
                shape = shapes_dict[shape_name]
            selected_shapes.append(shape)
            
        # Convert shapes to blocks
        return [Block(shape) for shape in selected_shapes]


# Register the static DDA algorithm
registry.register(StaticDDA) 