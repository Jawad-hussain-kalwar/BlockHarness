I have attached a screenshot outlining the desired UI layout. The entire window has a width of 1920 pixels and a height of 992 pixels. There are four sections with 10px padding between them and on each side.

**Calculation:**
- Remaining width for sections content: 1920 - 50px (padding) = 1870px
- Remaining height for sections content: 992 - 20px (padding) = 972px

**Optional Placement Strategy:**
- All sections have 10px padding on the right, top, and bottom.
- Only the DDA section has padding on the left because it is the first one.

**Sections:**
1. **DDA Section:** 372px width x 972px height (excluding padding)
2. **Simulation Section:** 372px width x 972px height (excluding padding)
3. **Game Section:** 754px width x 972px height (excluding padding)
4. **Game State Section:** 372px width x 972px height (excluding padding)

**Game Section Details:**
The game section is divided into three parts:
1. **Stats View:** 754px x 100px
   - Each stat takes 238px x 80px, laid out horizontally.
   - The first stat has 10px padding on the left.
   - All stats have 10px padding on the top, right, and bottom.

2. **Game Board:** 640px x 640px
   - 57px padding on the right and left.
   - No padding on the top or bottom.

3. **Preview View:** 754px width x 232px height (remaining height)
   - Preview area: 640px x 160px
   - Padding: 36px on top and bottom, 57px on left and right.
   - Contains three Preview Block Areas, each 160px x 160px, laid out horizontally.
   - The first Preview Block Area has no padding on the left and right.
   - The second and third Preview Block Areas have 80px padding on the left.

To achieve this, thoroughly plan each step required. Write down all the steps one by one in a file named `@Task.md`. Review the requirements one by one, then examine the code to determine what is needed to fulfill each requirement. Document the necessary actions for the first task, then move on to the second task, and so on.

# BlockHarness UI Layout Implementation Plan

## Overview

This document outlines the detailed steps required to implement the new UI layout based on the provided specifications. The layout consists of four main sections with specific dimensions and padding requirements.

## 1. Update Layout Constants

### Task 1.1: Define New Layout Constants
- Create new constants in `ui/layout.py` for the new layout specifications:
  - Window dimensions: 1920×992 pixels
  - Padding values: 10px between sections and on sides
  - Section widths: 372px for DDA, Simulation, and Game State sections; 754px for Game section
  - Section heights: 972px (excluding padding)
  - Game section subdivisions:
    - Stats View: 754×100px
    - Game Board: 640×640px with 57px padding on left/right
    - Preview View: 754×232px
    - Preview Block Areas: 160×160px each

## 2. Create or Update Section Components

### Task 2.1: Update DDA Section
- Update `ui/views/dda_section.py` to conform to new dimensions (372×972px)
- Adjust positioning to account for 10px padding
- Update internal layout of controls if necessary

### Task 2.2: Update Simulation Section
- Update `ui/views/simulation_section.py` to conform to new dimensions (372×972px)
- Position with 10px padding from DDA section
- Adjust internal controls as needed

### Task 2.3: Implement Game Section
- Create/update a main game section container view
- Implement three sub-components:
  - Stats View (754×100px)
    - Create three stat boxes, each 238×80px
    - Position horizontally with specified padding
  - Game Board (640×640px)
    - Update `board_view.py` with new dimensions and positioning
    - Ensure 57px padding on left/right
  - Preview View (754×232px)
    - Update `preview_view.py` with new dimensions
    - Implement three preview block areas, each 160×160px
    - Apply correct padding and spacing

### Task 2.4: Implement Game State Section
- Create/update a Game State section (372×972px)
- Position at the rightmost part of the window
- Implement internal controls for displaying game state information

## 3. Update Game Controller

### Task 3.1: Update Window Initialization
- Modify `game_controller.py` to initialize window with correct dimensions (1920×992)
- Ensure DPI awareness is maintained

### Task 3.2: Update View Initialization and Positioning
- Update the initialization of all view components with new positions and dimensions
- Update the calculation of board_origin, preview_origin, and other position variables
- Replace the previous SIDEBAR_WIDTH-based calculations with the new layout constants

### Task 3.3: Update Drawing Logic
- Modify the `_draw_core` method to draw all sections with correct z-order
- Ensure each section is positioned correctly with the required padding

## 4. Update Event Handling

### Task 4.1: Update Click Handling
- Update `handle_board_click` and `handle_preview_click` to work with the new coordinates
- Calculate grid positions based on new board origin and dimensions

### Task 4.2: Update Window Resize Handling
- Update the window resize event handling to maintain the layout proportions
- Ensure all views are updated when the window is resized

## 5. Create New Required Views

### Task 5.1: Identify Missing Views
- Determine if any new view classes are needed for the new layout
- Create class stubs for any new required views

### Task 5.2: Implement Missing Views
- Implement any new view classes required for the layout
- Ensure they adhere to the dimension and padding requirements

## 6. Update Existing Views

### Task 6.1: Update Board View
- Modify `board_view.py` to use the new dimensions and position
- Update the cell size calculation if necessary

### Task 6.2: Update Preview View
- Modify `preview_view.py` to use new layout specifications
- Update spacing and positioning of preview blocks

### Task 6.3: Update HUD View
- Modify `hud_view.py` to use new layout specifications
- Ensure it's correctly positioned within the Game Section

## 7. Integration and Testing

### Task 7.1: Testing Layout Dimensions
- Add debug visualization to verify correct section dimensions
- Add temporary borders to visualize section boundaries

### Task 7.2: Testing Section Content
- Verify that all section content is properly contained within the section boundaries
- Ensure all elements are correctly positioned and sized

### Task 7.3: Testing UI Interactions
- Test all UI interactions (clicks, selections) with the new layout
- Verify that event coordinates are correctly translated to grid positions

## 8. Finalization

### Task 8.1: Remove Debug Visualization
- Remove any debug visualization code
- Clean up any temporary test code

### Task 8.2: Final Code Review
- Review all changes to ensure they meet the layout requirements
- Check for any hardcoded values that should be constants
- Ensure consistent code style throughout the changes

### Task 8.3: Documentation Update
- Update any relevant documentation to reflect the new layout
- Add comments to explain any complex layout calculations

## Implementation Approach

1. Start by updating the layout constants to define the new dimensions and spacing
2. Update the window initialization to use the correct size
3. Create or update the section views one by one, starting with the main containers
4. Update the drawing logic to position all sections correctly
5. Update the event handling to work with the new layout
6. Test the layout with debug visualization before finalizing

## Dependencies and Considerations

- The existing code uses pygame for rendering, which will continue to be used
- The current window initialization includes DPI awareness, which must be preserved
- The current code uses a mix of absolute and relative positioning, which will need to be updated
- The resize handling will need special attention to maintain the layout proportions 