## Hot-spot discovery

### Functions / methods with cyclomatic complexity ≥ 10

| Function / Method | CC | Fan-in | Fan-out | In cycles? | High coupling (≥ 12) |
| ----------------- | -- | ------ | ------- | ---------- | -------------------- |
| `BlockPool._generate_blocks_below_threshold` | 20 | 1 | 9 | no | no |
| `BlockPool._select_distinct_blocks` | 13 | 2 | 3 | no | no |
| `GameController.handle_events` | 18 | 1 | 6 | no | no |
| `MainView.handle_event` | 16 | 0 | 0 | – | no |
| `Board.clear_full_lines` | 11 | 0 | 0 | – | no |
| `InputField.handle_event` | 11 | 0 | 0 | – | no |
| `PreviewView.render` | 10 | 0 | 0 | – | no |

_No node combined both high complexity and very high coupling (fan-in + fan-out ≥ 12); however the first three items sit close to the threshold and deserve attention._

---

## Refactoring opportunities

### 1. `BlockPool._generate_blocks_below_threshold`  (CC 20)
* **Issues**: Deep nesting, repeated filtering logic, duplicate calls to `_select_distinct_blocks` and `Block.__init__` inflate fan-out.
* **Proposed refactor**: 
  * Extract helper methods:
    * `_filter_blocks_below_threshold()` – returns candidate shapes.
    * `_instantiate_block()` – wraps `Block()` construction.
  * Replace duplicate calls with a single loop or comprehension.
* **Estimated post-refactor CC**: ≈ 7.
* **Change scope**: `engine/block_pool.py` only.

### 2. `GameController.handle_events`  (CC 18)
* **Issues**: Swiss-army method handling disparate event types; difficult to test.
* **Proposed refactor**:
  * Introduce a **Command / Strategy** pattern: map `pygame` event codes to dedicated handler methods (`_on_key()`, `_on_mouse()`, etc.).
  * Move restart logic into `restart_game()` and configuration logic into `apply_config_changes()`.
* **Estimated post-refactor CC**: 7-9.
* **Change scope**: `engine/game_controller.py`; minor updates to callers.

### 3. `MainView.handle_event`  (CC 16)
* **Issues**: Similar event-dispatch bloat to `GameController.handle_events`.
* **Proposed refactor**: Extract a private `_dispatch()` plus per-widget handlers; consider delegating to child views.
* **Estimated post-refactor CC**: 6-8.
* **Change scope**: `ui/views/main_view.py` and sub-views.

### 4. `BlockPool._select_distinct_blocks`  (CC 13)
* **Issues**: Iterative uniqueness checks; several redundant passes over data.
* **Proposed refactor**: Use `random.sample()` with a `set` of recent L-values to guarantee distinctness; collapse duplicate logic.
* **Estimated post-refactor CC**: 5-6.
* **Change scope**: `engine/block_pool.py` only.

### 5. `InputField.handle_event`  (CC 11)
* **Issues**: Multiple branches for keyboard vs mouse vs focus.
* **Proposed refactor**: Split into `_handle_keypress()` and `_handle_mouse()` helpers; keep state transitions obvious.
* **Estimated post-refactor CC**: 5-6.

### 6. `Board.clear_full_lines`  (CC 11, zero callers?)
* **Issues**: Not referenced in the current call-graph; may be **dead code** or legacy.
* **Actions**: Verify usage via tests; if truly unused, delete or move to utility module.

### 7. `PreviewView.render`  (CC 10)
* **Issues**: Monolithic rendering routine combining layout + draw calls.
* **Proposed refactor**: Extract `_render_block()` per preview item and `_render_selection_highlight()`.
* **Estimated post-refactor CC**: 4-5.

---

## Architectural insight

### God classes / modules

| Class / Module | Total edges | Symptoms | Recommendation |
| -------------- | ----------- | -------- | -------------- |
| `GameEngine` | ≈ 30 | Central hub for block logic, scoring, animation, and game-over detection. | Split into `BoardLogic`, `ScoreManager`, `AnimationOrchestrator`.
| `BlockPool` | ≈ 20 | Generates blocks, maintains L-value stats, enforces config. | Separate `BlockGenerator` from statistical tracking.
| `GameController` | ≈ 15 | Event loop, config management, rendering orchestration. | Introduce `EventDispatcher`; move rendering to view layer.

### Potential orphan / dead code

* `Board.clear_full_lines` – not present in call-graph; confirm usage.
* `MainView.handle_event`, `InputField.handle_event`, `PreviewView.render` show zero incoming edges – check if code2flow missed GUI callbacks or if they are indeed unused during gameplay.

---

## Risk × Effort matrix

| # | Item | Benefit | Effort |
| - | ---- | -------- | ------ |
| 1 | Extract event dispatch in `GameController.handle_events` | High | Medium |
| 2 | Split `GameEngine` into focused components | High | Large |
| 3 | Refactor `BlockPool` generation methods | Medium-High | Medium |
| 4 | Extract handlers in `MainView.handle_event` | Medium | Medium |
| 5 | Trim / refactor `InputField.handle_event` | Medium | Small |
| 6 | Delete or relocate unused `Board.clear_full_lines` | Medium | Small |
| 7 | Modularise `PreviewView.render` | Low-Medium | Small |

**Prioritised action list (highest value first)**
1. `GameController.handle_events` extraction (1)
2. `BlockPool` generation / selection simplification (3)
3. Confirm & remove dead code (`Board.clear_full_lines`) (6)
4. `InputField.handle_event` split (5)
5. `MainView.handle_event` dispatch (4)
6. Split `GameEngine` responsibilities (2 – larger but strategic)
7. Optimise `PreviewView.render` (7)

---
