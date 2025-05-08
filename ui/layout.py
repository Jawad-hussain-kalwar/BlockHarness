# ui/layout.py
"""
Layout constants for the BlockHarness UI.

The UI has a fixed size of 680x960 pixels and is not resizable.
The Game Section contains:
- Stats View (top): 100px height with three stat boxes
- Game Board (middle): 640x640px with 20px padding on sides
- Preview View (bottom): Contains three 160x160px preview blocks
"""

# Window dimensions - fixed size
WINDOW_WIDTH = 680
WINDOW_HEIGHT = 960
PADDING = 10           # space between sections and window edges

# Content dimensions
CONTENT_HEIGHT = WINDOW_HEIGHT - 2 * PADDING  # 940

# Game width equals window width
GAME_WIDTH = WINDOW_WIDTH

# Section dimensions (legacy section dimensions kept for compatibility)
DDA_WIDTH = 372
SIM_WIDTH = 372
STATE_WIDTH = 372
SECTION_HEIGHT = CONTENT_HEIGHT

# Game section subdivisions
# Stats view
STATS_HEIGHT = 100
STATS_BOX_WIDTH = 213
STATS_BOX_HEIGHT = 80

# Hints view
HINTS_HEIGHT = 40  # height reserved for hint legend between stats and board
HINTS_PADDING = PADDING  # horizontal padding for hint text

# Game board
BOARD_SIZE = 640
BOARD_PADDING_W = (GAME_WIDTH - BOARD_SIZE) // 2  # 20px
CELL_RADIUS = 10

# Preview view
PREVIEW_HEIGHT = CONTENT_HEIGHT - STATS_HEIGHT - HINTS_HEIGHT - BOARD_SIZE
PREVIEW_BLOCK = 160
PREVIEW_CELL_RADIUS = 5
PREVIEW_PADDING_V = (PREVIEW_HEIGHT - PREVIEW_BLOCK) // 2
PREVIEW_PADDING_H = BOARD_PADDING_W
PREVIEW_GAP = 80  # horizontal gap between preview blocks

# Legacy constants - keeping for backward compatibility
SIDEBAR_WIDTH      = 560
SIDEBAR_PADDING    = 16
FIELD_HEIGHT       = 32
FIELD_SPACING      = 10
SECTION_SPACING    = 24
LABEL_SPACING      = 8
BORDER_RADIUS      = 4
SECTION_WIDTH      = (SIDEBAR_WIDTH - (SIDEBAR_PADDING * 3)) // 2
