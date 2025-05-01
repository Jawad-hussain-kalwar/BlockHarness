# UI Layout System

This document describes the UI layout system implemented for the BlockHarness application.

## Overview

The UI is divided into four main sections with the following dimensions:

1. **DDA Section:** 372px width x 972px height
2. **Simulation Section:** 372px width x 972px height
3. **Game Section:** 754px width x 972px height
4. **Game State Section:** 372px width x 972px height

These sections are arranged horizontally with 10px padding between them and on the edges of the window.

## Layout Constants

All layout constants are defined in `ui/layout.py`. The main constants are:

- `WINDOW_WIDTH = 1920` - Total window width
- `WINDOW_HEIGHT = 992` - Total window height
- `PADDING = 10` - Space between sections and window edges
- `CONTENT_HEIGHT = 972` - Available height for content (WINDOW_HEIGHT - 2*PADDING)

### Section Dimensions
- `DDA_WIDTH = 372`
- `SIM_WIDTH = 372`
- `GAME_WIDTH = 754`
- `STATE_WIDTH = 372`
- `SECTION_HEIGHT = 972`

### Game Section Subdivisions

The Game Section is further divided into:

1. **Stats View (Top)**
   - `STATS_HEIGHT = 100`
   - `STATS_BOX_WIDTH = 238`
   - `STATS_BOX_HEIGHT = 80`

2. **Game Board (Middle)**
   - `BOARD_SIZE = 640`
   - `BOARD_PADDING_W = 57` (centered horizontally)

3. **Preview View (Bottom)**
   - `PREVIEW_HEIGHT = 232`
   - `PREVIEW_BLOCK = 160`
   - `PREVIEW_PADDING_V = 36`
   - `PREVIEW_PADDING_H = 57`
   - `PREVIEW_GAP = 80`

## Debugging

To visualize the layout during development:

1. Set `DEBUG_BORDERS = True` in `ui/debug.py`
2. Run the application
3. Colored borders will be displayed around each section:
   - DDA Section: Red
   - Simulation Section: Green
   - Game Section: Blue
   - Game State Section: Yellow
   - Board: Magenta
   - Preview Blocks: Cyan
   - Stats Boxes: Orange

## Implementation

Each view component has been updated to:
1. Import layout constants from `ui/layout.py`
2. Initialize a `self.rect` property with the appropriate dimensions
3. Draw using the rect for positioning
4. Optionally display debug borders when `DEBUG_BORDERS` is enabled

## Maintenance

When modifying the layout:
1. Update constants in `ui/layout.py`
2. Ensure new controls are positioned relative to their section's `rect`
3. Use the debug borders to verify positioning 