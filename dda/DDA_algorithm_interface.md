# DDA Algorithm Interface Documentation

This document outlines the standard interface for Dynamic Difficulty Adjustment (DDA) algorithms in the BlockHarness project.

## Interface Overview

All DDA algorithms must inherit from `BaseDDAAlgorithm` and implement its required methods. The base class provides default implementations for some methods that can be overridden if needed.

## Required Methods

### `initialize(self, config_params: Dict[str, Any]) -> None`

This method initializes the algorithm with configuration parameters.

**Parameters:**
- `config_params`: Dictionary containing configuration parameters specific to this algorithm.

**Implementation Requirements:**
- Must store any configuration values needed by the algorithm
- Should validate input parameters and set reasonable defaults if needed
- Should not rely on any game state (that's provided later to `maybe_adjust()`)

### `maybe_adjust(self, engine_state) -> Optional[List[int]]`

This method checks the game state and determines if the difficulty needs to be adjusted.

**Parameters:**
- `engine_state`: The current game engine state

**Returns:**
- `Optional[List[int]]`: New shape weights if adjustment is needed, `None` otherwise

**Implementation Requirements:**
- Should analyze the game state to determine if adjustment is needed
- If adjustment is needed, return a list of weights with the same length as the shapes
- If no adjustment is needed, return `None`

## Optional Methods with Default Implementations

### `get_next_blocks(self, engine_state, count: int = 3) -> List[Block]`

This method generates the next set of blocks for the game. The default implementation uses `maybe_adjust()` to determine whether to adjust block weights.

**Parameters:**
- `engine_state`: The current game engine state
- `count`: Number of blocks to generate (default 3)

**Returns:**
- `List[Block]`: The specific blocks to be spawned in the preview tray

**Default Implementation:**
- Calls `maybe_adjust()` to get new weights if adjustment is needed
- Falls back to default weights from the engine configuration if no adjustment
- Ensures weights match the number of shapes
- Uses weighted random selection to choose blocks
- Returns a list of blocks

**When to Override:**
- If your algorithm needs direct control over specific block selection
- If you need to use factors other than just weights to determine blocks
- If you need special handling for specific game situations

### `name(self) -> str`

This property returns the algorithm name.

**Returns:**
- `str`: The name of the algorithm

**Default Implementation:**
- Returns the class name

**When to Override:**
- If you need a custom name different from the class name

## Class Attributes

### `display_name: str`

This class attribute specifies the display name for the algorithm in the UI.

**Default Value:**
- `"Abstract DDA Algorithm"`

**Implementation Requirement:**
- Each DDA algorithm subclass should set this to a user-friendly name

## Initialization and Registration

To make your DDA algorithm available in the system:

1. Implement the required methods
2. Set the `display_name` class attribute
3. Register your algorithm with the registry:

```python
from dda.registry import registry

# Option 1: Automatic registration on import
registry.register(YourDDAAlgorithm)

# Option 2: In the main file
registry.register(YourDDAAlgorithm)
```

## Using the Factory Method

The recommended way to create and initialize a DDA algorithm is through the registry's factory method:

```python
from dda.registry import registry

# Create and initialize the algorithm
algorithm = registry.create_and_initialize_algorithm(
    "YourDDAAlgorithm", 
    config_params
)
```

This ensures consistent initialization across all algorithms. 