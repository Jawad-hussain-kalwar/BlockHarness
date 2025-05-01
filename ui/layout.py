# ui/layout.py
"""
Layout constants for the BlockHarness UI.

The UI is divided into four main sections:
1. DDA Section (left): 372px width
2. Simulation Section (middle-left): 372px width
3. Game Section (middle-right): 754px width
4. Game State Section (right): 372px width

The Game Section is further divided into:
- Stats View (top): 100px height with three stat boxes
- Game Board (middle): 640x640px with 57px padding on sides
- Preview View (bottom): Contains three 160x160px preview blocks
"""

# Window dimensions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 992
PADDING = 10           # space between sections and window edges

# Content dimensions
CONTENT_HEIGHT = WINDOW_HEIGHT - 2 * PADDING  # 972

# Section dimensions
DDA_WIDTH = 372
SIM_WIDTH = 372
GAME_WIDTH = 754
STATE_WIDTH = 372
SECTION_HEIGHT = CONTENT_HEIGHT  # 972

# Game section subdivisions
# Stats view
STATS_HEIGHT = 100
STATS_BOX_WIDTH = 238
STATS_BOX_HEIGHT = 80

# Hints view
HINTS_HEIGHT = 40  # height reserved for hint legend between stats and board
HINTS_PADDING = PADDING  # horizontal padding for hint text

# Game board
BOARD_SIZE = 640
BOARD_PADDING_W = (GAME_WIDTH - BOARD_SIZE) // 2  # 57 px
CELL_RADIUS = 10

# Preview view
PREVIEW_HEIGHT = CONTENT_HEIGHT - STATS_HEIGHT - HINTS_HEIGHT - BOARD_SIZE  # adjusted for hints
PREVIEW_BLOCK = 160
PREVIEW_CELL_RADIUS = 5
PREVIEW_PADDING_V = (PREVIEW_HEIGHT - PREVIEW_BLOCK) // 2   # 36 px
PREVIEW_PADDING_H = BOARD_PADDING_W                         # 57 px
PREVIEW_GAP = 80  # horizontal gap between preview blocks

# Legacy constants - keeping for backward compatibility
SIDEBAR_WIDTH      = 560  # Doubled from 280
SIDEBAR_PADDING    = 16
FIELD_HEIGHT       = 32
FIELD_SPACING      = 10
SECTION_SPACING    = 24
LABEL_SPACING      = 8
BORDER_RADIUS      = 4
SECTION_WIDTH      = (SIDEBAR_WIDTH - (SIDEBAR_PADDING * 3)) // 2  # Width for each section
