# engine/shapes.py
# 41 shapes in total, Exactly as in the original game

SHAPES = {
   "1x1-square"  : [(0,0)],                                              # Square
   "1x2-line"    : [(0,0),(0,1)],                                        # 1x2 Horizontal Line
   "2x1-line"    : [(0,0),(1,0)],                                        # 2x1 vertical line
   "1x3-line"    : [(0,0),(0,1),(0,2)],                                  # 1x3 horizontal line
   "3x1-line"    : [(0,0),(1,0),(2,0)],                                  # 3x1 vertical line
   "1x4-line"    : [(0,0),(0,1),(0,2),(0,3)],                            # 1x4 horizontal line
   "4x1-line"    : [(0,0),(1,0),(2,0),(3,0)],                            # 4x1 vertical line
   "1x5-line"    : [(0,0),(0,1),(0,2),(0,3),(0,4)],                      # 1x5 horizontal line
   "5x1-line"    : [(0,0),(1,0),(2,0),(3,0),(4,0)],                      # 5x1 Vertical Line
   "2x2-square"  : [(0,0),(0,1),(1,0),(1,1)],                            # 2x2 Square
   "2x3-rect"    : [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)],                # 2x3 Rectangle
   "3x2-rect"    : [(0,0),(0,1),(1,0),(1,1),(2,0),(2,1)],                # 3x2 Rectangle
   "3x3-square"  : [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)], # 3x3 Square
   "2x2-L-tl"    : [(0,0),(0,1),(1,0)],                                  # 2x2 L-shape at top-left
   "2x2-L-tr"    : [(0,0),(0,1),(1,1)],                                  # 2x2 L-shape at top-right
   "2x2-L-bl"    : [(0,0),(1,0),(1,1)],                                  # 2x2 L-shape at bottom-left
   "2x2-L-br"    : [(0,1),(1,0),(1,1)],                                  # 2x2 L-shape at bottom-right
   "2x3-L-tl"    : [(0,0),(0,1),(0,2),(1,0)],                            # 2x3 L-shape at top-left
   "2x3-L-tr"    : [(0,0),(0,1),(0,2),(1,2)],                            # 2x3 L-shape at top-right
   "2x3-L-bl"    : [(0,0),(1,0),(1,1),(1,2)],                            # 2x3 L-shape at bottom-left
   "2x3-L-br"    : [(0,2),(1,0),(1,1),(1,2)],                            # 2x3 L-shape at bottom-right
   "3x2-L-tl"    : [(0,0),(0,1),(1,0),(2,0)],                            # 3x2 L-shape at top-left
   "3x2-L-tr"    : [(0,1),(1,1),(2,0),(2,1)],                            # 3x2 L-shape at top-right
   "3x2-L-bl"    : [(0,0),(1,0),(2,0),(2,1)],                            # 3x2 L-shape at bottom-left
   "3x2-L-br"    : [(0,0),(0,1),(1,1),(2,1)],                            # 3x2 L-shape at bottom-right (fixed coordinates)
   "3x3-L-tl"    : [(0,0),(0,1),(0,2),(1,0),(2,0)],                      # 3x3 L-shape at top-left
   "3x3-L-tr"    : [(0,0),(0,1),(0,2),(1,2),(2,2)],                      # 3x3 L-shape at top-right
   "3x3-L-bl"    : [(0,0),(1,0),(2,0),(2,1),(2,2)],                      # 3x3 L-shape at bottom-left
   "3x3-L-br"    : [(0,2),(1,2),(2,0),(2,1),(2,2)],                      # 3x3 L-shape at bottom-right
   "2x3-S"       : [(0,1),(0,2),(1,0),(1,1)],                            # 2x3 S-shape (like Tetris S)
   "3x2-S"       : [(0,0),(1,0),(1,1),(2,1)],                            # 3x2 rotated S
   "2x3-Z"       : [(0,0),(0,1),(1,1),(1,2)],                            # 2x3 Z-shape (like Tetris Z)
   "3x2-Z"       : [(0,1),(1,0),(1,1),(2,0)],                            # 3x2 rotated Z
   "2x3-T"       : [(0,1),(1,0),(1,1),(1,2)],                            # 2x3 T-shape
   "2x3-T-U"     : [(0,0),(0,1),(0,2),(1,1)],                            # 2x3 Upside Down T
   "3x2-T-C"     : [(0,0),(1,0),(1,1),(2,0)],                            # 3x2 clock-wise rotated T
   "3x2-T-CC"    : [(0,1),(1,0),(1,1),(2,1)],                            # 3x2 Counter-clockwise rotated T
   "3x3-Diag"    : [(0,0),(1,1),(2,2)],                                  # 3x3 long diagonal
   "3x3-Diag-b"  : [(0,2),(1,1),(2,0)],                                  # 3x3 Long Diagonal Back
   "2x2-Diag"    : [(0,0),(1,1)],                                        # 2x2 diagonal
   "2x2-Diag-b"  : [(0,1),(1,0)],                                        # 2x2 back diagonal
}