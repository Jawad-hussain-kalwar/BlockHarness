# DDA System Refactoring Plan

## Problem Analysis

After reviewing the codebase, I've identified the key issues with the current DDA implementation:

1. **Inconsistent Integration**: The DDA algorithms are well-designed but not properly integrated with the game engine.
2. **Limited DDA Control**: DDAs currently only return weight adjustments, but don't have direct control over which blocks spawn.
3. **Unused DDA Algorithms**: IntervalDDA and MetricsDDA are implemented and registered but they're ineffective as they only modify weights which are not properly used by the game engine.
4. **Hard-coded Block Selection Logic**: The game engine's block generation is performed by the BlockPool class using a weighted random approach, which limits the DDA's ability to make strategic block selection.

## Goals

- Refactor the system so DDAs return specific blocks to spawn rather than just weights
- Maintain backward compatibility with existing ThresholdDDA and StaticDDA
- Ensure all DDA algorithms (including IntervalDDA and MetricsDDA) work as intended
- Make the system extensible for future DDA algorithms

## Implementation Plan

### 1. Update the DDA Algorithm Interface
- [x] Modify the `BaseDDAAlgorithm` class to include a new method for block selection
- [x] Add a `get_next_blocks()` method that returns specific Block objects instead of just weights
- [x] Update the docstrings and type hints to reflect the new interface

### 2. Refactor Game Engine Block Generation
- [x] Modify `GameEngine._refill_preview()` to use DDA algorithm for block selection
- [x] Change how blocks are generated to use the DDA's block selection method
- [x] Create a compatibility layer for existing DDAs to work with the new system

### 3. Update Existing DDA Algorithms
- [x] Modify ThresholdDDA to implement the new `get_next_blocks()` method
- [x] Update StaticDDA to implement the new block selection logic
- [x] Enhance IntervalDDA and MetricsDDA to take advantage of direct block selection
- [x] Ensure backward compatibility with existing configuration parameters

### 4. Update DDA Registry and Configuration
- [x] Update the DDA registry to support the new interface
- [x] Modify configuration handling to support block-specific DDA parameters
- [x] Ensure backward compatibility with existing configuration files

### 5. Controller and UI Updates
- [x] Update controllers to work with the new DDA block selection approach
- [x] Ensure metrics tracking still works with the new implementation
- [x] Add any necessary UI elements to show DDA influence on block selection

## Detailed Implementation Steps

### 1. BaseDDAAlgorithm Interface Update

#### 1.1 Add New Method to BaseDDAAlgorithm
- [x] Add a `get_next_blocks(engine_state, count: int = 3)` method to BaseDDAAlgorithm
- [x] Make this a required abstract method for all DDA implementations
- [x] Keep the existing `maybe_adjust()` method for backward compatibility

```python
# In base_dda.py
@abstractmethod
def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
    """Get the next blocks to spawn in the preview tray.
    
    Args:
        engine_state: The current game engine state
        count: Number of blocks to generate (default 3)
        
    Returns:
        List[Block]: The specific blocks to be spawned in the preview tray
    """
    pass
```

#### 1.2 Backward Compatibility Layer
- [x] Add a default implementation of `get_next_blocks` that uses `maybe_adjust()` and random selection
- [x] This ensures existing DDAs can work without immediate modification

```python
# In base_dda.py - default implementation for backward compatibility
def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
    """Default implementation that uses maybe_adjust() and weighted random selection.
    DDA algorithms should override this with their own implementation.
    """
    # Get weights adjustment if any
    weights = self.maybe_adjust(engine_state)
    
    # If no adjustment, use default weights from engine
    if weights is None:
        weights = engine_state.config.get("shape_weights", [1] * len(engine_state.config["shapes"]))
    
    # Select 'count' blocks using weighted random choice
    shapes = engine_state.config["shapes"]
    selected_shapes = [random.choices(shapes, weights=weights, k=1)[0] for _ in range(count)]
    
    # Convert shapes to blocks
    return [Block(shape) for shape in selected_shapes]
```

### 2. Game Engine Refactoring

