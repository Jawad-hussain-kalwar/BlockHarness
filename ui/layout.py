# ui/layout.py
"""
Layout constants for the BlockHarness UI.

This layout is designed to be responsive for Android devices:
- The game scales horizontally to fill the device screen width
- Vertical space is adjusted proportionally to maintain aspect ratio
- Elements are positioned relative to the base dimensions and scaled on render
- Touch targets are sized appropriately for mobile interfaces
"""

# Base design dimensions - used as reference for scaling
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

# Touch-friendly UI constants for mobile
TOUCH_TARGET_MIN = 48  # Minimum touch target size (in pixels)
BUTTON_PADDING = 12    # Padding for buttons to increase touch area

# Legacy constants - keeping for backward compatibility
SIDEBAR_WIDTH      = 560
SIDEBAR_PADDING    = 16
FIELD_HEIGHT       = 32
FIELD_SPACING      = 10
SECTION_SPACING    = 24
LABEL_SPACING      = 8
BORDER_RADIUS      = 4
SECTION_WIDTH      = (SIDEBAR_WIDTH - (SIDEBAR_PADDING * 3)) // 2

# Dynamic scaling helpers
def scale_position(x: float, y: float, scale_factor: float) -> tuple:
    """Scale a position based on the current scale factor.
    
    Args:
        x: Original x coordinate
        y: Original y coordinate
        scale_factor: Current scaling factor
        
    Returns:
        Tuple containing scaled x and y coordinates
    """
    return x * scale_factor, y * scale_factor

def scale_rect(rect, scale_factor: float) -> tuple:
    """Scale a rectangle (x, y, width, height) based on the current scale factor.
    
    Args:
        rect: Original rectangle as (x, y, width, height)
        scale_factor: Current scaling factor
        
    Returns:
        Tuple containing scaled rectangle values
    """
    return (
        rect[0] * scale_factor,
        rect[1] * scale_factor,
        rect[2] * scale_factor,
        rect[3] * scale_factor
    )
