## Problem:
Currently, `@dda.py` and `@block_pool.py` share the same responsibility of generating three new blocks for the preview section. This setup is unnecessarily complex and ineffective.

## Objective:
To simplify, we need to update `@block_pool.py` with the correct algorithm and eliminate `@dda.py` entirely. Below is the algorithm for generating the next three blocks:

## variables:
### from metrics manager:
	- best fit block: (block) this block clears most lines on the board
	- best fit place: (tupple)(row, column)
	- opportunity: (bool) if any of the blocks from all possible blocks can not fit the available space on the board
	- game over block: (block) this block does not fit anywhere on the board
	- moves: (int) number of blocks placed
	- lines cleared: (int) number of lines cleared
	- clear rate: (float) lines cleared/moves | 0 when moves==0
	
### from config: 
	- number of best fit blocks to generate: (int) 
	- number of game over blocks to generate: (int) 
	- score threshold: (int) 
	- low clear rate: (float) between 0 and high clear rate
	- high clear rate: (float) between low clear rate and 1
	
### baked in:
	- L: (int) frequency of 'best fit' block generation (Only values 1, 2, 3 are allowed):
		L=1 (when clear rate is low): Generate 'n' 'best fit' in every tray.
		L=2 (when clear rate is medium): Generate 'n' 'best fit' in every 2nd tray.
		L=3 (when clear rate is high): Generate 'n' 'best fit' in every 3rd tray.

## Algorithm:
get config from config
get metrics from metrics manager

initialize tray_index = 0
initialize last generated blocks = []
initialize default weights from config = []


set weights of last generated blocks = 0

if score is lower than score threshold:
    if clear rate is low:
        generate n best fit blocks, 3-n distinct weighted random blocks, no game over blocks
        
    else if clear rate is medium:
        generate 3 distinct weighted random blocks for the first tray, no game over blocks
        generate n best fit blocks in every 2nd tray, 3-n distinct weighted random blocks in every 2nd tray, no game over blocks
    else if clear rate is high:
        generate 3 distinct weighted random blocks for the first tray, no game over blocks
        generate 3 distinct weighted random blocks for the second tray, no game over blocks
        generate n best fit blocks in every 3rd tray, 3-n distinct weighted random blocks in every 3rd tray, no game over blocks

if score is higher than score threshold:
    generate n game over blocks, 3-n weighted random blocks, no best fit blocks, in every tray

save generated blocks to last generated blocks

## Comprehensive Implementation Plan

### Phase 1: Analysis and Preparation

#### 1. Dependencies Analysis ✅
- `engine/game_engine.py` depends on DDA in multiple places:
  - Line 59-65: DDA algorithm initialization ✅
  - Line 303-326: Uses DDA to refill preview blocks via `get_next_blocks` ✅
  - Original BlockPool is used only for fallback ✅

#### 2. Configuration Review ✅
- Relevant configuration in `config/defaults.py`:
  - `DEFAULT_WEIGHTS`: Used for block generation weighting ✅
  - `dda_params`: Contains DDA-specific configuration parameters (add if needed, must be reflected in ui) ✅

#### 3. Algorithm Logic Transfer ✅
- DDA's core functionality for block generation needs to be migrated to BlockPool:
  - Tray tracking mechanism ✅
  - Clear rate based L value calculation ✅
  - threshold, opportunity and 'L' based Best fit and game over block generation ✅

### Phase 2: Implementation Plan

#### 1. Update `engine/block_pool.py`: ✅
1. Enhance class definition with new attributes: ✅
   ```python
   def __init__(self, shapes, weights, config=None):
       self.shapes = shapes
       self.shape_names = list(shapes.keys())
       self.weights = weights
       self.config = config or {}
       self.tray_counter = 0
       self.L = 1  # Default L value
       self.last_generated_blocks = []
   ```

2. Add configuration loading method: ✅
   ```python
   def _load_config(self, config):
       # Extract required configuration values
       dda_config = config.get("dda_params", {}).get("dda", {})
       
       # Load parameters
       self.low_clear_rate = dda_config.get("low_clear_rate", 0.5)
       self.high_clear_rate = dda_config.get("high_clear_rate", 0.8)
       self.score_threshold = dda_config.get("score_threshold", 100)
       self.n_best_fit_blocks = dda_config.get("n_best_fit_blocks", 1)
       self.n_game_over_blocks = dda_config.get("n_game_over_blocks", 1)
   ```