#### 2.1 Update GameEngine Initialization
- [x] Add a `self.dda_algorithm` field to store the selected DDA algorithm
- [x] Use the DDA registry to create the algorithm based on config
- [x] Initialize the DDA with the appropriate parameters from config

```python
# In GameEngine.__init__()
from dda.registry import registry as dda_registry

# Create and initialize DDA algorithm
dda_name = self.config.get("dda_algorithm", "ThresholdDDA")
self.dda_algorithm = dda_registry.create_algorithm(dda_name)
dda_params = self.config.get("dda_params", {})
self.dda_algorithm.initialize(dda_params)
```

#### 2.2 Update _refill_preview Method
- [x] Replace the current block generation logic with DDA algorithm call
- [x] Use the DDA's `get_next_blocks()` method to get specific blocks

```python
def _refill_preview(self, target_count=3):
    """Refill the preview area with blocks up to the target count."""
    blocks_needed = target_count - len(self._preview_blocks)
    
    if blocks_needed > 0:
        # Get specific blocks from the DDA algorithm
        new_blocks = self.dda_algorithm.get_next_blocks(self, blocks_needed)
        
        # Add the new blocks to the preview (with default rotation 0)
        for block in new_blocks:
            self._preview_blocks.append((block, 0))
    
    # Select the first preview block if none is currently selected
    if self._selected_preview_index is None and self._preview_blocks:
        self._selected_preview_index = 0
```

#### 2.3 Modify _spawn Method
- [x] Update the _spawn method to use the DDA for block generation
- [x] Keep for backward compatibility but it should now use the DDA

```python
def _spawn(self) -> Block:
    """Create a new block using the DDA algorithm."""
    # Get a single block from the DDA
    blocks = self.dda_algorithm.get_next_blocks(self, 1)
    return blocks[0]
```

#### 2.4 Update _maybe_update_difficulty Method
- [x] Modify to maintain backward compatibility
- [x] This may be partially deprecated as difficulty is now handled by the DDA directly

```python
def _maybe_update_difficulty(self):
    """Update difficulty - maintained for backward compatibility.
    
    Note: This method is primarily kept for backward compatibility.
    Modern DDA algorithms will handle difficulty adjustment directly.
    """
    # For backward compatibility with threshold-based DDAs
    for thr, new_weights in self.config.get("difficulty_thresholds", []):
        if self.score >= thr:
            self.pool.weights = new_weights
```

### 3. DDA Algorithm Updates

#### 3.1 Update ThresholdDDA 
- [x] Implement the new `get_next_blocks()` method for ThresholdDDA
- [x] Ensure it properly handles threshold-based difficulty adjustment

```python
def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
    """Get the next blocks based on threshold-adjusted weights.
    
    Args:
        engine_state: The current game engine state
        count: Number of blocks to generate
        
    Returns:
        List[Block]: The specific blocks to be spawned
    """
    # First check for threshold crossing
    weights = self.maybe_adjust(engine_state)
    
    # If no adjustment, use current weights from engine
    if weights is None:
        weights = engine_state.pool.weights
    
    # Select 'count' shapes using the adjusted weights
    shapes = engine_state.config["shapes"]
    selected_shapes = [random.choices(shapes, weights=weights, k=1)[0] for _ in range(count)]
    
    # Convert shapes to blocks
    return [Block(shape) for shape in selected_shapes]
```

#### 3.2 Update IntervalDDA
- [x] Implement the new `get_next_blocks()` method for IntervalDDA
- [x] Take advantage of direct block selection to provide rescue/awkward blocks

