# BlockHarness Documentation

## Overview
BlockHarness is a block-placement game platform similar to Tetris but with more customizable mechanics. The application allows for both interactive play and AI-driven simulations. The game consists of placing various shapes on a grid, clearing lines when they are filled, and earning points based on successful placements and line clears.

Key features:
- Multiple block shapes with customizable spawn probabilities
- Progressive difficulty scaling based on score thresholds
- Multiple modes of operation (Play, Simulation, AI)
- Streamlit-based parameter playground for testing game configurations
- Extensible AI interface for implementing different strategies

## Directory Structure
```
BlockHarness/
├── ai/                 # AI player implementations
│   └── Greedy1.py      # Basic greedy strategy implementation
├── config/             # Configuration management
│   ├── cli.py          # Command-line argument parsing
│   └── defaults.py     # Default game settings
├── controllers/        # Game flow controllers
│   ├── ai_controller.py        # AI-driven gameplay
│   ├── base_controller.py      # Base controller interface
│   ├── game_controller.py      # Interactive gameplay
│   └── simulation_controller.py # Simulation management
├── data/               # Game data storage
├── engine/             # Core game logic
│   ├── block.py        # Block representation
│   ├── block_pool.py   # Block generation and sampling
│   ├── board.py        # Game board and placement logic
│   ├── game_engine.py  # Main game mechanics and scoring
│   └── shapes.py       # Predefined block shapes
├── ui/                 # User interface components
├── app.py              # Streamlit parameter playground
├── play.py             # Entry point for gameplay
└── simulator.py        # Simulation driver
```

## Play Mode
Play mode provides an interactive game experience where the player can select and place blocks on the game board. This mode is accessed through the `play.py` script, which initializes a `SimulationController` with the configured settings.

Key features:
- Block selection from preview area
- Block rotation
- Score tracking
- Line clearing
- Progressive difficulty increases

To start play mode:
```
python play.py
```

## Simulation Mode
Simulation mode allows for running multiple game sessions with configurable parameters to analyze performance and test different settings. This is useful for balancing game difficulty and understanding how different block distributions affect gameplay outcomes.

The simulation mode can be accessed through:
1. `simulator.py` - For running multiple simulations with predefined parameters
2. `app.py` - A Streamlit application that provides an interactive interface for testing different parameters

Key features:
- Run multiple simulations with the same configuration
- Track statistics like average score, moves, and lines cleared
- Test different block weight distributions
- Visualize results using charts and statistics

To run simulations:
```
python simulator.py
```

To launch the parameter playground:
```
streamlit run app.py
```

## Configuration
The game's behavior can be customized through configuration parameters:

- **shapes**: Defines the available block shapes as coordinate lists
- **shape_weights**: Controls the probability distribution for spawning blocks
- **difficulty_thresholds**: Score thresholds at which block weights change to increase difficulty

Example configuration:
```python
CONFIG = {
    "shapes": SHAPES,  # Predefined shapes from engine/shapes.py
    "shape_weights": [2, 2, 2, 2, 1, 1, 1, 1],  # Initial weights
    "difficulty_thresholds": [
        (1000, [1, 2, 2, 2, 2, 2, 2, 3]),  # First difficulty increase
        (3000, [1, 1, 2, 3, 3, 3, 3, 4]),  # Second difficulty increase
    ],
}
```

Configuration can be provided through command-line arguments or by directly modifying the configuration files.

## AI
BlockHarness includes an AI framework for developing and testing automated block-placement strategies. 

The current implementation includes:
- **Greedy1**: A simple greedy algorithm that prioritizes immediate line clears

The AI controller manages the interaction between the AI player and the game engine, allowing the AI to:
1. Select blocks from the preview
2. Apply rotations
3. Choose optimal placement positions
4. Progress through the game automatically

The AI interface is designed to be extensible, allowing for the implementation of more sophisticated strategies by creating new classes in the `ai/` directory that implement the `choose_move` method.

To implement a new AI strategy:
1. Create a new file in the `ai/` directory
2. Implement a class with a `choose_move` method that returns a tuple of (row, col) or None
3. Update the controller to use your new AI implementation

---

## Scoring System
- Each line cleared: 100 points
- Combo bonus for multiple lines: 50 points per additional line
- Each block placed without clearing lines: 1 point

