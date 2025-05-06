# BestFitDDA Implementation

## Overview

This document details the implementation of a new Dynamic Difficulty Adjustment (DDA) algorithm called `BestFitDDA` for the BlockHarness game. The algorithm intelligently generates blocks based on the player's performance metrics, focusing on "best-fit" blocks that can clear lines and strategically introducing "game-over" blocks when appropriate.

## Key Features

1. **Best-Fit Block Generation**: The algorithm strategically includes blocks that can clear lines on the current board state.
2. **Dynamic Difficulty via L Factor**: Adjusts the frequency of best-fit blocks based on the player's clear rate:
   - High clear rate (≥ 0.8) → L=3 (best-fit every 3rd tray)
   - Medium clear rate (≥ 0.5 but < 0.8) → L=2 (best-fit every 2nd tray)
   - Low clear rate (< 0.5) → L=1 (best-fit every tray)
3. **Game-Over Opportunity**: After the player reaches a score threshold (default: 1000), the algorithm may introduce a block that will lead to game over.

## Implementation Details

### Files Created/Modified

1. `BlockHarness/dda/best_fit_dda.py` - Main implementation of the BestFitDDA algorithm
2. `BlockHarness/dda/__init__.py` - Added import for the new DDA class
3. `BlockHarness/config/defaults.py` - Added configuration parameters for BestFitDDA

### Core Algorithm Logic

The algorithm works by:

1. Tracking the player's clear rate (lines cleared / moves)
2. Adjusting the L factor (frequency of best-fit block generation) based on clear rate
3. Checking for game-over opportunities once the player reaches a score threshold
4. Generating blocks based on these factors

### Class Structure

The `BestFitDDA` class extends `BaseDDAAlgorithm` and implements:

- `initialize()`: Sets up configuration parameters
- `maybe_adjust()`: Determines if weights need to be adjusted
- `get_next_blocks()`: Generates the next set of blocks
- Helper methods for creating weights arrays

### Configuration

The algorithm can be configured with these parameters:

```python
"best_fit_dda": {
    "low_clear_rate": 0.5,      # Threshold for L=1
    "high_clear_rate": 0.8,     # Threshold for L=3
    "score_threshold": 1000     # Score threshold for game-over opportunity
}
```

## Usage

To use this DDA algorithm in the game:

1. Select "BestFitDDA" as the DDA algorithm in the game configuration
2. The algorithm will appear in the dropdown menu as "Best-Fit Adaptive"

## Testing

To test the implementation:

1. Run the game with BestFitDDA enabled
2. Monitor the generated blocks as you play:
   - Low clear rate should give more best-fit blocks
   - High clear rate should give fewer best-fit blocks
   - After reaching the score threshold, game-over blocks may appear

## Future Improvements

Potential enhancements:

1. Add a configurable parameter for 'n' (number of best-fit blocks per tray)
2. Implement different strategies for different game phases (early, mid, late)
3. Add emotional state consideration to further refine block generation
4. Implement more sophisticated game-over probability based on player skill 