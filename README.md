# BlockHarness 🧩

BlockHarness is a simulation environment and parameter tuning testbed for a Tetris-like block-dropping game powered by a simple AI player. It provides a web interface using Streamlit to configure game parameters, run multiple simulations, and analyze the AI's performance based on metrics like score, lines cleared, and blocks placed.

## Features

*   **Tetris-like Game Engine:** Core logic for block spawning, placement, line clearing, and scoring.
*   **Configurable Parameters:** Adjust shape spawn probabilities and difficulty scaling based on score thresholds.
*   **Simple AI Player:** A greedy AI that chooses moves based on maximizing immediate line clears.
*   **Streamlit UI:** An interactive "Parameter Playground" to configure simulations and view results.
*   **Simulation Runner:** Run batches of simulations to test parameter effectiveness.
*   **Performance Analysis:** Basic statistical summary and charts for simulation results (Score, Moves, Lines).
*   **Dynamic Difficulty Adjustment:** Adaptive block generation based on player performance metrics.

## How it Works

BlockHarness simulates games played by a simple AI. The goal is often to test how different game parameters influence the AI's ability to score points or survive longer.

### Core Components

1.  **`engine/`**: Contains the core game logic.
    *   `game_engine.py`: Manages the main game loop, state (score, lines, blocks), block spawning, move validation, placement, line clearing, scoring, and difficulty adjustments.
    *   `board.py`: Represents the game board (grid) and handles block placement, collision detection, and line clearing logic.
    *   `block.py`: (Implicitly used) Defines the structure and rotation of different block shapes (defined in `shapes.py`).
    *   `block_pool.py`: Manages the pool of upcoming blocks with dynamic difficulty adjustment. It generates blocks based on player performance metrics, providing best-fit blocks to help players when they struggle and challenging game-over blocks when they perform well.
    *   `ai_player.py`: Implements the AI logic. The current AI uses a greedy heuristic: it simulates placing the current block in all valid positions and chooses the one that clears the most lines *immediately*.

2.  **`app.py`**: The main Streamlit application.
    *   Defines the UI ("Parameter Playground") with input fields for shape weights, difficulty thresholds, and the number of simulations.
    *   Takes user inputs to configure the `GameEngine`.
    *   Runs the specified number of simulations by repeatedly:
        *   Initializing a `GameEngine`.
        *   Creating an `AIPlayer`.
        *   Spawning the first block.
        *   Entering a loop where the `AIPlayer` chooses a move, the `GameEngine` places the block, clears lines, updates the score, potentially adjusts difficulty, and spawns the next block.
        *   The loop continues until the `AIPlayer` cannot find a valid move (`engine.no_move_left()`).
    *   Collects results (Score, Moves, Lines) from each simulation run.
    *   Uses `pandas` to calculate descriptive statistics (mean, std dev, min, max, etc.) of the results across all runs.
    *   Displays the statistics and bar charts of the results in the Streamlit UI.

3.  **`shapes.py`**: Defines the different block shapes available in the game.

4.  **`play.py`**: (Likely) A simpler script to run or potentially visualize a single game instance (its exact function requires inspection).

5.  **`requirements.txt`**: Lists the Python dependencies (`streamlit`, `pandas`, `pygame`). `pygame` is likely used by the underlying engine or potentially for a graphical version run via `play.py`, even if not directly imported in `app.py`.

### Simulation Flow (via `app.py`)

1.  User configures parameters (weights, thresholds, run count) in the Streamlit UI.
2.  User clicks "Run".
3.  `app.py` loops `runs` times:
    *   Creates `GameEngine` with config.
    *   Creates `AIPlayer`.
    *   `GameEngine` spawns the first block (`engine.spawn()`).
    *   **Game Loop:**
        *   Check if any valid moves exist (`engine.no_move_left()`). If not, end simulation.
        *   `AIPlayer` evaluates all valid moves by simulating them on a *copy* of the board and selects the move clearing the most lines (`ai.choose(engine)`).
        *   `GameEngine` places the block at the chosen location (`engine.place(r, c)`).
            *   Board state is updated.
            *   Completed lines are cleared.
            *   Score and line counts are updated.
            *   Difficulty might be updated based on the new score (`engine._maybe_update_difficulty()`).
        *   `GameEngine` spawns the next block (`engine.spawn()`).
        *   Repeat game loop.
    *   Store final score, moves, and lines for the completed simulation.
4.  After all simulations, aggregate results using `pandas`.
5.  Display results (table and charts) in the Streamlit UI.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd BlockHarness
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

### Parameter Playground (Web UI)

1.  Make sure you are in the project's root directory (`BlockHarness`) and your virtual environment is activated.
2.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
3.  Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).
4.  Use the interface to:
    *   Adjust the spawn weights for each shape (higher values mean higher probability).
    *   Set score thresholds and the corresponding weights that should be applied when those scores are reached.
    *   Specify the number of simulations to run.
    *   Click the "▶️ Run" button.
5.  Wait for the simulations to complete. The results (statistics and charts) will be displayed on the page.

### Other Scripts (e.g., `play.py`)

*   To understand how to run `play.py` or other scripts, you may need to examine their contents:
    ```bash
    python play.py --help  # Check if it has command-line arguments
    # or simply try running it
    python play.py
    ```
    (Further investigation needed to document `play.py` accurately).

## Configuration Files

*   **`shapes.py`**: Defines the block shapes used by the game. Modify this file to change the available pieces.
*   **`config/`**: This directory might contain other configuration files, although none were explicitly used by `app.py` or `game_engine.py`. Explore this directory if further customization is needed.

## Dependencies

*   **Streamlit:** For creating the interactive web UI.
*   **Pandas:** For data manipulation and analysis of simulation results.
*   **Pygame:** Likely used for game logic internals (e.g., potentially handling sprites or basic graphics if `play.py` offers visualization) or required by a sub-dependency.

## Block Generation Algorithm

The system uses an adaptive block generation algorithm that adjusts based on player performance:

### Key Metrics
- **Clear Rate**: Ratio of lines cleared to moves made
- **Score**: Current player score
- **Best Fit Block**: Block that would clear the most lines on the current board
- **Game Over Block**: Block that cannot be placed anywhere on the current board

### Algorithm Behavior
1. For players with **low score** (below score threshold):
   - When clear rate is **low**: Generates helpful "best fit" blocks to assist the player
   - When clear rate is **medium**: Generates best fit blocks in every 2nd tray
   - When clear rate is **high**: Generates best fit blocks in every 3rd tray

2. For players with **high score** (above score threshold):
   - Occasionally generates challenging "game over" blocks to increase difficulty

This dynamic system ensures that the game maintains an appropriate difficulty level based on player skill, providing assistance when needed and increasing challenge as players improve. 