from typing import Dict, List, Optional
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry


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
        self.weights = config_params.get("weights", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Static DDA never adjusts weights.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            None, as static DDA never adjusts weights
        """
        return None


# Register the static DDA algorithm
registry.register("StaticDDA", StaticDDA) 