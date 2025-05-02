
## VISION — "Collect-Metrics with Default-Config"

> **Goal**   
> 1. Instrument the game loop to emit a **comprehensive metrics object** every frame. metrics manager  
> 2. Persist all tunable values in `config/defaults.py`; treat them as read-only defaults for now.  
> 3. Expose the live metrics in the **State Section** (UI table).  
> 4. Do **NOT** change gameplay behaviour yet—just measure & report.

---

### 1. Config file (`config/defaults.py`)
```
board_size        = 8        # cols, rows
# weights:
occupancy       = 0.50
fragmentation   = 0.30
inv_largest     = 0.20

# flow:
low_clear       = 0.30
high_clear      = 0.70
danger_cut      = 0.80

# timing:
max_time_per_move= 8.0            # seconds
```

---

#### 2. Game-State Metrics  (emit each tick)

| Name                   | 1-line formula / note                                                        |
|------------------------|------------------------------------------------------------------------------|
| **ImminentThreat**     | `True` if *any* of the shape in preview does not fits on current board.      |
| **OccupancyRatio**     | `filledCells / (boardW × boardH)`                                            |
| **FragmentationCount** | `len(findEmptyClusters(board))` ← BFS/Flood-Fill.                            |
| **LargestEmptyRegion** | `maxClusterSize / totalEmptyCells` (0–1).                                    |
| **DangerScore**        | `0.50·Occupancy + 0.30·(1/FragmentationCount) + 0.20·(1-LargestEmptyRegion)` |
| **Phase**              | `"early" if moves ≤ 9; "mid" ≤ 29; else "late"`                              |

---

#### 3. Player-State Metrics  (emit after each move)

