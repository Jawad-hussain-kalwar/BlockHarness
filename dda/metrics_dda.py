from typing import Dict, List, Optional
import random
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry
from engine.block import Block

class MetricsDDA(BaseDDAAlgorithm):
    """DDA algorithm that adjusts difficulty based on player performance metrics."""
    
    display_name = "Metrics Adaptive"
    
    def __init__(self):
        """Initialize the metrics-based DDA algorithm."""
        self.difficulty_level = 3  # Default initial difficulty (1-10)
        self.low_clear = 0.30
        self.high_clear = 0.70
        self.danger_threshold = 0.80
        self.rescue_shape_weights = []
        self.size_caps = []
        self.current_mode = "normal"  # "normal", "rescue", or "emergency"
        
    def initialize(self, config_params: Dict) -> None:
        """Initialize algorithm with configuration parameters."""
        params = config_params.get("metrics_dda", {})
        self.difficulty_level = params.get("initial_difficulty", 3)
        
        # Get flow parameters from global metrics config if not specified
        metrics_flow = config_params.get("metrics_flow", {})
        self.low_clear = params.get("low_clear", metrics_flow.get("low_clear", 0.30))
        self.high_clear = params.get("high_clear", metrics_flow.get("high_clear", 0.70))
        self.danger_threshold = params.get("danger_cut", metrics_flow.get("danger_cut", 0.80))
        
        # Other parameters
        self.rescue_shape_weights = params.get("rescue_shape_weights", [10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.size_caps = params.get("size_caps", [3, 3, 3, 4, 4, 4, 5, 5, 5, 5])
        
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed."""
        # Get all metrics from the engine
        metrics = engine_state.get_metrics()
        
        # Check for emergency mode (imminent threat)
        imminent_threat = metrics.get("imminent_threat", False)
        if imminent_threat:
            self.current_mode = "emergency"
            return self._get_emergency_weights()
            
        # Check for rescue mode (high danger score)
        danger_score = metrics.get("danger_score", 0.0)
        if danger_score >= self.danger_threshold:
            if self.current_mode != "rescue":
                self.current_mode = "rescue"
                return self._get_rescue_weights()
        else:
            # Normal mode - check if we need to adjust difficulty
            self.current_mode = "normal"
            
            # Get player performance metrics
            clear_rate = metrics.get("clear_rate", 0.5)
            emotional_state = metrics.get("emotional_state", "Calm")
            
            # Adjust difficulty level based on clear rate
            old_difficulty = self.difficulty_level
            if clear_rate < self.low_clear:
                self.difficulty_level = max(1, self.difficulty_level - 1)
            elif clear_rate > self.high_clear:
                self.difficulty_level = min(10, self.difficulty_level + 1)
                
            # Special adjustments based on emotional state
            if emotional_state == "Frustrated" and danger_score > 0.6:
                self.difficulty_level = max(1, self.difficulty_level - 2)
            elif emotional_state == "Bored" and self.difficulty_level < 10:
                self.difficulty_level = min(10, self.difficulty_level + 1)
                
            # Return new weights if difficulty changed
            if old_difficulty != self.difficulty_level:
                return self._get_normal_weights(metrics.get("phase", "mid"))
                
        # No adjustment needed
        return None
    
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Get the next blocks based on current game metrics.
        
        Args:
            engine_state: The current game engine state
            count: Number of blocks to generate
            
        Returns:
            List[Block]: The specific blocks to be spawned
        """
        # Get the danger score from metrics manager
        metrics = engine_state.get_metrics()
        danger_score = metrics.get("danger_score", 0.0)
        
        # Get shapes from configuration
        shapes = engine_state.config["shapes"]
        
        # Determine if we're in a rescue scenario
        is_rescue_needed = danger_score >= self.danger_threshold
        
        blocks = []
        
        if is_rescue_needed:
            # Select smaller, simpler shapes for rescue
            rescue_indices = [0, 1, 2]  # Indices of simple shapes
            # Ensure indices are within range
            valid_indices = [idx for idx in rescue_indices if idx < len(shapes)]
            
            # Select blocks for rescue scenario
            for _ in range(count):
                if valid_indices:  # Check if we have valid rescue shapes
                    shape_idx = random.choice(valid_indices)
                    blocks.append(Block(shapes[shape_idx]))
                else:
                    # Fallback to first shape if no valid rescue shapes
                    blocks.append(Block(shapes[0]))
        else:
            # Normal difficulty-based selection
            # Use the current difficulty level to determine max block size
            max_size = self.size_caps[min(int(self.difficulty_level) - 1, len(self.size_caps) - 1)]
            
            # Filter shapes that are appropriate for current difficulty
            valid_shapes = [(i, shape) for i, shape in enumerate(shapes) 
                          if self._get_shape_size(shape) <= max_size]
            
            if not valid_shapes:
                # Fallback if no shapes meet criteria
                valid_shapes = [(i, shape) for i, shape in enumerate(shapes)]
            
            # Select from valid shapes
            for _ in range(count):
                shape_idx, shape = random.choice(valid_shapes)
                blocks.append(Block(shape))
        
        return blocks
        
    def _get_shape_size(self, shape) -> int:
        """Calculate the effective size of a shape.
        
        Args:
            shape: The shape definition (list of lists)
            
        Returns:
            int: Size metric of the shape
        """
        # Simple size metric: number of filled cells
        return sum(sum(row) for row in shape)
        
    def _get_emergency_weights(self) -> List[int]:
        """Get weights for emergency mode - only smallest shapes."""
        weights = [0] * 11  # Assuming 11 shape types
        weights[0] = 10  # High weight for 1x1 shape
        weights[1] = 5   # Medium weight for 1x2 shape
        return weights
        
    def _get_rescue_weights(self) -> List[int]:
        """Get weights for rescue mode - favor small shapes."""
        return self.rescue_shape_weights
        
    def _get_normal_weights(self, phase: str) -> List[int]:
        """Get weights for normal mode based on difficulty and phase."""
        weights = [1] * 11  # Default equal weights
        
        # Get size cap based on difficulty level
        idx = min(int(self.difficulty_level) - 1, len(self.size_caps) - 1)
        size_cap = self.size_caps[idx]
        
        # Reduce size cap in early phase
        if phase == "early":
            size_cap = min(size_cap, 3)
            
        # Apply weights based on size cap
        for i in range(len(weights)):
            if i < size_cap:
                weights[i] = size_cap - i + 1  # Higher weights for smaller shapes
            else:
                weights[i] = 0  # Zero weight for shapes above size cap
                
        return weights

# Register the metrics DDA algorithm
registry.register(MetricsDDA) 