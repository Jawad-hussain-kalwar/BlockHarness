# config/defaults.py
from engine.shapes import SHAPES

# Get the number of shapes in the dictionary
SHAPE_COUNT = len(SHAPES)

# Create weight arrays with appropriate length
DEFAULT_WEIGHTS = [0] * SHAPE_COUNT
# Set weights for simple shapes (first ~10 shapes)
for i in range(min(10, SHAPE_COUNT)):
    DEFAULT_WEIGHTS[i] = 2 if i < 4 else 1
    
# Create difficulty threshold weights
HARDER_WEIGHTS = [0] * SHAPE_COUNT
HARDEST_WEIGHTS = [0] * SHAPE_COUNT
# Set weights for harder difficulty
for i in range(min(10, SHAPE_COUNT)):
    HARDER_WEIGHTS[i] = 1 if i == 0 else (3 if i == 7 else (1 if i >= 8 else 2))
    HARDEST_WEIGHTS[i] = 1 if i <= 1 else (4 if i == 7 else (2 if i >= 8 else 3))

# Rescue weights for emergency situations
RESCUE_WEIGHTS = [0] * SHAPE_COUNT
if SHAPE_COUNT > 0:
    RESCUE_WEIGHTS[0] = 10  # Very high weight for simplest shape
if SHAPE_COUNT > 1:
    RESCUE_WEIGHTS[1] = 8   # High weight for second shape
    
# Default configuration
CONFIG = {
    "shapes": SHAPES,
    "shape_weights": DEFAULT_WEIGHTS,           # initial bias with appropriate length
    "difficulty_thresholds": [
        (1000, HARDER_WEIGHTS),                # harder
        (3000, HARDEST_WEIGHTS),               # hardest
    ],
    "dda_algorithm": "MetricsDDA",           # default DDA algorithm
    "dda_params": {                            # algorithm-specific parameters
        "thresholds": [
            (1000, HARDER_WEIGHTS),            # harder
            (3000, HARDEST_WEIGHTS),           # hardest
        ],
        "metrics_dda": {
            "initial_difficulty": 3,                 # Starting difficulty (1-10)
            "low_clear": 0.30,                       # From existing metrics_flow
            "high_clear": 0.70,                      # From existing metrics_flow
            "danger_cut": 0.80,                      # From existing metrics_flow
            "rescue_shape_weights": RESCUE_WEIGHTS,  # Weights for rescue mode
            "size_caps": [3, 3, 3, 4, 4, 4, 5, 5, 5, 5]  # Max shape size per difficulty level
        },
        "opportunity_dda": {
            "low_clear_rate": 0.5,                   # Threshold for L=1
            "high_clear_rate": 0.8,                  # Threshold for L=3
            "n_best_fit_blocks": 1,                  # Number of best fit blocks to preview out of 3
            "score_threshold": 1000,                  # Score threshold for game-over opportunity
            "n_game_over_blocks": 1                  # Number of best fit blocks to preview out of 3
        }
    },
    # Metrics configuration
    "board_size": 8,                                              # cols, rows
    # weights for danger score calculation:
    "metrics_weights": {
        "occupancy": 0.50,                                        # weight for occupancy ratio
        "fragmentation": 0.30,                                    # weight for fragmentation count
        "inv_largest": 0.20,                                      # weight for inverse largest empty region
    },
    # flow parameters for performance evaluation:
    "metrics_flow": {
        "low_clear": 0.30,                                        # threshold for "Hard" difficulty
        "high_clear": 0.70,                                       # threshold for "Easy" difficulty
        "danger_cut": 0.80,                                       # threshold for danger warning
    },
    # timing parameters:
    "metrics_timing": {
        "max_time_per_move": 8.0,                                 # seconds
    },
    # Configuration for which metrics are displayed in the state section
    "viewable_metrics": {
        # Game Analysis Metrics
        "best_fit_block": True,
        "opportunity": True,
        "game_over_block": True,
        
        # Game State Metrics
        "imminent_threat": True,
        "occupancy_ratio": True,
        "fragmentation_count": True,
        "largest_empty_region": True,
        "danger_score": False,
        "phase": False,
        
        # Player State Metrics
        "move_count": True,
        "lines_cleared": True,
        "score": True,
        "clear_rate": True,
        "recent_clears": True,  # History of recent line clears
        "perf_band": False,
        "player_level": False,
        "emotional_state": False,
        "placement_efficiency": False,  # Efficiency of block placements
        
        # Timing Metrics
        "time_per_move": False,
        "avg_time_per_move": False,
        
        # Mistake Metrics
        "mistake_flag": False,
        "mistake_count": False,
        "mistake_rate": False,
        "mistake_sw": False
    }
} 