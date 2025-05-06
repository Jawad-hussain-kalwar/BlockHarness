from typing import Dict, List, Optional, Tuple, Any
import random
from engine.block import Block


class DDA:
    """Dynamic Difficulty Adjustment algorithm that adjusts difficulty based on best-fit blocks and game-over opportunities."""
    
    def __init__(self):
        """Initialize the DDA algorithm."""
        self.tray_counter = 0  # Counter to keep track of tray refills
        self.L = 1  # Frequency of best-fit block generation (1-3)
        self.score_threshold = 100  # Score threshold for game-over opportunity
        self.low_clear_rate = 0.5  # Lower bound for clear rate
        self.high_clear_rate = 0.8  # Upper bound for clear rate
        self.n_best_fit_blocks = 1  # Number of best fit blocks to generate
        self.n_game_over_blocks = 1  # Number of game over blocks to generate
    
    def initialize(self, config_params: Dict[str, Any]) -> None:
        """Initialize algorithm with configuration parameters."""
        params = config_params.get("dda", {})
        
        # Get best-fit parameters from configuration
        self.low_clear_rate = params.get("low_clear_rate", 0.5)
        self.high_clear_rate = params.get("high_clear_rate", 0.8)
        self.score_threshold = params.get("score_threshold", 100)
        self.n_best_fit_blocks = params.get("n_best_fit_blocks", 1)
        self.n_game_over_blocks = params.get("n_game_over_blocks", 1)
        
        # Get flow parameters from global metrics config if not specified
        metrics_flow = config_params.get("metrics_flow", {})
        if not params.get("low_clear_rate"):
            self.low_clear_rate = metrics_flow.get("low_clear", 0.3)
        if not params.get("high_clear_rate"):
            self.high_clear_rate = metrics_flow.get("high_clear", 0.7)
    
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed."""
        # Get all metrics from the engine
        metrics = engine_state.get_metrics()
        
        # Increment tray counter since this is called when generating a new tray
        self.tray_counter += 1
        
        # Get shape count for weights array length
        shape_count = len(engine_state.config["shapes"])
        
        # Default weights (all equal)
        default_weights = [1] * shape_count
        
        # Get relevant metrics
        best_fit_block = metrics.get("best_fit_block", "None")
        opportunity = metrics.get("opportunity", False)
        game_over_block = metrics.get("game_over_block", "None")
        score = metrics.get("score", 0)
        
        # Calculate clear rate safely
        move_count = metrics.get("move_count", 0)
        lines_cleared = metrics.get("lines_cleared", 0)
        clear_rate = lines_cleared / max(1, move_count)  # Avoid division by zero
        
        # Update L based on clear rate
        if clear_rate >= self.high_clear_rate:
            self.L = 3
        elif clear_rate >= self.low_clear_rate:
            self.L = 2
        else:
            self.L = 1
        
        # Only consider game-over opportunity if score threshold is reached
        if opportunity and score >= self.score_threshold and game_over_block != "None":
            # Game over mode - generate game-over block and no fitting blocks
            return self._get_game_over_weights(engine_state, game_over_block)
        
        # Otherwise, use L-based best-fit generation
        if best_fit_block != "None" and self.tray_counter % self.L == 0:
            # It's time to include a best-fit block
            return self._get_best_fit_weights(engine_state, best_fit_block)
        
        # No special adjustment needed, use default weights
        return default_weights
    
    def _get_game_over_weights(self, engine_state, game_over_block: str) -> List[int]:
        """Get weights to generate a game-over block."""
        # Get shapes from configuration
        shapes_dict = engine_state.config["shapes"]
        shape_names = list(shapes_dict.keys())
        
        # Create a weights array with zeros
        weights = [0] * len(shape_names)
        
        # Set weight for game-over block
        if game_over_block in shape_names:
            game_over_index = shape_names.index(game_over_block)
            weights[game_over_index] = 10  # High weight for game-over block
        
        # If no game-over block found, use random weights
        if sum(weights) == 0:
            weights = [1] * len(shape_names)
        
        return weights
    
    def _get_best_fit_weights(self, engine_state, best_fit_block: str) -> List[int]:
        """Get weights to include a best-fit block in the tray."""
        # Get shapes from configuration
        shapes_dict = engine_state.config["shapes"]
        shape_names = list(shapes_dict.keys())
        
        # Create a weights array with equal weights
        weights = [1] * len(shape_names)
        
        # Set higher weight for best-fit block
        if best_fit_block in shape_names:
            best_fit_index = shape_names.index(best_fit_block)
            weights[best_fit_index] = 5  # Higher weight for best-fit block
        
        return weights
    
    def _select_distinct_blocks(self, shape_names: List[str], shapes_dict: Dict[str, List[Tuple[int, int]]], 
                               count: int, bias_shape: str = None, bias_weight: int = 5) -> List[Block]:
        """Select 'count' distinct block types, with optional bias toward a specific shape.
        
        Args:
            shape_names: List of available shape names
            shapes_dict: Dictionary mapping shape names to shape definitions
            count: Number of blocks to generate
            bias_shape: Optional shape to favor in selection
            bias_weight: Weight to give the bias_shape
            
        Returns:
            List[Block]: List of distinct blocks
        """
        if len(shape_names) < count:
            # Not enough distinct shapes available, will need duplicates
            return [Block(shapes_dict[random.choice(shape_names)]) for _ in range(count)]
        
        # Create a copy of shape_names to avoid modifying the original
        available_shapes = shape_names.copy()
        selected_blocks = []
        
        # If we have a bias shape and it's in our available shapes, try to include it first
        if bias_shape and bias_shape in available_shapes and random.random() < 0.8:  # 80% chance
            selected_blocks.append(Block(shapes_dict[bias_shape]))
            available_shapes.remove(bias_shape)
            count -= 1
        
        # Randomly select the remaining distinct shapes
        selected_shape_names = random.sample(available_shapes, count)
        for name in selected_shape_names:
            selected_blocks.append(Block(shapes_dict[name]))
            
        # Shuffle the blocks to avoid predictable placement
        random.shuffle(selected_blocks)
        
        return selected_blocks
    
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Get the next blocks based on the best-fit strategy with distinct blocks.
        
        Args:
            engine_state: The current game engine state
            count: Number of blocks to generate
            
        Returns:
            List[Block]: The specific blocks to be spawned
        """
        # Get all metrics from the engine
        metrics = engine_state.get_metrics()
        
        # Get shapes from configuration
        shapes_dict = engine_state.config["shapes"]
        shape_names = list(shapes_dict.keys())
        
        # Get relevant metrics
        best_fit_block = metrics.get("best_fit_block", "None")
        opportunity = metrics.get("opportunity", False)
        game_over_block = metrics.get("game_over_block", "None")
        score = metrics.get("score", 0)
        
        # Calculate clear rate safely
        move_count = metrics.get("move_count", 0)
        lines_cleared = metrics.get("lines_cleared", 0)
        clear_rate = lines_cleared / max(1, move_count)  # Avoid division by zero
        
        # Game over opportunity with score threshold
        if opportunity and score >= self.score_threshold and game_over_block != "None":
            # Check if game over block exists in shapes
            if game_over_block in shape_names:
                # Generate blocks with game over block bias
                return self._select_distinct_blocks(
                    shape_names, shapes_dict, count, 
                    bias_shape=game_over_block, bias_weight=10
                )
        
        # Update L based on clear rate
        if clear_rate >= self.high_clear_rate:
            self.L = 3
        elif clear_rate >= self.low_clear_rate:
            self.L = 2
        else:
            self.L = 1
        
        # Check if it's time to include a best-fit block
        if best_fit_block != "None" and best_fit_block in shape_names and self.tray_counter % self.L == 0:
            # Generate blocks with best fit block bias
            return self._select_distinct_blocks(
                shape_names, shapes_dict, count,
                bias_shape=best_fit_block, bias_weight=5
            )
        
        # Generate fully random distinct blocks
        return self._select_distinct_blocks(shape_names, shapes_dict, count)