---

## Development Notes

### Game Engine
The engine directory contains the core game mechanics and logic that powers BlockHarness. It follows a modular design where each component has a specific responsibility:

#### shapes.py
This file defines the fundamental building blocks of the game - the different shapes that players can place on the board. It contains:
- `SHAPES`: A list of coordinate-based shape definitions where each shape is a list of (row, column) tuples
- Eight predefined shapes including single blocks, lines, L-shapes, T-shapes, and squares
- Each coordinate pair represents a cell in the shape relative to its top-left corner

#### block.py
The Block class encapsulates a shape with operations for manipulating it:
- `__init__`: Creates a block from a list of cell coordinates, calculating its dimensions
- `rotate_clockwise`: Implements the rotation logic for blocks, supporting 0-3 rotations (0°, 90°, 180°, 270°)
- Each rotation creates a new Block instance with transformed coordinates
- The implementation handles all rotation calculations by applying appropriate coordinate transformations

#### block_pool.py
This module manages the generation of blocks based on configurable probabilities:
- `BlockPool` class: Implements a weighted random generator for shapes
- Takes a list of shapes and their corresponding weights during initialization
- `sample` method: Returns a new randomly selected Block based on the current weights
- The weighting system allows for dynamic difficulty adjustments during gameplay

#### board.py
The Board class represents the game grid and handles block placement and line clearing:
- Default board size is 8×8, but can be customized
- `can_place`: Checks if a block can be placed at a specific position
- `place_block`: Adds a block to the grid at the specified position
- `clear_full_lines`: Scans both rows and columns for completions and clears them
- Line clearing is a key scoring mechanic - when a row or column is completely filled, it's cleared and points are awarded

#### game_engine.py
This is the central component that orchestrates all game mechanics:

**Core Game State**:
- Manages the board, score, lines cleared, and blocks placed
- Tracks game state including the block preview and whether the game is over
- Handles the block pool for weighted random block generation

**Preview System**:
- Maintains a list of upcoming blocks with their current rotations
- Allows selection, rotation, and placement of blocks from the preview
- Automatically refills the preview when blocks are used

**Block Placement**:
- `get_valid_placements`: Finds all valid positions for a block with a specific rotation
- `place_selected_block`: Places the currently selected block, updates score, and manages game state
- When a block is placed, any completed rows or columns are cleared

**Game Progression**:
- `_check_game_over`: Determines if the game has ended (no blocks can be placed)
- `_maybe_update_difficulty`: Adjusts block weights based on score thresholds
- Implements the scoring system with bonuses for multiple line clears

**Public API**:
- Provides a clean interface for controllers to interact with the game state
- Includes methods for block selection, rotation, placement, and state querying
- Handles all game rules enforcement internally, ensuring consistent gameplay

The engine is designed to be extensible and configurable, allowing for:
1. Custom block shapes and spawn probabilities
2. Progressive difficulty scaling
3. Various gameplay modes (human play, AI-driven, simulation)
4. Clean separation between game logic and presentation

This architecture makes it easy to implement new gameplay features, AI strategies, or user interfaces without modifying the core game mechanics.

## Controllers

### Controller Hierarchy
The BlockHarness controller architecture follows a hierarchical design with each controller extending functionality from its parent:

1. **BaseController**: The abstract base class that defines the core interface for game control
2. **GameController**: Extends BaseController with Pygame UI and interactive controls
3. **SimulationController**: Extends GameController with simulation capabilities
4. **AIController**: Extends BaseController with AI-driven gameplay

This inheritance structure allows for code reuse while specializing each controller for its specific purpose.

### BaseController
The BaseController serves as the foundation for all game controllers, providing essential methods for interacting with the game engine.

**Role**: Provides a common interface between the game engine and higher-level controllers.

**Functions**:
- `__init__(config)`: Initializes the controller with the provided configuration
- `restart_game()`: Resets the game with the current configuration
- `update_config(new_config)`: Updates the game configuration and restarts
- `select_block(index)`: Selects a block from the preview
- `rotate_block(rotations)`: Rotates the currently selected block
- `place_block(row, col)`: Places the currently selected block at the specified position
- `find_next_valid_block()`: Finds the next placeable block in the preview
- `get_game_state()`: Gets the current game state as a dictionary

