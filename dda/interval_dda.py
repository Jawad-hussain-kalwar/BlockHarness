from typing import Dict, List, Optional
import random
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry
from engine.block import Block


class IntervalDDA(BaseDDAAlgorithm):
    """DDA algorithm that introduces rescue and awkward blocks at specific intervals."""
    
    display_name = "Interval-Based"
    
    def __init__(self):
        """Initialize the interval DDA algorithm."""
        # Tray counters
        self.tray_count = 0
        
        # Configuration parameters
        self.steps_to_rescue = 2
        self.rescue_block_count = 1
        self.steps_to_awkward = 2
        self.awkward_block_count = 1
        
        # Default block weights (equal weights)
        #                      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.default_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        
        # Block classification
        # Rescue blocks: small blocks that typically fit well and can clear lines
        self.rescue_blocks = [0, 1, 2]  # Indices of rescue blocks (typically small blocks)
        
        # Awkward blocks: more complex shapes that are harder to place
        self.awkward_blocks = [7, 8, 9, 10]  # Indices of awkward blocks (S, Z, T, Plus, etc.)
    
    def initialize(self, config_params: Dict) -> None:
        """Initialize with configuration parameters.
        
        Args:
            config_params: Dictionary containing configuration parameters.
                Expected keys:
                - steps_to_rescue: Number of trays after which rescue blocks are spawned
                - rescue_block_count: Number of rescue blocks to include
                - steps_to_awkward: Number of trays after which awkward blocks are spawned
                - awkward_block_count: Number of awkward blocks to include
        """
        # Reset tray counter
        self.tray_count = 0
        
        # Load configuration parameters with default fallbacks
        self.steps_to_rescue = config_params.get("steps_to_rescue", 2)
        self.rescue_block_count = min(config_params.get("rescue_block_count", 1), 3)
        self.steps_to_awkward = config_params.get("steps_to_awkward", 2)
        self.awkward_block_count = min(config_params.get("awkward_block_count", 1), 3)
        
        # Ensure parameters are within valid ranges
        self.steps_to_rescue = max(1, self.steps_to_rescue)
        self.rescue_block_count = max(1, min(self.rescue_block_count, 3))
        self.steps_to_awkward = max(1, self.steps_to_awkward)
        self.awkward_block_count = max(1, min(self.awkward_block_count, 3))
    
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            Optional[List[int]]: New shape weights if adjustment needed, None otherwise
        """
        # Increment tray counter
        self.tray_count += 1
        
        # Calculate whether this is a rescue tray or awkward tray
        is_rescue_tray = (self.tray_count % self.steps_to_rescue == 0)
        is_awkward_tray = (self.tray_count > 1) and (self.tray_count % self.steps_to_awkward == 0)
        
        # No adjustment needed if not a special tray
        if not is_rescue_tray and not is_awkward_tray:
            return None
        
        # Initialize weights to default
        new_weights = self.default_weights.copy()
        
        # Adjust weights for rescue tray
        if is_rescue_tray:
            # Calculate boost factor to give preference to rescue blocks
            rescue_boost = 5  # Significant boost to rescue block probability
            
            # Apply boost to rescue blocks
            for idx in self.rescue_blocks[:self.rescue_block_count]:
                new_weights[idx] = rescue_boost
        
        # Adjust weights for awkward tray
        if is_awkward_tray:
            # Calculate boost factor to give preference to awkward blocks
            awkward_boost = 5  # Significant boost to awkward block probability
            
            # Apply boost to awkward blocks
            for idx in self.awkward_blocks[:self.awkward_block_count]:
                new_weights[idx] = awkward_boost
        
        # Return adjusted weights
        return new_weights
        
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Get the next blocks based on the interval pattern.
        
        This provides rescue or awkward blocks at specific intervals,
        giving direct control over specific shapes instead of just weights.
        
        Args:
            engine_state: The current game engine state
            count: Number of blocks to generate
            
        Returns:
            List[Block]: The specific blocks to be spawned
        """
        # Increment tray counter
        self.tray_count += 1
        
        # Get available shapes
        shapes = engine_state.config["shapes"]
        
        # Determine if this is a rescue or awkward interval
        is_rescue = (self.tray_count % self.steps_to_rescue == 0)
        is_awkward = (self.tray_count > 1) and (self.tray_count % self.steps_to_awkward == 0)
        
        # Initialize result list for blocks
        blocks = []
        
        # Handle rescue blocks
        if is_rescue:
            # Add specific rescue blocks
            rescue_shapes = [shapes[idx] for idx in self.rescue_blocks[:self.rescue_block_count] if idx < len(shapes)]
            blocks.extend([Block(shape) for shape in rescue_shapes])
        
        # Handle awkward blocks
        if is_awkward:
            # Add specific awkward blocks
            awkward_shapes = [shapes[idx] for idx in self.awkward_blocks[:self.awkward_block_count] if idx < len(shapes)]
            blocks.extend([Block(shape) for shape in awkward_shapes])
        
        # Fill remaining slots with random blocks
        remaining = count - len(blocks)
        if remaining > 0:
            # Use default weights for random selection
            weights = engine_state.pool.weights
            random_shapes = [random.choices(shapes, weights=weights, k=1)[0] for _ in range(remaining)]
            blocks.extend([Block(shape) for shape in random_shapes])
        
        # If we have more blocks than requested, trim the list
        return blocks[:count]


# Register the interval DDA algorithm
registry.register(IntervalDDA) 