# **GOAL:** 
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

To achieve this, follow all the steps one by one in the file named `Task.md`. Review the requirements one by one, then examine the code to determine what is needed to fulfill each requirement. Document the necessary actions for the first task, then move on to the second task, and so on.

---

# UI Layout Implementation Plan

This document outlines the step-by-step actions needed to implement the specified UI layout in the codebase. All file paths and constant names assume the existing project structure.

---

## 1. Update Layout Constants in `ui/layout.py` ✅

### 1.1 Define Window Size and Padding ✅

- **Action 1.1.1:** Open `ui/layout.py` (create if missing). ✅
- **Action 1.1.2:** Add the following constants at the top: ✅
  ```python
  WINDOW_WIDTH = 1920
  WINDOW_HEIGHT = 992
  PADDING = 10           # space between sections and window edges
  ```

### 1.2 Define Section Dimensions ✅

- **Action 1.2.1:** Still in `ui/layout.py`, compute content height: ✅
  ```python
  CONTENT_HEIGHT = WINDOW_HEIGHT - 2 * PADDING  # 972
  ```
- **Action 1.2.2:** Declare widths for each section: ✅
  ```python
  DDA_WIDTH = 372
  SIM_WIDTH = 372
  GAME_WIDTH = 754
  STATE_WIDTH = 372
  SECTION_HEIGHT = CONTENT_HEIGHT  # 972
  ```

### 1.3 Define Game Section Subdivisions ✅

- **Action 1.3.1:** Add stats view size: ✅
  ```python
  STATS_HEIGHT = 100
  STATS_BOX_WIDTH = 238
  STATS_BOX_HEIGHT = 80
  ```
- **Action 1.3.2:** Add game board size: ✅
  ```python
  BOARD_SIZE = 640
  BOARD_PADDING_W = (GAME_WIDTH - BOARD_SIZE) // 2  # 57 px
  ```
- **Action 1.3.3:** Add preview view size: ✅
  ```python
  PREVIEW_HEIGHT = CONTENT_HEIGHT - STATS_HEIGHT - BOARD_SIZE  # 232
  PREVIEW_BLOCK = 160
  PREVIEW_PADDING_V = (PREVIEW_HEIGHT - PREVIEW_BLOCK) // 2   # 36 px
  PREVIEW_PADDING_H = BOARD_PADDING_H                     # 57 px
  PREVIEW_GAP = 80  # horizontal gap between second and third block
  ```

---

## 2. Update Section View Classes ✅

For each section, update its view class to use the constants defined above.

### 2.1 DDA Section (`ui/views/dda_section.py`) ✅

- **Action 2.1.1:** Import layout constants: ✅
  ```python
  from ui.layout import PADDING, DDA_WIDTH, SECTION_HEIGHT
  ```
- **Action 2.1.2:** In `DDASection.__init__` (or similar), set: ✅
  ```python
  self.rect = pygame.Rect(
    PADDING,
    PADDING,
    DDA_WIDTH,
    SECTION_HEIGHT
  )
  ```
- **Action 2.1.3:** Update any control positions to start at `self.rect.x + PADDING`, `self.rect.y + PADDING`. ✅

### 2.2 Simulation Section (`ui/views/simulation_section.py`) ✅

- **Action 2.2.1:** Import constants: ✅
  ```python
  from ui.layout import PADDING, DDA_WIDTH, SIM_WIDTH, SECTION_HEIGHT
  ```
- **Action 2.2.2:** Compute origin: ✅
  ```python
  x_origin = PADDING + DDA_WIDTH + PADDING
  y_origin = PADDING
  ```
- **Action 2.2.3:** Initialize rect: ✅
  ```python
  self.rect = pygame.Rect(x_origin, y_origin, SIM_WIDTH, SECTION_HEIGHT)
  ```
- **Action 2.2.4:** Offset internal controls by `(self.rect.x + PADDING, self.rect.y + PADDING)`. ✅

### 2.3 Game Section (`ui/views/game_section.py`) ✅

- **Action 2.3.1:** Import constants: ✅
  ```python
  from ui.layout import PADDING, DDA_WIDTH, SIM_WIDTH, GAME_WIDTH, SECTION_HEIGHT
  ```
- **Action 2.3.2:** Compute origin: ✅
  ```python
  x_origin = PADDING + DDA_WIDTH + PADDING + SIM_WIDTH + PADDING
  y_origin = PADDING
  ```
