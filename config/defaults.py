# config/defaults.py
from engine.shapes import SHAPES

# Get the number of shapes in the dictionary
SHAPE_COUNT = len(SHAPES)

# Enumeration       [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41]
DEFAULT_WEIGHTS =   [1,5,5,5,5,5,5,5,5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1], # initial bias with appropriate length

# Default configuration
CONFIG = {
    "shapes": SHAPES,
    
    "dda_params": {                            # algorithm-specific parameters
            "dda": {
            "low_clear_rate":       0.5,                   # Threshold for L=1
            "high_clear_rate":      0.8,                  # Threshold for L=3
            "n_best_fit_blocks":    1,                  # Number of best fit blocks to preview out of 3
            "score_threshold":      100,                  # Score threshold for game-over opportunity
            "n_game_over_blocks":   1                  # Number of best fit blocks to preview out of 3
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