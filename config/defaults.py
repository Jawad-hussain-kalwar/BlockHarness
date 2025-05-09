# config/defaults.py
from engine.shapes import SHAPES

# Get the number of shapes in the dictionary
SHAPE_COUNT = len(SHAPES)
    
DEFAULT_WEIGHTS =[1,    # Single cell Square
   5,    # 1x2 Horizontal Line
   5,    # 2x1 vertical line
   5,    # 1x3 horizontal line
   5,    # 3x1 vertical line
   5,    # 1x4 horizontal line
   5,    # 4x1 vertical line
   5,    # 1x5 horizontal line
   5,    # 5x1 Vertical Line

   5,    # 2x2 Square
   5,    # 2x3 Rectangle
   5,    # 3x2 Rectangle
   5,    # 3x3 Square

   5,    # 2x2 L-shape at top-left
   5,    # 2x2 L-shape at top-right
   5,    # 2x2 L-shape at bottom-left
   5,    # 2x2 L-shape at bottom-right

   5,    # 2x3 L-shape at top-left
   5,    # 2x3 L-shape at top-right
   5,    # 2x3 L-shape at bottom-left
   5,    # 2x3 L-shape at bottom-right

   5,    # 3x2 L-shape at top-left
   5,    # 3x2 L-shape at top-right
   5,    # 3x2 L-shape at bottom-left
   5,    # 3x2 L-shape at bottom-right

   3,    # 3x3 L-shape at top-left
   3,    # 3x3 L-shape at top-right
   3,    # 3x3 L-shape at bottom-left
   3,    # 3x3 L-shape at bottom-right

   5,    # 2x3 S-shape (like Tetris S)
   5,    # 3x2 rotated S

   5,    # 2x3 Z-shape (like Tetris Z)
   5,    # 3x2 rotated Z

   5,    # 2x3 T-shape
   5,    # 2x3 Upside Down T
   5,    # 3x2 clock-wise rotated T
   5,    # 3x2 Counter-clockwise rotated T

   2,    # 3x3 long diagonal
   2,    # 3x3 Long Diagonal Back

   2,    # 2x2 diagonal
   2,    # 2x2 back diagonal
]

SIMULATION_CONFIG = {
    "default_player": "Greedy",
    "steps_per_second": 0, # max possible or infinite
    "number_of_runs": 10
}

# Default configuration
CONFIG = {
    "shapes": SHAPES,
    
    "dda_params": {                            # algorithm-specific parameters
            "dda": {
            "low_clear_rate":       0.5,                   # Threshold for L=1
            "high_clear_rate":      0.8,                  # Threshold for L=3
            "n_best_fit_blocks":    1,                      # Number of best fit blocks to preview out of 3
            "score_threshold":      99999,                  # Score threshold for game-over opportunity
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

    }