```python
def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
    """Get the next blocks based on the interval pattern.
    
    This provides rescue or awkward blocks at specific intervals,
    giving direct control over specific shapes instead of just weights.
    
    Args:
        engine_state: The current game engine state
        count: Number of blocks to generate
        
    Returns:
        List[Block]: The specific blocks to be spawned
    """
    # Increment tray counter
    self.tray_count += 1
    
    # Get available shapes
    shapes = engine_state.config["shapes"]
    
    # Determine if this is a rescue or awkward interval
    is_rescue = (self.tray_count % self.steps_to_rescue == 0)
    is_awkward = (self.tray_count > 1) and (self.tray_count % self.steps_to_awkward == 0)
    
    # Initialize result list for blocks
    blocks = []
    
    # Handle rescue blocks
    if is_rescue:
        # Add specific rescue blocks
        rescue_shapes = [shapes[idx] for idx in self.rescue_blocks[:self.rescue_block_count]]
        blocks.extend([Block(shape) for shape in rescue_shapes])
    
    # Handle awkward blocks
    if is_awkward:
        # Add specific awkward blocks
        awkward_shapes = [shapes[idx] for idx in self.awkward_blocks[:self.awkward_block_count]]
        blocks.extend([Block(shape) for shape in awkward_shapes])
    
    # Fill remaining slots with random blocks
    remaining = count - len(blocks)
    if remaining > 0:
        # Use default weights for random selection
        weights = engine_state.pool.weights
        random_shapes = [random.choices(shapes, weights=weights, k=1)[0] for _ in range(remaining)]
        blocks.extend([Block(shape) for shape in random_shapes])
    
    # If we have more blocks than requested, trim the list
    return blocks[:count]
```

#### 3.3 Update MetricsDDA
- [x] Implement the new `get_next_blocks()` method for MetricsDDA
- [x] Use direct block selection based on game metrics

```python
def get_next_blocks(self, engine_state, count: int = 3) -> List[Block]:
    """Get the next blocks based on current game metrics.
    
    Args:
        engine_state: The current game engine state
        count: Number of blocks to generate
        
    Returns:
        List[Block]: The specific blocks to be spawned
    """
    # Get the danger score from metrics manager
    metrics = engine_state.metrics_manager
    danger_score = metrics.danger_score
    
    # Get shapes and determine selection strategy based on game state
    shapes = engine_state.config["shapes"]
    
    # Determine if we're in a rescue scenario
    is_rescue_needed = danger_score >= self.danger_threshold
    
    if is_rescue_needed:
        # Select smaller, simpler shapes for rescue
        rescue_indices = [0, 1, 2]  # Indices of simple shapes
        selected_indices = random.choices(rescue_indices, k=count)
    else:
        # Normal difficulty-based selection
        # Use the current difficulty level to determine max block size
        max_size = self.size_caps[min(self.current_difficulty, len(self.size_caps) - 1)]
        
        # Filter shapes that are appropriate for current difficulty
        valid_shapes = [(i, shape) for i, shape in enumerate(shapes) 
                        if self._get_shape_size(shape) <= max_size]
        
        if not valid_shapes:
            # Fallback if no shapes meet criteria
            valid_shapes = [(i, shape) for i, shape in enumerate(shapes)]
        
        # Select from valid shapes
        selected_indices = [random.choice(valid_shapes)[0] for _ in range(count)]
    
    # Convert selected indices to blocks
    return [Block(shapes[idx]) for idx in selected_indices]
```

### 4. Configuration and Registry Updates

#### 4.1 Update Default Configuration
- [x] Add any new configuration parameters needed for direct block selection
- [x] Ensure backward compatibility with existing configuration

#### 4.2 Update DDA Registry
- [x] No significant changes needed to the registry mechanism
- [x] Ensure all DDAs properly implement the new interface

### 5. Testing Framework

#### 5.1 Manual Testing Steps
- [x] Test each DDA algorithm individually
- [x] Verify that blocks are spawned according to the DDA's logic
- [x] Test with different difficulty levels and game states
- [x] Verify that the system gracefully handles edge cases

#### 5.2 Verification Steps
- [x] Verify ThresholdDDA works the same as before
- [x] Verify IntervalDDA now properly provides rescue/awkward blocks
- [x] Verify MetricsDDA adapts to game metrics correctly
- [x] Confirm compatibility with existing saves/configs

## Implementation Notes
- This approach gives DDAs direct control over block selection instead of relying on weights
- The backward compatibility layer ensures existing DDAs still work
- Use the existing Metrics Manager for MetricsDDA implementation
- All DDAs now have a consistent interface for block generation
- The approach makes it easier to implement more sophisticated DDAs in the future