# engine/block_pool.py
import random
from typing import Dict, List, Tuple, Any
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
        self.last_generated_blocks = []  # Keep track of recently generated blocks
        
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

    def get_block(self) -> Block:
        """Sample a random block based on shape weights.
        
        Returns:
            Block: A new block with randomly selected shape
        """
        if not self.shape_names:
            raise ValueError("[engine/block_pool.py] No shapes available in the block pool")
            
        try:
            shape_name = random.choices(self.shape_names, weights=self.weights, k=1)[0]
        except (ValueError, KeyError) as e:
            # Fallback to uniform selection if weights cause an error
            print(f"[engine/block_pool.py] Warning: Error in weighted selection ({e}), falling back to uniform selection")
            shape_name = random.choice(self.shape_names)
            
        shape = self.shapes[shape_name]
        return Block(shape)

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
        game_over_block = metrics.get("game_over_block", "None")
        score = metrics.get("score", 0)
        clear_rate = metrics.get("clear_rate", 0.0)
        
        # Update L based on clear rate
        self._update_L_value(clear_rate)
        
        # Generate blocks based on conditions
        blocks = []
        
        if score < self.score_threshold:
            blocks = self._generate_blocks_below_threshold(best_fit_block, count, clear_rate)
        else:
            blocks = self._generate_blocks_above_threshold(game_over_block, opportunity, count)
        
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
    
    def _generate_blocks_below_threshold(self, best_fit_block: str, count: int, clear_rate: float) -> List[Block]:
        """Generate blocks when score is below threshold.
        
        Args:
            best_fit_block: Name of the best fit block
            count: Number of blocks to generate
            clear_rate: Current line clear rate
            
        Returns:
            List[Block]: Generated blocks
        """
        blocks = []
        
        if clear_rate < self.low_clear_rate:
            # Low clear rate: Generate n best fit blocks and random blocks
            if best_fit_block != "None" and best_fit_block in self.shape_names:
                # Add best fit blocks
                for _ in range(min(self.n_best_fit_blocks, count)):
                    blocks.append(Block(self.shapes[best_fit_block]))
                
                # Add random blocks to complete the count
                excluded_shapes = [best_fit_block]
                random_blocks = self._select_distinct_blocks(count - len(blocks), excluded_shapes)
                blocks.extend(random_blocks)
            else:
                # If no best fit block, generate all random blocks
                blocks = self._select_distinct_blocks(count)
                
        elif clear_rate < self.high_clear_rate:
            # Medium clear rate: Every 2nd tray has best fit blocks
            if self.tray_counter % 2 == 0 and best_fit_block != "None" and best_fit_block in self.shape_names:
                # Add best fit blocks
                for _ in range(min(self.n_best_fit_blocks, count)):
                    blocks.append(Block(self.shapes[best_fit_block]))
                
                # Add random blocks to complete the count
                excluded_shapes = [best_fit_block]
                random_blocks = self._select_distinct_blocks(count - len(blocks), excluded_shapes)
                blocks.extend(random_blocks)
            else:
                # First tray or non-best-fit tray: all random blocks
                blocks = self._select_distinct_blocks(count)
                
        else:
            # High clear rate: Every 3rd tray has best fit blocks
            if self.tray_counter % 3 == 0 and best_fit_block != "None" and best_fit_block in self.shape_names:
                # Add best fit blocks
                for _ in range(min(self.n_best_fit_blocks, count)):
                    blocks.append(Block(self.shapes[best_fit_block]))
                
                # Add random blocks to complete the count
                excluded_shapes = [best_fit_block]
                random_blocks = self._select_distinct_blocks(count - len(blocks), excluded_shapes)
                blocks.extend(random_blocks)
            else:
                # Not a best-fit tray: all random blocks
                blocks = self._select_distinct_blocks(count)
        
        # Shuffle to avoid predictable patterns
        random.shuffle(blocks)
        return blocks
    
    def _generate_blocks_above_threshold(self, game_over_block: str, opportunity: bool, count: int) -> List[Block]:
        """Generate blocks when score is above threshold.
        
        Args:
            game_over_block: Name of the game over block
            opportunity: Whether there's a game over opportunity
            count: Number of blocks to generate
            
        Returns:
            List[Block]: Generated blocks
        """
        blocks = []
        
        # Generate game over blocks if opportunity exists
        if opportunity and game_over_block != "None" and game_over_block in self.shape_names:
            # Add game over blocks
            for _ in range(min(self.n_game_over_blocks, count)):
                blocks.append(Block(self.shapes[game_over_block]))
            
            # Add random blocks to complete the count
            excluded_shapes = [game_over_block]
            random_blocks = self._select_distinct_blocks(count - len(blocks), excluded_shapes)
            blocks.extend(random_blocks)
        else:
            # If no game over opportunity, generate all random blocks
            blocks = self._select_distinct_blocks(count)
        
        # Shuffle to avoid predictable patterns
        random.shuffle(blocks)
        return blocks
    
    def _select_distinct_blocks(self, count: int, excluded_shapes: List[str] = None) -> List[Block]:
        """Select distinct blocks with optional exclusions.
        
        Args:
            count: Number of blocks to select
            excluded_shapes: List of shape names to exclude
            
        Returns:
            List[Block]: List of distinct blocks
        """
        if excluded_shapes is None:
            excluded_shapes = []
        
        # Get all available shapes, excluding the specified ones
        available_shapes = [s for s in self.shape_names if s not in excluded_shapes]
        
        # Also exclude recently generated blocks to increase variety
        available_shapes = [s for s in available_shapes if s not in self.last_generated_blocks]
        
        # If too many exclusions, fall back to all shapes except excluded ones
        if len(available_shapes) < count:
            available_shapes = [s for s in self.shape_names if s not in excluded_shapes]
        
        # If still not enough shapes, just use what we have with potential duplicates
        if len(available_shapes) < count:
            selected_blocks = []
            for _ in range(count):
                if available_shapes:
                    shape_name = random.choice(available_shapes)
                    selected_blocks.append(Block(self.shapes[shape_name]))
                else:
                    # Ultimate fallback: use any shape
                    shape_name = random.choice(self.shape_names)
                    selected_blocks.append(Block(self.shapes[shape_name]))
        else:
            # Enough distinct shapes available
            selected_shape_names = random.sample(available_shapes, count)
            selected_blocks = [Block(self.shapes[name]) for name in selected_shape_names]
        
        return selected_blocks
