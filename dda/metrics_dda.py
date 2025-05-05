from typing import Dict, List, Optional, Tuple, Any
import random
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry
from engine.block import Block
from config.defaults import RESCUE_WEIGHTS

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
        
    def initialize(self, config_params: Dict[str, Any]) -> None:
        """Initialize algorithm with configuration parameters."""
        params = config_params.get("metrics_dda", {})
        self.difficulty_level = params.get("initial_difficulty", 3)
        
        # Get flow parameters from global metrics config if not specified
        metrics_flow = config_params.get("metrics_flow", {})
        self.low_clear = params.get("low_clear", metrics_flow.get("low_clear", 0.30))
        self.high_clear = params.get("high_clear", metrics_flow.get("high_clear", 0.70))
        self.danger_threshold = params.get("danger_cut", metrics_flow.get("danger_cut", 0.80))
        
        # Use RESCUE_WEIGHTS from defaults rather than hardcoded values
        shape_count = len(config_params.get("shapes", {}))
        
        # Get rescue weights from configuration or use RESCUE_WEIGHTS from defaults
        rescue_weights = params.get("rescue_shape_weights", RESCUE_WEIGHTS)
        
        # Ensure rescue weights are the right length
        if shape_count > len(rescue_weights):
            self.rescue_shape_weights = rescue_weights + [0] * (shape_count - len(rescue_weights))
        else:
            self.rescue_shape_weights = rescue_weights[:shape_count]
            
        # Get size caps from configuration or use default
        self.size_caps = params.get("size_caps", [3, 3, 3, 4, 4, 4, 5, 5, 5, 5])
        
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed."""
        # Get all metrics from the engine
        metrics = engine_state.get_metrics()
        
        # Ensure weights array length matches number of shapes
        shape_count = len(engine_state.config["shapes"])
        if len(self.rescue_shape_weights) != shape_count:
            # Create a new rescue weights array of the right size
            if shape_count > len(self.rescue_shape_weights):
                self.rescue_shape_weights = self.rescue_shape_weights + [0] * (shape_count - len(self.rescue_shape_weights))
            else:
                self.rescue_shape_weights = self.rescue_shape_weights[:shape_count]
        
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
        shapes_dict = engine_state.config["shapes"]
        shape_names = list(shapes_dict.keys())
        
        # Determine if we're in a rescue scenario
        is_rescue_needed = danger_score >= self.danger_threshold
        
        blocks = []
        
        if is_rescue_needed:
            # Select smaller, simpler shapes for rescue
            # For dictionaries, we'll focus on the smaller shapes like 1x1, 1x2, 2x1
            rescue_shapes = ["1x1-square", "1x2-line", "2x1-line"]
            # Filter valid rescue shapes that exist in our dict
            valid_rescue_shapes = [name for name in rescue_shapes if name in shape_names]
            
            # Select blocks for rescue scenario
            for _ in range(count):
                if valid_rescue_shapes:  # Check if we have valid rescue shapes
                    shape_name = random.choice(valid_rescue_shapes)
                    blocks.append(Block(shapes_dict[shape_name]))
                else:
                    # Fallback to first shape if no valid rescue shapes
                    fallback_shape = shapes_dict[shape_names[0]]
                    blocks.append(Block(fallback_shape))
        else:
            # Normal difficulty-based selection
            # Use the current difficulty level to determine max block size
            max_size = self.size_caps[min(int(self.difficulty_level) - 1, len(self.size_caps) - 1)]
            
            # Filter shapes that are appropriate for current difficulty
            valid_shapes = []
            for name, shape in shapes_dict.items():
                if self._get_shape_size(shape) <= max_size:
                    valid_shapes.append((name, shape))
            
            if not valid_shapes:
                # Fallback if no shapes meet criteria
                valid_shapes = [(name, shape) for name, shape in shapes_dict.items()]
            
            # Select from valid shapes
            for _ in range(count):
                shape_name, shape = random.choice(valid_shapes)
                blocks.append(Block(shape))
        
        return blocks
        
    def _get_shape_size(self, shape) -> int:
        """Calculate the effective size of a shape.
        
        Args:
            shape: The shape definition (list of coordinate tuples)
            
        Returns:
            int: Size metric of the shape
        """
        # Size metric: number of cells in the shape
        return len(shape)
        
    def _get_emergency_weights(self) -> List[int]:
        """Get weights for emergency mode - only smallest shapes."""
        # Create a weight list with the same length as shapes
        weights = [0] * len(self.rescue_shape_weights)
        
        # Set high weight for simplest shapes (small patterns first)
        if len(weights) > 0:
            weights[0] = 10  # High weight for 1x1 shape
        if len(weights) > 1:
            weights[1] = 5   # Medium weight for small shapes
        if len(weights) > 2:
            weights[2] = 3   # Some weight for third shape
        
        return weights
        
    def _get_rescue_weights(self) -> List[int]:
        """Get weights for rescue mode - favor small shapes."""
        return self.rescue_shape_weights
        
    def _get_normal_weights(self, phase: str) -> List[int]:
        """Get weights for normal mode based on difficulty and phase."""
        shape_count = len(self.rescue_shape_weights)
        weights = [1] * shape_count  # Default equal weights
        
        # Get size cap based on difficulty level
        idx = min(int(self.difficulty_level) - 1, len(self.size_caps) - 1)
        size_cap = self.size_caps[idx]
        
        # Reduce size cap in early phase
        if phase == "early":
            size_cap = min(size_cap, 3)
        
        # Apply progressive weights based on difficulty
        # Higher difficulty means more complex shapes get higher weights
        weight_factor = self.difficulty_level / 10.0  # 0.1 to 1.0
        
        # Calculate how many shapes to enable based on difficulty
        enabled_shapes = max(3, int(shape_count * weight_factor))
        
        # Give higher weights to appropriate shapes based on difficulty
        for i in range(shape_count):
            if i < enabled_shapes:
                # Weights taper off gradually, with bias based on difficulty
                if self.difficulty_level <= 3:
                    # At low difficulty, favor simple shapes
                    weights[i] = max(1, enabled_shapes - i)
                elif self.difficulty_level <= 7:
                    # At medium difficulty, favor medium-complexity shapes
                    mid_point = enabled_shapes // 2
                    weights[i] = max(1, enabled_shapes - abs(i - mid_point))
                else:
                    # At high difficulty, favor complex shapes
                    weights[i] = max(1, i + 1)
            else:
                weights[i] = 0  # Disable shapes beyond our difficulty level
        
        return weights

# Register the metrics DDA algorithm
registry.register(MetricsDDA) 