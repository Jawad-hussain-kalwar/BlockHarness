# engine/shapes.py
# Eight example shapes (feel free to expand)
SHAPES = [
    [(0, 0)],                                   # single
    [(0, 0), (0, 1)],                           # 1×2
    [(0, 0), (0, 1), (1, 0), (1, 1)],           # 2×2 square
    [(0, 0), (1, 0), (2, 0)],                   # 3×1 line
    [(0, 0), (1, 0), (1, 1)],                   # L-shape
    [(0, 0), (1, 0), (1, 1), (1, 2)],           # long L-shape
    [(0, 1), (1, 0), (1, 1), (1, 2)],           # T-shape
    [(0, 0), (0, 1), (1, 1), (1, 2)],           # Snake line
    ]
