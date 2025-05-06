from typing import Dict, List, Optional, Tuple, Any
import random
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry
from engine.block import Block


class OpportunityDDA(BaseDDAAlgorithm):
    """DDA algorithm that adjusts difficulty based on best-fit blocks and game-over opportunities."""
    
    display_name = "Opportunity Adaptive"
    
    def __init__(self):
        """Initialize the best-fit DDA algorithm."""
        self.tray_counter = 0  # Counter to keep track of tray refills
        self.L = 1  # Frequency of best-fit block generation (1-3)
        self.score_threshold = 1000  # Score threshold for game-over opportunity
        self.low_clear_rate = 0.5  # Lower bound for clear rate
        self.high_clear_rate = 0.8  # Upper bound for clear rate
        self.n_best_fit_blocks = 1  # Number of best fit blocks to generate
        self.n_game_over_blocks = 1  # Number of game over blocks to generate
    
    def initialize(self, config_params: Dict[str, Any]) -> None:
        """Initialize algorithm with configuration parameters."""
        params = config_params.get("opportunity_dda", {})
        
        # Get best-fit parameters from configuration
        self.low_clear_rate = params.get("low_clear_rate", 0.5)
        self.high_clear_rate = params.get("high_clear_rate", 0.8)
        self.score_threshold = params.get("score_threshold", 1000)
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
        
        # Check for game-over opportunity with score threshold
        if opportunity and score >= self.score_threshold:
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
    
    def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
        """Get the next blocks based on the best-fit strategy.
        
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
        
        # Initialize list of blocks to generate
        blocks = []
        
        # Game over opportunity with score threshold
        if opportunity and score >= self.score_threshold:
            # Include game-over block if it exists
            if game_over_block != "None" and game_over_block in shape_names:
                game_over_shape = shapes_dict[game_over_block]
                
                # Add n_game_over_blocks instances of the game over block
                for _ in range(min(self.n_game_over_blocks, count)):
                    blocks.append(Block(game_over_shape))
                
                # Fill the rest with random shapes
                remaining_shapes = [s for s in shape_names if s != game_over_block]
                for _ in range(count - min(self.n_game_over_blocks, count)):
                    if remaining_shapes:
                        random_shape_name = random.choice(remaining_shapes)
                        blocks.append(Block(shapes_dict[random_shape_name]))
                    else:
                        # Fallback if no other shapes available
                        blocks.append(Block(game_over_shape))
            else:
                # If no game-over block, generate random blocks
                for _ in range(count):
                    random_shape_name = random.choice(shape_names)
                    blocks.append(Block(shapes_dict[random_shape_name]))
        else:
            # Update L based on clear rate
            if clear_rate >= self.high_clear_rate:
                self.L = 3
            elif clear_rate >= self.low_clear_rate:
                self.L = 2
            else:
                self.L = 1
            
            # Check if it's time to include a best-fit block
            if best_fit_block != "None" and self.tray_counter % self.L == 0:
                # Include a best-fit block if it exists
                if best_fit_block in shape_names:
                    best_fit_shape = shapes_dict[best_fit_block]
                    
                    # Add n_best_fit_blocks instances of the best fit block
                    for _ in range(min(self.n_best_fit_blocks, count)):
                        blocks.append(Block(best_fit_shape))
                    
                    # Fill the rest with random shapes
                    remaining_shapes = [s for s in shape_names if s != best_fit_block]
                    for _ in range(count - min(self.n_best_fit_blocks, count)):
                        if remaining_shapes:
                            random_shape_name = random.choice(remaining_shapes)
                            blocks.append(Block(shapes_dict[random_shape_name]))
                        else:
                            # Fallback if no other shapes available
                            random_shape_name = random.choice(shape_names)
                            blocks.append(Block(shapes_dict[random_shape_name]))
                else:
                    # If best-fit block not found, generate random blocks
                    for _ in range(count):
                        random_shape_name = random.choice(shape_names)
                        blocks.append(Block(shapes_dict[random_shape_name]))
            else:
                # Generate random blocks
                for _ in range(count):
                    random_shape_name = random.choice(shape_names)
                    blocks.append(Block(shapes_dict[random_shape_name]))
        
        return blocks

# Register the best-fit DDA algorithm
registry.register(OpportunityDDA) 