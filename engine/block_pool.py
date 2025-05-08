# engine/block_pool.py
import random
from typing import Dict, List, Tuple, Any, Optional
from engine.block import Block


class BlockPool:
    """Block generator with dynamic difficulty adjustment capabilities."""

    def __init__(self, shapes: Dict[str, List[Tuple[int, int]]], weights: List[int], config=None):
        """Initialize the block pool with shapes, weights, and configuration.
        
        Args:
            shapes: Dictionary of shape definitions mapped by name
            weights: List of weights for each shape (should match order of shapes.keys())
            config: Configuration dictionary containing DDA parameters
        """
        self.shapes = shapes
        self.shape_names = list(shapes.keys())
        self.weights = weights
        self.config = config or {}
        
        # Initialize DDA-related attributes
        self.tray_counter = 0  # Counter to keep track of tray refills
        self.L = 1  # Frequency of best-fit block generation (1-3)
        self.last_generated_blocks: List[str] = []  # Keep track of recently generated blocks
        
        # Load configuration
        self._load_config(self.config)
        
        # Adjust weights list length if needed
        if len(weights) != len(self.shape_names):
            raise ValueError("[engine/block_pool.py] Weights list length must match number of shapes")
            
        # Ensure at least one shape has a non-zero weight to avoid ValueError in random.choices
        if not any(weights) and self.shape_names:
            # If all weights are zero, set uniform weights
            self.weights = [1] * len(self.shape_names)

    def _load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration parameters for block generation.
        
        Args:
            config: Configuration dictionary
        """
        # Extract required configuration values
        dda_config = config.get("dda_params", {}).get("dda", {})
        
        # Load parameters with defaults
        self.low_clear_rate = dda_config.get("low_clear_rate", 0.5)
        self.high_clear_rate = dda_config.get("high_clear_rate", 0.8)
        self.score_threshold = dda_config.get("score_threshold", 100)
        self.n_best_fit_blocks = dda_config.get("n_best_fit_blocks", 1)
        self.n_game_over_blocks = dda_config.get("n_game_over_blocks", 1)

    # def get_block(self) -> Block:
    #     """Sample a random block based on shape weights.
        
    #     Returns:
    #         Block: A new block with randomly selected shape
    #     """
    #     if not self.shape_names:
    #         raise ValueError("[engine/block_pool.py] No shapes available in the block pool")
            
    #     try:
    #         shape_name = random.choices(self.shape_names, weights=self.weights, k=1)[0]
    #     except (ValueError, KeyError) as e:
    #         # Fallback to uniform selection if weights cause an error
    #         print(f"[engine/block_pool.py] Warning: Error in weighted selection ({e}), falling back to uniform selection")
    #         shape_name = random.choice(self.shape_names)
            
    #     shape = self.shapes[shape_name]
    #     return Block(shape)

    def get_next_blocks(self, engine_state, count=3) -> List[Block]:
        """Get the next blocks based on the game state and difficulty adjustment.
        
        Args:
            engine_state: Current game engine state
            count: Number of blocks to generate
            
        Returns:
            List[Block]: List of blocks for the preview tray
        """
        # Get metrics from engine state
        metrics = engine_state.get_metrics()
        
        # Increment tray counter
        self.tray_counter += 1
        
        # Generate blocks based on metrics and algorithm
        return self._generate_next_blocks(metrics, count)
    
    def _generate_next_blocks(self, metrics: Dict[str, Any], count: int) -> List[Block]:
        """Generate blocks based on the game metrics and algorithm.
        
        Args:
            metrics: Current game metrics
            count: Number of blocks to generate
            
        Returns:
            List[Block]: Generated blocks
        """
        # Extract metrics
        best_fit_block = metrics.get("best_fit_block", "None")
        opportunity = metrics.get("opportunity", False)
        game_over_blocks = metrics.get("game_over_blocks", ["None"])
        # If game_over_blocks doesn't exist in metrics (backward compatibility), use game_over_block
        if "None" in game_over_blocks and game_over_blocks == ["None"]:
            single_block = metrics.get("game_over_block", "None")
            if single_block != "None":
                game_over_blocks = [single_block]
                
        score = metrics.get("score", 0)
        clear_rate = metrics.get("clear_rate", 0.0)
        
        # Update L based on clear rate
        self._update_L_value(clear_rate)
        
        # Generate blocks based on conditions
        blocks = []
        
        if score < self.score_threshold:
            blocks = self._generate_blocks_below_threshold(best_fit_block, count, clear_rate, game_over_blocks)
        else:
            blocks = self._generate_blocks_above_threshold(game_over_blocks, opportunity, count)
        
        # Store generated block names for future reference
        self.last_generated_blocks = [b.get_shape_name() for b in blocks if hasattr(b, 'get_shape_name')]
        
        return blocks
    
    def _update_L_value(self, clear_rate: float) -> None:
        """Update the L value based on clear rate.
        
        Args:
            clear_rate: Current line clear rate
        """
        if clear_rate >= self.high_clear_rate:
            self.L = 3
        elif clear_rate >= self.low_clear_rate:
            self.L = 2
        else:
            self.L = 1
    
    def _filter_blocks_below_threshold(self, best_fit_block: str, game_over_blocks: List[str]) -> List[str]:
        """Filter out blocks that should be excluded from random selection.
        
        Args:
            best_fit_block: Name of the best fit block
            game_over_blocks: List of blocks that would cause game over
            
        Returns:
            List[str]: List of shape names to exclude from random selection
        """
        # Filter out "None" from game_over_blocks
        excluded_shapes = [block for block in game_over_blocks if block != "None"]
        
        # Add best fit block to excluded shapes if it exists and isn't already excluded
        if best_fit_block != "None" and best_fit_block in self.shape_names and best_fit_block not in excluded_shapes:
            excluded_shapes.append(best_fit_block)
            
        return excluded_shapes
    
    def _instantiate_block(self, shape_name: str) -> Block:
        """Create a Block instance from a shape name.
        
        Args:
            shape_name: Name of the shape to create
            
        Returns:
            Block: New Block instance
        """
        return Block(self.shapes[shape_name])
    
    def _should_add_best_fit_blocks(self, clear_rate: float, best_fit_block: str) -> bool:
        """Determine if best fit blocks should be added based on clear rate and tray counter.
        
        Args:
            clear_rate: Current line clear rate
            best_fit_block: Name of the best fit block
            
        Returns:
            bool: True if best fit blocks should be added
        """
        if best_fit_block == "None" or best_fit_block not in self.shape_names:
            return False
            
        if clear_rate < self.low_clear_rate:
            # Always add for low clear rate
            return True
        elif clear_rate < self.high_clear_rate:
            # Every 2nd tray for medium clear rate
            return self.tray_counter % 2 == 0
        else:
            # Every 3rd tray for high clear rate
            return self.tray_counter % 3 == 0
    
    def _generate_blocks_below_threshold(self, best_fit_block: str, count: int, clear_rate: float, 
                                       game_over_blocks: Optional[List[str]] = None) -> List[Block]:
        """Generate blocks when score is below threshold.
        
        Args:
            best_fit_block: Name of the best fit block
            count: Number of blocks to generate
            clear_rate: Current line clear rate
            game_over_blocks: List of blocks that would cause game over
            
        Returns:
            List[Block]: Generated blocks
        """
        blocks = []
        game_over_blocks = game_over_blocks or ["None"]
        
        # Check if we should add best fit blocks based on clear rate and tray counter
        if self._should_add_best_fit_blocks(clear_rate, best_fit_block):
            # Add best fit blocks
            best_fit_count = min(self.n_best_fit_blocks, count)
            blocks.extend([self._instantiate_block(best_fit_block) for _ in range(best_fit_count)])
            
            # Get excluded shapes for random block selection
            excluded_shapes = self._filter_blocks_below_threshold(best_fit_block, game_over_blocks)
            
            # Add random blocks to complete the count
            random_blocks = self._select_distinct_blocks(count - len(blocks), excluded_shapes)
            blocks.extend(random_blocks)
        else:
            # Get excluded shapes (just game over blocks in this case)
            excluded_shapes = [block for block in game_over_blocks if block != "None"]
            
            # Generate all random blocks
            blocks = self._select_distinct_blocks(count, excluded_shapes)
        
        # Shuffle to avoid predictable patterns
        random.shuffle(blocks)
        return blocks
    
    def _generate_blocks_above_threshold(self, game_over_blocks: List[str], opportunity: bool, count: int) -> List[Block]:
        """Generate blocks when score is above threshold.
        
        Args:
            game_over_blocks: List of blocks that would cause game over
            opportunity: Whether there's a game over opportunity
            count: Number of blocks to generate
            
        Returns:
            List[Block]: Generated blocks
        """
        blocks = []
        
        # Filter out "None" from game_over_blocks
        valid_game_over_blocks = [block for block in game_over_blocks if block != "None" and block in self.shape_names]
        
        # Generate game over blocks if opportunity exists
        if opportunity and valid_game_over_blocks:
            # Select a game over block (for consistency, use the first one if multiple exist)
            game_over_block = valid_game_over_blocks[0]
            
            # Add game over blocks
            for _ in range(min(self.n_game_over_blocks, count)):
                blocks.append(Block(self.shapes[game_over_block]))
            
            # Add random blocks to complete the count
            excluded_shapes = valid_game_over_blocks.copy()
            random_blocks = self._select_distinct_blocks(count - len(blocks), excluded_shapes)
            blocks.extend(random_blocks)
        else:
            # If no game over opportunity, generate all random blocks
            blocks = self._select_distinct_blocks(count)
        
        # Shuffle to avoid predictable patterns
        random.shuffle(blocks)
        return blocks
    
    def _select_distinct_blocks(self, count: int, excluded_shapes: Optional[List[str]] = None) -> List[Block]:
        """Select distinct blocks with optional exclusions.
        
        Args:
            count: Number of blocks to select
            excluded_shapes: List of shape names to exclude
            
        Returns:
            List[Block]: List of distinct blocks
        """
        if excluded_shapes is None:
            excluded_shapes = []
        
        # Create a set of excluded shapes for faster lookups
        excluded_set = set(excluded_shapes)
        recent_set = set(self.last_generated_blocks)
        
        # First try excluding both excluded_shapes and recently generated blocks
        available_shapes = [s for s in self.shape_names if s not in excluded_set and s not in recent_set]
        
        # If we don't have enough shapes, try only excluding the explicit exclusions
        if len(available_shapes) < count:
            available_shapes = [s for s in self.shape_names if s not in excluded_set]
        
        # If we still don't have enough shapes, we'll have to allow duplicates
        if len(available_shapes) < count:
            # Use random.choices which allows duplicates
            if available_shapes:
                # We have some available shapes but not enough for count distinct ones
                selected_shape_names = random.choices(available_shapes, k=count)
            else:
                # Ultimate fallback: no shapes available after exclusions, use any shape
                selected_shape_names = random.choices(self.shape_names, k=count)
        else:
            # We have enough shapes for random.sample (which guarantees distinctness)
            selected_shape_names = random.sample(available_shapes, count)
        
        # Create blocks from the selected shape names
        return [self._instantiate_block(name) for name in selected_shape_names]