### GameController
The GameController extends BaseController to provide a graphical user interface using Pygame.

**Role**: Handles user interaction and visual representation of the game state.

**Functions**:
- `__init__(config)`: Initializes Pygame and UI components
- `apply_config_changes()`: Applies changes from the sidebar config inputs
- `handle_board_click(x, y)`: Handles click on the game board to place a block
- `handle_preview_click(x, y)`: Handles click on the preview area to select a block
- `save_game_stats()`: Saves current game stats to CSV when game is over
- `restart_game()`: Resets the game and stats saving flag
- `handle_events()`: Processes user input events
- `draw()`: Renders the game state to the screen
- `loop()`: Runs the main game loop

### SimulationController
The SimulationController extends GameController to add simulation capabilities.

**Role**: Manages automated game simulations with customizable parameters for testing and analysis.

**Functions**:
- `__init__(config)`: Initializes simulation state variables and AI controller
- `restart_simulation()`: Restarts the game while preserving simulation state variables
- `start_simulation()`: Starts the AI simulation at the specified steps per second
- `abort_simulation()`: Stops the AI simulation and allows manual play
- `run_simulation_step()`: Executes one AI step in the simulation
- `save_simulation_stats(run_stats)`: Saves simulation run statistics to CSV
- `handle_events()`: Processes user input events with simulation handling
- `draw()`: Renders the game state with simulation information
- `loop()`: Runs the main game loop with simulation support

### AIController
The AIController extends BaseController to provide AI-driven gameplay.

**Role**: Uses various AI strategies to automate block selection, rotation, and placement.

**Functions**:
- `__init__(config)`: Initializes the AI controller and player
- `step()`: Performs a single AI-driven game step
- `run_simulation(num_steps)`: Runs the AI simulation for a specified number of steps or until game over

## Controller Interaction Flow

1. **User Gameplay Flow** (GameController):
   - User selects a block from preview → `handle_preview_click()` → `select_block()`
   - User rotates the block → Key press (R) → `rotate_block()`
   - User places the block → `handle_board_click()` → `place_block()`
   - Game updates visuals → `draw()`
   - Game over detection → `save_game_stats()`

2. **Simulation Flow** (SimulationController):
   - User starts simulation → `start_simulation()`
   - For each step → `run_simulation_step()` → AIController's `step()`
   - AI makes a move → `place_block()`
   - Game over detection → `save_simulation_stats()` → next run or end
   - Visual update → `draw()`

3. **AI Decision Process** (AIController):
   - AI selects block and rotation → `find_next_valid_block()`
   - AI evaluates possible placements → AIPlayer's `choose_move()`
   - AI places block → `place_block()`

This architecture enables seamless transitions between manual play and AI-driven simulations, with a common interface for interacting with the game engine.

## AI Gameplay Mechanics

### Simulation Flow in Detail

The BlockHarness simulation system consists of three primary components working together:

1. **SimulationController**: Orchestrates the entire simulation process
2. **AIController**: Manages AI decision-making and block placement
3. **AIPlayer**: Implements the specific strategy for choosing block placements

#### Simulation Lifecycle

The simulation process follows these stages:

1. **Initialization**:
   - The `SimulationController` is created with game configuration parameters
   - It internally creates an `AIController` instance, which in turn instantiates an `AIPlayer`
   - Both controllers maintain separate instances of the same game engine

2. **Simulation Start**:
   - User initiates simulation via UI controls in the sidebar
   - `start_simulation()` retrieves simulation parameters (steps per second, total runs)
   - Simulation state variables are initialized (run count, statistics tracking)
   - If the game was over, a fresh simulation run is started

3. **Simulation Execution**:
   - The main game loop in `loop()` checks if simulation is running
   - When enough time has elapsed (based on steps_per_second), `run_simulation_step()` is called
   - `run_simulation_step()` calls `AIController.step()` to execute one AI action
   - Game state is synchronized between AI engine and display engine

4. **AI Decision Process**:
   - `AIController.step()` manages the AI decision process:
     - First attempts to find a valid move for the currently selected block and rotation
     - If no valid move exists, finds a different block or rotation using `find_next_valid_block()`
     - Calls `AIPlayer.choose_move()` to determine the optimal placement
     - Executes the move by calling `place_block()`