- **Action 2.3.3:** Initialize game section rect: ✅
  ```python
  self.rect = pygame.Rect(x_origin, y_origin, GAME_WIDTH, SECTION_HEIGHT)
  ```

#### 2.3.4 Stats View Subcomponent (`hud_view.py`) ✅

- **Import:** `from ui.layout import PADDING, STATS_HEIGHT, STATS_BOX_WIDTH, STATS_BOX_HEIGHT, GAME_WIDTH` ✅
- **Origin:** ✅
  ```python
  stats_x = self.parent.rect.x
  stats_y = self.parent.rect.y
  ```
- **Loop to create three boxes:** ✅
  ```python
  for i in range(3):
      box_x = stats_x + PADDING + i * (STATS_BOX_WIDTH + PADDING)
      box_y = stats_y + PADDING
      box_rect = pygame.Rect(box_x, box_y, STATS_BOX_WIDTH, STATS_BOX_HEIGHT)
      # instantiate StatBox(box_rect)
  ```

#### 2.3.5 Game Board Subcomponent (`board_view.py`) ✅

- **Import:** `from ui.layout import BOARD_SIZE, BOARD_PADDING_H` ✅
- **Origin:** ✅
  ```python
  board_x = self.parent.rect.x + BOARD_PADDING_H
  board_y = self.parent.rect.y + STATS_HEIGHT
  self.board_rect = pygame.Rect(board_x, board_y, BOARD_SIZE, BOARD_SIZE)
  ```
- **Action 2.3.5.1:** Update `board_view.py` to use the new cell size and block size. ✅

#### 2.3.6 Preview View Subcomponent (`preview_view.py`) ✅

- **Import:** `from ui.layout import PREVIEW_HEIGHT, PREVIEW_BLOCK, PREVIEW_PADDING_H, PREVIEW_PADDING_V, PREVIEW_GAP` ✅
- **Origin:** ✅
  ```python
  preview_x = self.parent.rect.x
  preview_y = self.parent.rect.y + STATS_HEIGHT + BOARD_SIZE
  self.preview_rect = pygame.Rect(preview_x, preview_y, GAME_WIDTH, PREVIEW_HEIGHT)
  ```
- **Nested Preview Blocks:** ✅
  ```python
  # First block
  block1_x = preview_x + PREVIEW_PADDING_H
  block1_y = preview_y + PREVIEW_PADDING_V

  # Second block
  block2_x = block1_x + PREVIEW_BLOCK + PREVIEW_GAP
  block2_y = block1_y

  # Third block
  block3_x = block2_x + PREVIEW_BLOCK + PREVIEW_GAP
  block3_y = block1_y
  ```
- **Instantiate** each preview block area with these rects. ✅

### 2.4 Game State Section (`ui/views/game_state_section.py`) ✅

- **Action 2.4.1:** Import constants: ✅
  ```python
  from ui.layout import PADDING, DDA_WIDTH, SIM_WIDTH, GAME_WIDTH, STATE_WIDTH, SECTION_HEIGHT
  ```
- **Action 2.4.2:** Compute origin: ✅
  ```python
  x_origin = PADDING + DDA_WIDTH + PADDING + SIM_WIDTH + PADDING + GAME_WIDTH + PADDING
  y_origin = PADDING
  ```
- **Action 2.4.3:** Initialize rect: ✅
  ```python
  self.rect = pygame.Rect(x_origin, y_origin, STATE_WIDTH, SECTION_HEIGHT)
  ```
- **Action 2.4.4:** Layout game state items vertically starting at `self.rect.x + PADDING, self.rect.y + PADDING` with a gap of `PADDING` between items. ✅

---

## 3. Update `GameController` in `controllers/game_controller.py` ✅

### 3.1 Window Initialization (if required) ✅

- **Action 3.1.1:** Replace hardcoded dimensions with constants: ✅
  ```python
  from ui.layout import WINDOW_WIDTH, WINDOW_HEIGHT
  pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
  ```

### 3.2 View Instantiation & Positioning (if required) ✅

- **Action 3.2.1:** Pass layout constants to each view's constructor if required. ✅
- **Action 3.2.2:** Remove any `SIDEBAR_WIDTH` references; rely on each view's `rect` for positioning others. ✅

