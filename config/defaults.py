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
        ]
    }
} 