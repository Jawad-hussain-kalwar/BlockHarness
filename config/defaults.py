# config/defaults.py
from shapes import SHAPES

# Default configuration (same as in simulator.py)
CONFIG = {
    "shapes": SHAPES,
    "shape_weights": [2, 2, 2, 2, 1, 1, 1, 1],           # initial bias
    "difficulty_thresholds": [
        (1000, [1, 2, 2, 2, 2, 2, 2, 3]),                # harder
        (3000, [1, 1, 2, 3, 3, 3, 3, 4]),                # hardest
    ],
} 