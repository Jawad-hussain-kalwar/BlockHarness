# config/defaults.py
from engine.shapes import SHAPES

# Default configuration (same as in simulator.py)
CONFIG = {
    "shapes": SHAPES,
    "shape_weights": [2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0],           # initial bias
    "difficulty_thresholds": [
        (1000, [1, 2, 2, 2, 2, 2, 2, 3, 1, 1, 1]),                # harder
        (3000, [1, 1, 2, 3, 3, 3, 3, 4, 2, 2, 2]),                # hardest
    ],
    "dda_algorithm": "ThresholdDDA",                              # default DDA algorithm
    "dda_params": {                                               # algorithm-specific parameters
        "thresholds": [
            (1000, [1, 2, 2, 2, 2, 2, 2, 3, 1, 1, 1]),            # harder
            (3000, [1, 1, 2, 3, 3, 3, 3, 4, 2, 2, 2]),            # hardest
        ],
        "metrics_dda": {
            "initial_difficulty": 3,                              # Starting difficulty (1-10)
            "low_clear": 0.30,                                    # From existing metrics_flow
            "high_clear": 0.70,                                   # From existing metrics_flow
            "danger_cut": 0.80,                                   # From existing metrics_flow
            "rescue_shape_weights": [10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Weights for rescue mode
            "size_caps": [3, 3, 3, 4, 4, 4, 5, 5, 5, 5]           # Max shape size per difficulty level
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