5. **Move Evaluation** (in Greedy1.py):
   - `choose_move()` evaluates all valid placements for the given block and rotation
   - For each placement:
     - Creates a temporary board copy
     - Simulates the block placement
     - Calculates the score based on lines cleared
     - Returns the position with the highest score

6. **Game End and Statistics**:
   - When `AIController.engine.game_over` becomes true, the run is complete
   - Statistics are collected via `get_game_state()` and stored
   - If more runs are configured, `restart_simulation()` is called
   - Otherwise, simulation is marked complete and results are displayed

7. **Visualization**:
   - Throughout the process, `draw()` renders the current game state
   - The sidebar displays simulation progress (current run/total runs)

### Adding New AI Strategies

The BlockHarness architecture is designed to make adding new AI strategies straightforward without modifying the existing controller code. This is achieved through a simple interface pattern:

#### The AIPlayer Interface

All AI implementations must provide a `choose_move` method with the following signature:
```python
def choose_move(self, engine: GameEngine, block_index: int, rotation: int) -> Optional[Tuple[int, int]]:
    """Choose the best placement for a block.
    
    Args:
        engine: The game engine
        block_index: Index of the block to place
        rotation: Rotation to apply to the block
        
    Returns:
        Tuple of (row, col) for best placement or None if no valid placement
    """
```

#### Steps to Add a New AI Strategy:

1. **Create a New AI File**:
   - Create a new Python file in the `ai/` directory (e.g., `ai/MyStrategy.py`)
   - Implement an `AIPlayer` class with the `choose_move` method

2. **Implement the Strategy Logic**:
   - The strategy can use any approach to evaluate and select moves
   - Use the `engine` parameter to access game state and valid placements
   - Access available methods like `get_valid_placements()` to find legal moves
   - Return a tuple with row and column coordinates, or None if no move is possible

3. **Modify the AIController Initialization**:
   - Update the import statement in `ai_controller.py` to import your new AI class
   - Change the `self.ai_player = AIPlayer()` line to instantiate your new strategy

#### Example: Creating a Looking-Ahead AI Strategy

Here's an example of how to implement a new AI strategy that looks ahead to evaluate moves:

```python
# ai/LookAhead.py
from typing import Tuple, Optional
from copy import deepcopy

from engine.game_engine import GameEngine


class AIPlayer:
    """Look-ahead AI strategy that considers future blocks."""
    
    def choose_move(self, engine: GameEngine, block_index: int, rotation: int) -> Optional[Tuple[int, int]]:
        """Choose the best placement by looking ahead at future positions."""
        best_move = None
        best_score = float('-inf')
        
        # Get all valid placements for this block+rotation
        valid_placements = engine.get_valid_placements(block_index, rotation)
        
        if not valid_placements:
            return None
            
        # Score each placement
        for r, c in valid_placements:
            # Create a copy of the engine to simulate placement
            engine_copy = deepcopy(engine)
            
            # Select and place the block in our simulation
            engine_copy.select_preview_block(block_index)
            engine_copy.place_selected_block(r, c)
            
            # Evaluate the resulting position using both immediate lines cleared
            # and open space for future placements
            score = self._evaluate_position(engine_copy)
            
            if score > best_score:
                best_score = score
                best_move = (r, c)
                
        return best_move
    
    def _evaluate_position(self, engine: GameEngine) -> float:
        """Evaluate a board position based on multiple factors."""
        score = 0.0
        
        # Reward for score (which includes line clears)
        score += engine.score
        
        # Penalize for filled cells (encourages keeping the board clear)
        filled_cells = sum(1 for row in engine.board.grid for cell in row if cell)
        score -= filled_cells * 0.5
        
        # Check how many valid placements exist for next blocks (playability)
        next_block_options = 0
        for i in range(len(engine.get_preview_blocks())):
            for rot in range(4):  # Check all 4 rotations
                placements = engine.get_valid_placements(i, rot)
                next_block_options += len(placements)
        
        # Reward for having more options for future blocks
        score += next_block_options * 0.2
        
        return score
```

#### Modifying AIController to Use the New Strategy:

```python
# controllers/ai_controller.py
from typing import Dict, Optional, Tuple

from controllers.base_controller import BaseController
# Change this import
from ai.LookAhead import AIPlayer  # Import your new AI strategy


class AIController(BaseController):
    """Controller that uses an AI player to make gameplay decisions."""
    
    def __init__(self, config: Dict):
        """Initialize the AI controller with the provided configuration."""
        super().__init__(config)
        self.ai_player = AIPlayer()  # This line remains the same, but now uses LookAhead
```

### Making AIController Dynamic

For even greater flexibility, you can modify AIController to dynamically load AI strategies:

```python
def __init__(self, config: Dict, ai_strategy: str = "Greedy1"):
    """Initialize the AI controller with the provided configuration.
    
    Args:
        config: Game configuration dictionary
        ai_strategy: Name of the AI strategy to use
    """
    super().__init__(config)
    
    # Dynamically import the requested AI strategy
    try:
        # Import the module
        ai_module = importlib.import_module(f"ai.{ai_strategy}")
        # Get the AIPlayer class
        AIPlayerClass = getattr(ai_module, "AIPlayer")
        # Instantiate the AI player
        self.ai_player = AIPlayerClass()
    except (ImportError, AttributeError):
        print(f"Strategy {ai_strategy} not found, falling back to Greedy1")
        from ai.Greedy1 import AIPlayer
        self.ai_player = AIPlayer()
```

This approach allows you to:
1. Specify the AI strategy as a parameter
2. Add new strategies without any controller changes
3. Select different strategies at runtime

### Current Implementation: Greedy1

The current AI implementation in `Greedy1.py` employs a simple greedy strategy:

1. It evaluates all valid placements for the current block and rotation
2. For each placement, it simulates the move on a temporary board
3. It calculates the score based on the number of lines that would be cleared:
   - 100 points per line cleared
   - 50 additional points for each line beyond the first (combo bonus)
4. It selects the placement with the highest immediate score

This approach prioritizes immediate line clears without considering future consequences, making it a basic but effective strategy for testing the simulation system.

### Simulation Controller and AI Integration

The `SimulationController` integrates with the AI system through these key mechanisms:

1. **Isolation of Game State**:
   - The AI controller maintains its own game engine instance
   - This allows the simulation to run independently of the display
   - The display engine is synchronized with the AI engine after each step

2. **Configuration Sharing**:
   - When configuration changes are applied in the UI, they are also passed to the AI controller
   - This ensures both engines operate with identical settings

3. **Statistics Collection**:
   - The SimulationController collects and stores statistics from each completed run
   - These statistics are saved to CSV files for later analysis
   - At the end of all runs, a summary is printed to the console

4. **Visual Feedback**:
   - The sidebar displays current simulation status
   - Game visualization shows the AI's decisions in real-time
   - Visual speed is controlled by the steps_per_second parameter

Below is a line-by-line view of how **AIPlayer** and **AIController** are built, what each one actually does, and where their responsibilities meet the rest of the stack.  
Quotes are taken verbatim from the files so the mapping is explicit.

---

## 1. AIPlayer  (`ai/Greedy1.py`)

| Element | Exact code | Effect / state |
|---------|------------|----------------|
| **Imports** | `from engine.game_engine import GameEngine`  | Only needs the public read-only API of the engine. |
| **Class** | `class AIPlayer:` | No base class, no attributes on `self`. |
| **Method** | `def choose_move(self, engine: GameEngine, block_index: int, rotation: int) -> Tuple[int, int]:` | Pure function-style heuristic. Takes three inputs, returns a position or `None` (annotation mismatch noted earlier). |
| **Algorithm outline** | 1. `engine.get_valid_placements()` → set of `(r,c)`  
2. For each placement:  
 a. `deepcopy(engine.board)` to isolate simulation  
 b. grab the rotated block from `engine.get_preview_blocks()`  
 c. `tmp_board.place_block()` → `tmp_board.clear_full_lines()`  
 d. score = `100*cleared + 50*max(0,cleared-1)`  
3. Return best `(r,c)` | No game state is mutated inside the real engine; only the deep-copy. |

**Scope / side-effects**

* Holds **zero** persistent fields.  
* Never calls `engine.select_*`, `engine.place_selected_block`, or commits a move.  
* Purely advisory.

---