3. Implement `get_next_blocks` method to replace DDA's functionality: ✅
   ```python
   def get_next_blocks(self, engine_state, count=3):
       # Get metrics from engine state
       metrics = engine_state.get_metrics()
       
       # Increment tray counter
       self.tray_counter += 1
       
       # Get block generation parameters
       return self._generate_next_blocks(metrics, count)
   ```

4. Implement helper methods: ✅
   ```python
   def _generate_next_blocks(self, metrics, count):
       # Extract metrics
       best_fit_block = metrics.get("best_fit_block", "None")
       opportunity = metrics.get("opportunity", False)
       game_over_block = metrics.get("game_over_block", "None")
       score = metrics.get("score", 0)
       clear_rate = metrics.get("clear_rate", 0.0)
       
       # Update L based on clear rate
       self._update_L_value(clear_rate)
       
       # Generate blocks based on conditions
       blocks = []
       
       # Implementation of the algorithm as described
       if score < self.score_threshold:
           blocks = self._generate_blocks_below_threshold(best_fit_block, count, clear_rate)
       else:
           blocks = self._generate_blocks_above_threshold(game_over_block, opportunity, count)
           
       # Store generated blocks
       self.last_generated_blocks = [b.cells for b in blocks]
       
       return blocks
   ```

5. Algorithm-specific helper methods: ✅
   ```python
   def _update_L_value(self, clear_rate):
       if clear_rate >= self.high_clear_rate:
           self.L = 3
       elif clear_rate >= self.low_clear_rate:
           self.L = 2
       else:
           self.L = 1
   
   def _generate_blocks_below_threshold(self, best_fit_block, count, clear_rate):
       # Implementation based on clear rate and L value
   
   def _generate_blocks_above_threshold(self, game_over_block, opportunity, count):
       # Implementation for above threshold
   
   def _select_distinct_blocks(self, count, excluded_shapes=None, biased_shape=None):
       # Select distinct blocks with optional exclusions
   ```

#### 2. Update `engine/game_engine.py`: ✅
1. Remove DDA initialization and references: ✅
   - Remove lines 59-65 where DDA is initialized ✅
   - Remove the dda_algorithm attribute ✅

2. Update the constructor to properly initialize BlockPool with config: ✅
   ```python
   self.pool = BlockPool(
       self.config["shapes"],
       self.config["shape_weights"],
       self.config
   )
   ```

3. Modify `_refill_preview` method: ✅
   ```python
   def _refill_preview(self, target_count=3):
       # Determine how many blocks to generate
       num_to_generate = max(0, target_count - len(self._preview_blocks))
       
       if num_to_generate <= 0:
           return  # Preview already has enough blocks
           
       try:
           # Get blocks directly from the enhanced BlockPool
           new_blocks = self.pool.get_next_blocks(self, num_to_generate)
           
           # Add new blocks to preview
           self._preview_blocks.extend(new_blocks)
           
           # Select first block if none selected
           if self._selected_preview_index is None and self._preview_blocks:
               self._selected_preview_index = 0
               
       except Exception as e:
           print(f"[engine/game_engine.py][Error] Error in _refill_preview: {e}")
           # There must not be any fallback code, if the game carshes I need to know why and fix the root cause instead of using a fallback
   ```

4. Remove the `_spawn` method. ✅

#### 3. Clean Up Work: ✅
1. Delete `engine/dda.py` after all functionality is migrated ✅
2. Update `config/defaults.py`: ✅
   - Merge relevant DDA configuration under a new "block_generation" key ✅
   - DO NOT Maintain backward compatibility for existing code, WE DO NOT WANT TO USE DDA ANYMORE ✅

### Phase 3: Testing and Verification

#### 1. Test Plan: ✅
1. Unit Tests:
   - Create tests for the new BlockPool class functionality ✅
   - Verify correct block generation in various scenarios: ✅
     - Low, medium, and high clear rates ✅
     - Above and below score threshold ✅
     - With and without best fit/game over blocks ✅

2. Integration Tests:
   - Verify game still functions after DDA removal ✅
   - Ensure preview blocks are generated correctly ✅
   - Validate difficulty adjustment still works as expected ✅

#### 2. Performance Evaluation: ✅
- Compare performance before and after changes ✅
- Ensure block generation algorithm doesn't introduce significant delays ✅

### Phase 4: Documentation ✅

#### 1. Update Code Documentation: ✅
- Add detailed docstrings to new methods in BlockPool ✅
- Explain algorithm logic in class-level documentation ✅
- Update README.md with the new block generation algorithm ✅

This plan provides a comprehensive approach to consolidate the block generation functionality from DDA into BlockPool while maintaining the same game behavior.