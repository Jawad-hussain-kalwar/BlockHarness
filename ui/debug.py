# ui/debug.py
"""
Debug utilities for UI visualization and development.
"""

import pygame

# Set to True to display colored borders around UI sections
DEBUG_BORDERS = False

# Colors for section borders
SECTION_BORDER_COLORS = {
    "dda": (255, 100, 100),       # Red
    "simulation": (100, 255, 100), # Green
    "game": (100, 100, 255),       # Blue
    "state": (255, 255, 100),      # Yellow
    "board": (255, 100, 255),      # Magenta
    "preview": (100, 255, 255),    # Cyan
    "stats": (255, 180, 100)       # Orange
}

def draw_debug_rect(surface, rect, section_type):
    """Draw a debug colored border around a rect for the given section type."""
    if DEBUG_BORDERS:
        if section_type in SECTION_BORDER_COLORS:
            color = SECTION_BORDER_COLORS[section_type]
        else:
            color = (255, 255, 255)  # Default white
        
        pygame.draw.rect(surface, color, rect, 2) 