## 2. AIController  (`controllers/ai_controller.py`)

| Element | Exact code | Effect / state |
|---------|------------|----------------|
| **Inheritance** | `class AIController(BaseController):`  | Gains `self.engine`, selection/rotation helpers, restart logic. |
| **Composition** | `self.ai_player = AIPlayer()` in `__init__` | Owns exactly one AIPlayer instance. |
| **step()** (core loop) | 1. Abort if `self.engine.game_over`.  
2. Read currently **selected** preview block via `engine.get_selected_preview_index()`.  
  • If none is selected, nothing happens.  
3. Get current rotation from `engine.get_preview_blocks()`.  
4. Call `self.ai_player.choose_move(...)`.  
5. If a move is returned → `self.place_block(row,col)` (inherited helper → `GameEngine.place_selected_block`).  
6. If no move:  
 a. `find_next_valid_block()` (in GameEngine) → `(idx,rot)`  
 b. `select_block(idx)`, `rotate_block()` as needed.  
 c. Call `choose_move()` again and `place_block()` if possible. | **step()** performs selection/rotation/placement and therefore does mutate the real engine state. |
| **run_simulation()** | While not game-over and until `num_steps` exhausted, repeatedly calls `step()`; returns a dict summary. | Provides batch execution for outside callers (e.g. SimulationController). |

**Scope / side-effects**

* Responsible for **all** changes to `GameEngine` during automated play.  
* Delegates **only** the evaluation of candidate moves to the AIPlayer.

---

## 3. Relationship and separation of concerns

| Concern | Where it lives now | Comment (objective) |
|---------|-------------------|----------------------|
| **Game State Mutation** | AIController (`select_block`, `rotate_block`, `place_block`) | Kept out of AIPlayer. |
| **Move Evaluation / Heuristic** | AIPlayer (`choose_move`) | Kept out of AIController. |
| **Block-search fallback** (find next usable block) | AIController (`find_next_valid_block()` is called on engine, selection is done in controller) | Could in theory be part of an AI strategy, but currently treated as controller utility so that any AIPlayer only worries about a *single* block + rotation at a time. |
| **Board deep-copy scoring** | AIPlayer | This repeats part of scoring logic already in GameEngine but is required here because AIPlayer must not affect the real board. |

Nothing in the controller **has to** be in the player for the current contract to work, and vice-versa.  Each layer calls only the public API of the other:

* AIPlayer needs read-only queries from GameEngine; it never reaches into controller helpers.  
* AIController receives a position from AIPlayer and then uses its own inherited helpers to mutate the engine.

---

## 4. Cross-file view (other modules)

| File | Interaction with AI pieces | Notes |
|------|---------------------------|-------|
| **base_controller.py**  | Exposes generic helpers (`select_block`, `rotate_block`, `place_block`, `find_next_valid_block`) used verbatim by AIController. | Keeps UI-free facade separating control logic from UI layers. |
| **game_controller.py**  | Human-driven controller; shares the same helpers but no AI. | No overlap with AIPlayer logic. |
| **simulation_controller.py**  | Owns a **second** AIController to run automated steps, then copies its engine into the on-screen GameController. | AIPlayer remains untouched. |
| **game_engine.py**  | Supplies the immutable information and mutators used by both AI layers. | None of the AI or controller code duplicates line-clear rules except the scoring copy inside AIPlayer. |

---

## 5. Are any responsibilities misplaced?

* **Selection & rotation logic** (deciding *which* preview block to play) currently sits in AIController, not AIPlayer.  
  *Moving it into AIPlayer would couple the heuristic to multi-block strategy and to engine helper calls; the present split keeps AIPlayer purely evaluative. This is a design choice, not an error.*

* **Board-copy scoring code** inside AIPlayer duplicates the numeric scoring formula in `GameEngine.place_selected_block()`.  
  Consolidating that formula into a shared utility would avoid maintaining two sources, but the duplication itself is deliberate to keep AIPlayer side-effect-free.

* **Type annotation** of `choose_move` should be `Optional[Tuple[int,int]]`. This is a minor correctness fix inside AIPlayer and does not affect separation. 

Apart from the annotation mismatch and the duplicated scoring expression, the separation is clean: AIPlayer is *policy*, AIController is *actor*.

