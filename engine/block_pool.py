# engine/block_pool.py
import random
from typing import Dict, List, Any, Optional
from engine.block import Block


class BlockPool:
    """Block generator with dynamic difficulty adjustment capabilities."""

    def __init__(self, shapes: Dict[str, Any], weights: List[int], config=None):
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
        try:
            assert self.L in [1, 2, 3], f"[engine/block_pool.py][27] L must be 1, 2, or 3, got {self.L}"
        except AssertionError as e:
            print(f"[engine/block_pool.py][29] {e}")
            self.L = 1
        self.last_generated_blocks: List[str] = []  # Keep track of recently generated blocks
        
        # Load configuration
        self._load_config(self.config)
        
        # Adjust weights list length if needed
        if len(weights) != len(self.shape_names):
            raise ValueError("[engine/block_pool.py] Weights list length must match number of shapes")
            
        # Ensure at least one shape has a non-zero weight to avoid ValueError in random.choices
        if not any(weights) and self.shape_names:
            # If all weights are zero, set uniform weights
            print(f"[engine/block_pool.py][43] All weights are zero, setting uniform weights")
            self.weights = [1] * len(self.shape_names)

    def _load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration parameters for block generation.
        
        Args:
            config: Configuration dictionary
        """
        # Extract required configuration values
        dda_config = config.get("dda_params", {})
        
        # Load parameters with defaults
        self.low_clear_rate = dda_config.get("low_clear_rate", 0.5)
        self.high_clear_rate = dda_config.get("high_clear_rate", 0.8)
        self.score_threshold = dda_config.get("score_threshold", 99999)
        self.n_best_fit_blocks = dda_config.get("n_best_fit_blocks", 1)  # N in the algorithm

    def get_next_blocks(self, engine_state) -> List[Block]:
        """Get the next blocks based on the game state and difficulty adjustment.
        
        Args:
            engine_state: Current game engine state
            
        Returns:
            List[Block]: List of blocks for the preview tray (always 3 blocks)
        """
        # Get metrics from engine state
        metrics = engine_state.get_metrics()
        
        # Increment tray counter
        self.tray_counter += 1
        
        # Generate exactly 3 blocks based on metrics and algorithm
        return self._generate_next_blocks(metrics)
    
    def _generate_next_blocks(self, metrics: Dict[str, Any]) -> List[Block]:
        """Generate blocks based on the game metrics and algorithm.
        
        Args:
            metrics: Current game metrics
            
        Returns:
            List[Block]: Generated blocks (always 3)
        """
        # Extract metrics
        best_fit_blocks = metrics.get("best_fit_blocks", [])
        game_over_blocks = metrics.get("game_over_blocks", [])
        score = metrics.get("score", 0)
        clear_rate = metrics.get("clear_rate", 0.0)
        
        print(f"[engine/block_pool.py][94] generating blocks for score: {score}, clear rate: {clear_rate}")
        print(f"[engine/block_pool.py][95] based on {len(best_fit_blocks)} best fit blocks")
        print(f"[engine/block_pool.py][96] and {len(game_over_blocks)} game over blocks")
        # Fixed count - always generate exactly 3 blocks
        count = 3
        
        # Update L based on clear rate as per algorithm
        if clear_rate >= self.high_clear_rate:
            self.L = 3
        elif clear_rate >= self.low_clear_rate:
            self.L = 2
        else:
            self.L = 1
        
        print(f"[engine/block_pool.py][108] L is now {self.L}")
        # Generate blocks based on conditions
        if score < self.score_threshold:
            blocks = self._generate_blocks_below_threshold(best_fit_blocks, game_over_blocks, count)
        else:
            blocks = self._generate_blocks_above_threshold(game_over_blocks, count)
        
        # Store generated block IDs for future reference
        self.last_generated_blocks = [b.shape_id for b in blocks if hasattr(b, 'shape_id')]
        
        return blocks
    
    def _generate_blocks_below_threshold(self, best_fit_blocks: List[Block], game_over_blocks: List[Block], count: int) -> List[Block]:
        """Generate blocks when score is below threshold.
        
        Args:
            best_fit_blocks: List of blocks that clear the most lines
            game_over_blocks: List of blocks that cannot fit on the board
            count: Number of blocks to generate (always 3)
            
        Returns:
            List[Block]: Generated blocks
        """
        blocks = []
        
        # Get shape IDs of game over blocks to exclude them
        game_over_shape_ids = [b.shape_id for b in game_over_blocks if hasattr(b, 'shape_id')]
        
        # Determine if we should include best fit blocks in this tray
        # L=1: include in every tray, L=2: every 2nd tray, L=3: every 3rd tray
        include_best_fit = (self.tray_counter % self.L == 0)
        
        if include_best_fit and best_fit_blocks:
            # Determine how many best fit blocks to include (N from config)
            n_best_fit = min(self.n_best_fit_blocks, count, len(best_fit_blocks))
            
            # Randomly select N best fit blocks if we have more than N
            if len(best_fit_blocks) > n_best_fit:
                selected_best_fit = random.sample(best_fit_blocks, n_best_fit)
            else:
                selected_best_fit = best_fit_blocks.copy()
            
            # Add selected best fit blocks
            blocks.extend(selected_best_fit)
            
            # Add random blocks to complete the count
            if len(blocks) < count:
                # Exclude shape IDs of best fit blocks AND game over blocks from random selection
                best_fit_shape_ids = [b.shape_id for b in best_fit_blocks if hasattr(b, 'shape_id')]
                excluded_shapes = best_fit_shape_ids + game_over_shape_ids
                random_blocks = self._select_random_blocks(count - len(blocks), excluded_shapes)
                blocks.extend(random_blocks)
        else:
            # Generate all random blocks, excluding game over blocks
            blocks = self._select_random_blocks(count, game_over_shape_ids)
        
        # Ensure we have exactly the required count
        if len(blocks) > count:
            blocks = blocks[:count]
        
        # Shuffle to avoid predictable patterns
        random.shuffle(blocks)
        return blocks
    
    def _generate_blocks_above_threshold(self, game_over_blocks: List[Block], count: int) -> List[Block]:
        """Generate blocks when score is above threshold.
        
        Args:
            game_over_blocks: List of blocks that cannot fit on the board
            count: Number of blocks to generate (always 3)
            
        Returns:
            List[Block]: Generated blocks
        """
        blocks = []
        
        # Check if we have game over blocks
        if game_over_blocks:
            # Include 1 game over block in the tray
            game_over_block = random.choice(game_over_blocks)
            blocks.append(game_over_block)
            
            # Add random blocks to complete the count (excluding game over blocks)
            excluded_shapes = [b.shape_id for b in game_over_blocks if hasattr(b, 'shape_id')]
            random_blocks = self._select_random_blocks(count - len(blocks), excluded_shapes)
            blocks.extend(random_blocks)
        else:
            # If no game over blocks, generate all random blocks
            blocks = self._select_random_blocks(count)
        
        # Ensure we have exactly the required count
        if len(blocks) > count:
            blocks = blocks[:count]
        
        # Shuffle to avoid predictable patterns
        random.shuffle(blocks)
        return blocks
    
    def _select_random_blocks(self, count: int, excluded_shapes: Optional[List[str]] = None) -> List[Block]:
        """Select random blocks with optional exclusions based on shape weights.
        
        Args:
            count: Number of blocks to select
            excluded_shapes: List of shape IDs to exclude
            
        Returns:
            List[Block]: List of random blocks
        """
        if excluded_shapes is None:
            excluded_shapes = []
        
        # Create a set of excluded shapes for faster lookups
        excluded_set = set(excluded_shapes)
        
        # Filter available shapes and their corresponding weights
        available_shapes = []
        available_weights = []
        
        for i, shape_id in enumerate(self.shape_names):
            if shape_id not in excluded_set:
                available_shapes.append(shape_id)
                available_weights.append(self.weights[i] if i < len(self.weights) else 1)
        
        # If no shapes available after exclusions, use all shapes
        if not available_shapes:
            available_shapes = self.shape_names
            available_weights = self.weights if len(self.weights) == len(self.shape_names) else [1] * len(self.shape_names)
        
        # If we don't have enough weights, use uniform weights
        if len(available_weights) < len(available_shapes):
            available_weights = [1] * len(available_shapes)
        
        # Select random shapes based on weights
        try:
            selected_shape_ids = random.choices(available_shapes, weights=available_weights, k=count)
        except ValueError:
            # Fallback to uniform selection if weights cause an error
            selected_shape_ids = random.choices(available_shapes, k=count)
        
        # Create blocks from the selected shape IDs
        blocks = []
        for shape_id in selected_shape_ids:
            shape_data = self.shapes[shape_id]
            block = Block(shape_id, shape_data)
            blocks.append(block)
        
        return blocks
