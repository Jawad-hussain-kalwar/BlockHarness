from typing import Dict, List, Optional, Tuple
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry


class ThresholdDDA(BaseDDAAlgorithm):
    """DDA algorithm that changes shape weights at score thresholds."""
    
    display_name = "Score Threshold"
    
    def __init__(self):
        """Initialize the threshold DDA algorithm."""
        self.thresholds: List[Tuple[int, List[int]]] = []
        self.last_threshold_reached = -1
    
    def initialize(self, config_params: Dict) -> None:
        """Initialize with threshold configuration.
        
        Args:
            config_params: Dictionary containing configuration parameters.
                Expected to have a 'thresholds' key with a list of
                (score, weights) tuples.
        """
        # Extract thresholds from config, or use an empty list
        self.thresholds = config_params.get("thresholds", [])
        self.last_threshold_reached = -1
    
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Adjust weights when crossing a threshold.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            A new list of shape weights if a threshold was crossed,
            None otherwise
        """
        for idx, (score, weights) in enumerate(self.thresholds):
            if engine_state.score >= score and idx > self.last_threshold_reached:
                self.last_threshold_reached = idx
                return weights
        return None


# Register the threshold DDA algorithm
registry.register("ThresholdDDA", ThresholdDDA) 