### 3.3 Drawing Logic (if required) ✅

- **Action 3.3.1:** In `_draw_core`, draw views in order: ✅
  1. `dda_section.draw()`
  2. `simulation_section.draw()`
  3. `game_section.draw()`
  4. `game_state_section.draw()`
- **Action 3.3.2:** Ensure each draw call uses the view's own `rect` for positioning. ✅

---

## 4. Update Event Handling in `controllers/game_controller.py` (if required) ✅

### 4.1 Click Handling (if required) ✅

- **Action 4.1.1:** In `handle_board_click(event)`, compute local click: ✅
  ```python
  x, y = event.pos
  rel_x = x - board_view.board_rect.x
  rel_y = y - board_view.board_rect.y
  col = rel_x // (BOARD_SIZE // BOARD_COLUMNS)
  row = rel_y // (BOARD_SIZE // BOARD_ROWS)
  ```
- **Action 4.1.2:** In `handle_preview_click(event)`, compute which preview block was clicked using `PREVIEW_BLOCK` and `PREVIEW_GAP` offsets. ✅

### 4.2 Resize Handling (if required) ✅

- **Action 4.2.1:** On `VIDEORESIZE`, recalculate all view `rects` using layout constants and new scale factors if dynamic resizing is supported. ✅
- **Action 4.2.2:** Redraw all sections with updated sizes. ✅

---

## 5. Create Any Missing View Stubs (if any) ✅

### 5.1 Identify Missing Files (if any) ✅

- **Action 5.1.1:** If `ui/views/game_state_section.py` does not exist, create it. ✅
- **Action 5.1.2:** If `ui/views/game_section.py` does not exist, create it and import subviews. ✅

### 5.2 Implement Stub Classes (if required) ✅

- **Action 5.2.1:** For each new view file, add: ✅
  ```python
  import pygame
  from ui.layout import ...

  class GameStateSection:
      def __init__(self):
          # initialize self.rect as above

      def draw(self, surface):
          # draw boundary and contents
          pass
  ```

---

## 6. Update Existing View Code (if required) ✅

### 6.1 Board View (`board_view.py`) ✅

- **Action 6.1.1:** Replace hardcoded size with `BOARD_SIZE`. ✅
- **Action 6.1.2:** Use `self.board_rect` instead of manual positions. ✅

### 6.2 Preview View (`preview_view.py`) ✅

- **Action 6.2.1:** Replace sizes with `PREVIEW_BLOCK` and paddings. ✅
- **Action 6.2.2:** Lay out blocks using the computed origins. ✅

### 6.3 HUD View (`hud_view.py`) ✅

- **Action 6.3.1:** Replace stat box sizes with `STATS_BOX_WIDTH`, `STATS_BOX_HEIGHT`. ✅
- **Action 6.3.2:** Layout boxes in a loop using `PADDING` offsets. ✅

---

## 7. Integration and Testing (manual)

### 7.1 Debug Visualizations (required) ✅

- **Action 7.1.1:** In `ui/debug.py`, add a flag `DEBUG_BORDERS = True`. ✅
- **Action 7.1.2:** In each `draw()`, if `DEBUG_BORDERS`, draw a colored border around `self.rect`. ✅

### 7.2 Layout Verification (manual)

- **Action 7.2.1:** Run the app and verify each section matches the specified dimensions (+/−1px tolerance).
- **Action 7.2.2:** Adjust constants if any rounding issues appear.

### 7.3 Interaction Tests (manual)

- **Action 7.3.1:** Click each stat box, board cell, and preview block; verify callback is triggered.
- **Action 7.3.2:** Log coordinates on click to ensure correct hit detection.

---

## 8. Finalization (manual)

### 8.1 Remove Debug Code

- **Action 8.1.1:** Set `DEBUG_BORDERS = False`.
- **Action 8.1.2:** Remove any temporary print/log statements.

### 8.2 Code Review (manual)

- **Action 8.2.1:** Ensure no magic numbers remain; all values come from `ui/layout.py`.
- **Action 8.2.2:** Verify consistent use of `PADDING` and section constants across files.

### 8.3 Documentation (Required) ✅

- **Action 8.3.1:** Update README or developer docs to reference new layout constants. ✅
- **Action 8.3.2:** Add a summary of the layout to `ui/layout.py` as comments. ✅

