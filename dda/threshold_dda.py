from typing import Dict, List, Optional, Tuple, Any
import random
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry
from engine.block import Block
from config.defaults import DEFAULT_WEIGHTS, HARDER_WEIGHTS, HARDEST_WEIGHTS


class ThresholdDDA(BaseDDAAlgorithm):
    """DDA algorithm that changes shape weights at score thresholds."""
    
    display_name = "Score Threshold"
    
    def __init__(self):
        """Initialize the threshold DDA algorithm."""
        self.thresholds: List[Tuple[int, List[int]]] = []
        self.last_threshold_reached = -1
        self.shape_count = 0
    
    def initialize(self, config_params: Dict[str, Any]) -> None:
        """Initialize with threshold configuration.
        
        Args:
            config_params: Dictionary containing configuration parameters.
                Expected to have a 'thresholds' key with a list of
                (score, weights) tuples.
        """
        # Get thresholds from config params or use defaults
        thresholds = config_params.get("thresholds", [
            (1000, HARDER_WEIGHTS),
            (3000, HARDEST_WEIGHTS)
        ])
        
        # Get shapes count to ensure all thresholds have correct weight lengths
        self.shape_count = len(config_params.get("shapes", {}))
        
        # Ensure each threshold's weights are the right length
        self.thresholds = []
        for score, weights in thresholds:
            if len(weights) < self.shape_count:
                # Extend weights if too short
                adjusted_weights = weights + [0] * (self.shape_count - len(weights))
            else:
                # Truncate if too long
                adjusted_weights = weights[:self.shape_count]
            self.thresholds.append((score, adjusted_weights))
            
        self.last_threshold_reached = -1
    
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Adjust weights when crossing a threshold.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            A new list of shape weights if a threshold was crossed,
            None otherwise
        """
        # Check if shape count has changed (new shapes added)
        current_shape_count = len(engine_state.config["shapes"])
        if current_shape_count != self.shape_count:
            # Re-initialize thresholds with the new shape count
            self.shape_count = current_shape_count
            adjusted_thresholds = []
            for score, weights in self.thresholds:
                if len(weights) < self.shape_count:
                    adjusted_weights = weights + [0] * (self.shape_count - len(weights))
                else:
                    adjusted_weights = weights[:self.shape_count]
                adjusted_thresholds.append((score, adjusted_weights))
            self.thresholds = adjusted_thresholds
        
        # Check for threshold crossing
        for idx, (score, weights) in enumerate(self.thresholds):
            if engine_state.score >= score and idx > self.last_threshold_reached:
                self.last_threshold_reached = idx
                return weights
        return None
        
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Get the next blocks based on threshold-adjusted weights.
        
        Args:
            engine_state: The current game engine state
            count: Number of blocks to generate
            
        Returns:
            List[Block]: The specific blocks to be spawned
        """
        # First check for threshold crossing
        weights = self.maybe_adjust(engine_state)
        
        # If no adjustment, use current weights from engine
        if weights is None:
            weights = engine_state.pool.weights
        
        # Select 'count' shapes using the adjusted weights
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


# Register the threshold DDA algorithm
registry.register(ThresholdDDA) 