| Name                    | 1-line formula / note                                                                                                                               |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **MoveCount**           | increment per placement.                                                                                                                            |
| **LinesCleared**        | cumulative.                                                                                                                                         |
| **Score**               | existing scoring.                                                                                                                                   |
| **ClearRate**           | `LinesCleared / max(1,MoveCount)`.                                                                                                                  |
| **RecentClears[10]**    | ring buffer of last 10 `linesCleared` samples.                                                                                                      |
| **PerfBand**            | `"Hard"` if `ClearRate < LowClear`; `"Easy"` if > HighClear; else `"OK"`.                                                                           |
| **PlayerLevel**         | map ClearRate: `<0.2 ⇒ Novice`, `0.2-0.6 ⇒ Intermediate`, `>0.6 ⇒ Expert`.                                                                        |
| **EmotionalState**      | heuristic: `Frustrated` if `timePerMove > 0.8·max_time_per_move`; `Bored` if `timePerMove < 0.2·max_time_per_move && ClearRate > 0.7`; else `Calm`. |
| **TimePerMove**         | wall-clock Δ for last placement.                                                                                                                    |
| **AvgTimePerMove**      | sliding window for last 10 moves.                                                                                                                   |
| **PlacementEfficiency** | `linesCleared / bestPossibleLines` (oracle/heuristic). #skip for now just add a placeholder                                                         |
| **MistakeFlag**         | `True` on illegal-move attempt (trid to put a block where it doesn't fit)                                                                           |
| **MistakeCount**        | accumulated attempts to place blocks where they dont fit                                                                                            |
| **MistakeRate**         | `mistakes / MoveCount`                                                                                                                              |
| **MistakeSW**           | `mistakes` in last 10 moves                                                                                                                         |

---

> *Deliverables*:  
> • `config/defaults.py` (updated with metric defaults above)  
> • `utils/metrics_manager.py` with collection helpers & BFS utility  
> • State section UI updates to display metrics in a table in real time
---

TASK: Write a detailed implementation plan in @Task.md with check boxes [ ] with each step and its sub step, read all the files thoroghly before you start planning, 

**IMPORTANT:** THIS IS A PLANNING PHASE, READ THE FILES THOROUGHLY TO PLAN THIS FEATURE, DO NOT MODIFY ANY CODE OR TRY TO IMPLEMENT THIS, THIS IS A READ ONLY TASK WITH EXCEPTION TO @Task.md.
I REPEAT: DO NOT EDIT ANY CODE.a
# Game Metrics Implementation Plan

This document outlines the step-by-step actions needed to implement the comprehensive metrics system as specified.

## 1. Create Configuration System Updates

### 1.1 Update Configuration Defaults
- [ ] Add metrics configuration parameters to `config/defaults.py`:
  - [ ] Add board_size (8x8) parameter
  - [ ] Add weight factors: occupancy (0.50), fragmentation (0.30), inv_largest (0.20)
  - [ ] Add flow parameters: low_clear (0.30), high_clear (0.70), danger_cut (0.80)
  - [ ] Add timing: max_time_per_move (8.0 seconds)

### 1.2 Create Configuration Validation
- [ ] Add validation in config system to ensure metrics parameters are within valid ranges
- [ ] Add helper functions to retrieve metrics configuration

## 2. Create Metrics Manager

### 2.1 Create Base Structure
- [ ] Create new file `utils/metrics_manager.py`
- [ ] Implement `MetricsManager` class with the following attributes:
  - [ ] Game state metrics (board-related)
  - [ ] Player state metrics (performance-related)
  - [ ] Timing metrics
  - [ ] Configuration reference

### 2.2 Implement Game State Metrics
- [ ] Implement methods to calculate:
  - [ ] `calculate_imminent_threat`: Detect if any preview shape doesn't fit on current board
  - [ ] `calculate_occupancy_ratio`: Calculate filled cells / total cells
  - [ ] `calculate_fragmentation_count`: Implement BFS/flood-fill algorithm to find empty clusters
  - [ ] `calculate_largest_empty_region`: Find largest empty cluster relative to total empty cells
  - [ ] `calculate_danger_score`: Combine metrics using configured weights
  - [ ] `determine_game_phase`: Map move count to phases (`early` if ≤ 9 moves; `mid` if ≤ 29; else `late`)

### 2.3 Implement Player State Metrics
- [ ] Implement methods to calculate:
  - [ ] Track move count, lines cleared, score (existing)
  - [ ] `calculate_clear_rate`: Lines cleared / max(1, move count)
  - [ ] Implement ring buffer for recent clears (last 10 moves)
  - [ ] `determine_perf_band`: Compare clear rate to low/high thresholds (`Hard` if < low_clear; `Easy` if > high_clear; else `OK`)
  - [ ] `determine_player_level`: Map clear rate to skill level (`Novice` if <0.2; `Intermediate` if <0.6; `Expert` if ≥0.6)
  - [ ] `determine_emotional_state`: Heuristic based on timing and clear rate (`Frustrated` if timePerMove >0.8×max_time_per_move; `Bored` if timePerMove <0.2×max_time_per_move **and** clear rate > high_clear; else `Calm`)
  - [ ] `calculate_time_per_move`: Track time delta for last move
  - [ ] `calculate_avg_time_per_move`: Sliding window for last 10 moves
  - [ ] Create placeholder for `calculate_placement_efficiency` (future implementation)
  - [ ] Track mistake flags, count, rate, and sliding window

### 2.4 Implement Core Utilities
- [ ] Implement BFS utility for finding connected empty regions
- [ ] Implement sliding window utility for time-based metrics
- [ ] Create method to export all metrics as a JSON object
- [ ] Create method to update all metrics (to be called each frame)

## 3. Integrate Metrics Manager with Game Engine

### 3.1 Update Game Engine
- [ ] Import `MetricsManager` in `GameEngine`
- [ ] Initialize `MetricsManager` in `GameEngine.__init__`
- [ ] Add timing tracking before/after player actions
- [ ] Modify `place_selected_block` to track placement time and detect mistakes
- [ ] Create hook to update metrics after each game action
- [ ] Call `MetricsManager.update_all_metrics()` at the end of each frame in `GameController._loop_core` to emit the metrics object

### 3.2 Update Controllers
- [ ] Modify BaseController to access metrics from engine
- [ ] Add method to get_game_metrics() alongside get_game_state()
- [ ] Update GameController to pass metrics to views

## 4. Update State Section UI

### 4.1 Enhance State Section
- [ ] Update state_section.py to display metrics:
  - [ ] Create scrollable metrics view
  - [ ] Group metrics into categories (Game State, Player State, Timing)
  - [ ] Add styling for different metric types and warning states
  - [ ] Update draw method to show all metrics with current values

### 4.2 Create Metrics Visualization Components
- [ ] Create helper components in ui/views/metrics/:
  - [ ] Create metrics_table.py for tabular display of metrics
  - [ ] Create metrics_chart.py for simple visualizations (optional)
  - [ ] Create perf_band_indicator.py for visual performance indicators

### 4.3 Update Main View
- [ ] Update main_view.py to handle state_section with metrics
- [ ] Ensure metrics are refreshed with each draw cycle

## 5. Testing and Refinement

### 5.1 Create Test Tools
- [ ] Create/update debug tools to validate metrics calculations
- [ ] Add developer mode to show additional metrics details

### 5.2 Testing Plan
- [ ] Test basic metrics calculations with known board states
- [ ] Test BFS implementation for fragmentation counting
- [ ] Test edge cases (empty board, full board, game over state)
- [ ] Test performance to ensure metrics calculations don't impact game performance
- [ ] Test UI display of metrics in different window sizes
- [ ] Verify no gameplay behaviour changes (score, lines, moves) to ensure metrics collection is non-intrusive

## 6. Documentation

### 6.1 Code Documentation
- [ ] Add comprehensive docstrings to all new methods
- [ ] Document the formulas and algorithms used for calculations
- [ ] Add type hints to all new code

### 6.2 User Documentation
- [ ] Update README.md with information about the metrics system
- [ ] Create a metrics.md explaining all tracked metrics and their meaning

## 7. Future Extensions

### 7.1 Prepare for Next Features
- [ ] Add extension points for future metrics
- [ ] Plan storage of metrics history for analysis
- [ ] Structure metrics code to allow additional visualizations later
