# Detailed Plan for Metrics Manager Improvements

This document outlines a step-by-step strategy for correctly computing the following metrics in `MetricsManager` without allowing block rotations:

1. **Best Fit Block**: Identify the block shape that clears the most lines when placed.
2. **Best Fit Place**: Record the exact `(row, column)` coordinates where that block achieves its maximum clear.
3. **Game Over Block**: Find a shape that cannot fit on the current board and will not fit on any optimally simulated future board after placing all preview blocks.
4. **Opportunity**: A boolean flag indicating the presence of a game-over block.

---

## Core Variables

### Configuration
```python
shapes: Dict[str, List[Tuple[int, int]]]  # All fixed block shapes from game config
```

### Board State
```python
board: Board  # Current game board instance
preview_blocks: List[Block]  # Upcoming blocks in preview/pool
```

### Best Fit Metrics
```python
best_fit_block: str  # Name of shape clearing most lines (default: "None")
best_fit_position: Tuple[int, int]  # (row, col) for best placement (default: (-1, -1))
max_lines_cleared: int  # Highest count of lines cleared (default: 0)
```

### Game Over Metrics
```python
game_over_block: str  # Name of shape causing game over (default: "None")
opportunity: bool  # True if game-over block exists (default: False)
```

### Simulation Variables
```python
future_boards: List[Board]  # Collection of possible future board states
```

---

## Helper Functions

### 1. Position & Placement Testing

```python
def can_place_anywhere(board: Board, block: Block) -> bool:
    """Check if block can be placed anywhere on the board."""
    for r in range(board.rows):
        for c in range(board.cols):
            if board.can_place(block, r, c):
                return True
    return False

def count_lines(cleared_cells: Set[Tuple[int, int]]) -> int:
    """Count number of distinct rows and columns in the cleared set."""
    rows = set()
    cols = set()
    
    for r, c in cleared_cells:
        rows.add(r)
        cols.add(c)
        
    return len(rows) + len(cols)

def find_valid_placements(board: Board, block: Block) -> List[Tuple[int, int, int]]:
    """Find all valid placements for a block with their line clear counts.
    
    Returns:
        List of tuples (row, col, lines_cleared)
    """
    placements = []
    
    for r in range(board.rows):
        for c in range(board.cols):
            if board.can_place(block, r, c):
                # Simulate placement
                temp_board = Board.from_grid(board.grid)
                temp_board.place_block(block, r, c)
                cleared = temp_board.find_full_lines()
                lines = count_lines(cleared)
                
                placements.append((r, c, lines))
    
    return placements
```

### 2. Board Simulation

```python
def place_and_clear(board: Board, block: Block, position: Tuple[int, int]) -> int:
    """Place block at position and clear resulting lines. Returns lines cleared."""
    r, c = position
    board.place_block(block, r, c)
    cleared = board.find_full_lines()
    if cleared:
        board.clear_cells(cleared)
        return count_lines(cleared)
    return 0

def generate_possible_futures(board: Board, preview_blocks: List[Block], 
                             max_futures: int = 10) -> List[Board]:
    """Generate multiple possible future boards by simulating different placement strategies.
    
    Args:
        board: Current board state
        preview_blocks: List of upcoming blocks
        max_futures: Maximum number of futures to generate
        
    Returns:
        List of possible future board states
    """
    if not preview_blocks:
        return [Board.from_grid(board.grid)]
    
    futures = []
    # Queue of (board_state, remaining_blocks)
    queue = [(Board.from_grid(board.grid), list(preview_blocks))]
    
    while queue and len(futures) < max_futures:
        current, remaining = queue.pop(0)
        
        if not remaining:
            futures.append(current)
            continue
        
        # Get next block to place
        block = remaining[0]
        next_remaining = remaining[1:]
        
        # Find all valid placements
        placements = find_valid_placements(current, block)
        if not placements:
            # Can't place this block, so this branch ends
            futures.append(current)
            continue
        
        # Sort by lines cleared (descending)
        placements.sort(key=lambda x: x[2], reverse=True)
        
        # Add max line clear placement
        best_board = Board.from_grid(current.grid)
        place_and_clear(best_board, block, (placements[0][0], placements[0][1]))
        queue.append((best_board, next_remaining))
        
        # Add lowest row placement if different
        lowest_placement = min(placements, key=lambda x: x[0])
        if lowest_placement != placements[0]:
            low_board = Board.from_grid(current.grid)
            place_and_clear(low_board, block, (lowest_placement[0], lowest_placement[1]))
            queue.append((low_board, next_remaining))
        
        # Add central placement if available and different
        central_col = current.cols // 2
        central_placements = [p for p in placements if p[1] == central_col]
        if central_placements and central_placements[0] not in [placements[0], lowest_placement]:
            center_board = Board.from_grid(current.grid)
            place_and_clear(center_board, block, (central_placements[0][0], central_placements[0][1]))
            queue.append((center_board, next_remaining))
    
    # If we couldn't generate any futures, return current board
    if not futures:
        futures.append(Board.from_grid(board.grid))
    
    return futures
```

---

## Core Algorithms

### 1. Best Fit Block & Position

```python
def compute_best_fit(shapes: Dict[str, List[Tuple[int, int]]], board: Board) -> Tuple[str, Tuple[int, int], int]:
    """Identify block shape and position that clears the most lines.
    
    Returns:
        Tuple of (block_name, (row, col), lines_cleared)
    """
    best_block_name = "None"
    best_position = (-1, -1)
    max_lines_cleared = 0
    
    # Track fallback when no lines can be cleared
    fallback_block = "None"
    fallback_position = (-1, -1)
    min_height = board.rows  # For tie-breaking on height
    
    for shape_name, cells in shapes.items():
        block = Block(cells)
        
        for r in range(board.rows):
            for c in range(board.cols):
                if board.can_place(block, r, c):
                    # Track as fallback (prefer higher placements)
                    if fallback_block == "None" or r < min_height:
                        fallback_block = shape_name
                        fallback_position = (r, c)
                        min_height = r
                    
                    # Simulate placement
                    temp_board = Board.from_grid(board.grid)
                    temp_board.place_block(block, r, c)
                    cleared = temp_board.find_full_lines()
                    lines = count_lines(cleared)
                    
                    # Update if better
                    if lines > max_lines_cleared:
                        max_lines_cleared = lines
                        best_block_name = shape_name
                        best_position = (r, c)
                    elif lines == max_lines_cleared > 0:
                        # Tie-breaking: prefer higher placements (lower r)
                        if r < best_position[0]:
                            best_block_name = shape_name
                            best_position = (r, c)
                        # If same height, prefer more centered columns
                        elif r == best_position[0]:
                            board_center = board.cols // 2
                            if abs(c - board_center) < abs(best_position[1] - board_center):
                                best_block_name = shape_name
                                best_position = (r, c)
    
    # If no blocks can clear lines, use fallback
    if max_lines_cleared == 0:
        best_block_name = fallback_block
        best_position = fallback_position
    
    return (best_block_name, best_position, max_lines_cleared)
```

### 2. Game Over Block & Opportunity

```python
def find_game_over_block(shapes: Dict[str, List[Tuple[int, int]]], 
                        board: Board, 
                        preview_blocks: List[Block]) -> Tuple[bool, str]:
    """Find a block that cannot be placed now and won't fit after placing preview blocks.
    
    Returns:
        Tuple of (opportunity_exists, block_name)
    """
    # Generate multiple possible future boards
    future_boards = generate_possible_futures(board, preview_blocks)
    
    for shape_name, cells in shapes.items():
        block = Block(cells)
        
        # Check if block can be placed NOW
        fits_now = can_place_anywhere(board, block)
        
        if not fits_now:
            # If it can't fit now, check if it fits in ANY possible future
            fits_in_any_future = False
            
            for future in future_boards:
                if can_place_anywhere(future, block):
                    fits_in_any_future = True
                    break
            
            # If block can't fit now AND won't fit in any future → game over block
            if not fits_in_any_future:
                return (True, shape_name)
    
    # No game over block found
    return (False, "None")
```

---

## Integration & Flow

### MetricsManager Method Implementation

```python
def update_game_state_metrics(self, board: Board, preview_blocks: List[Block]) -> None:
    """Update all game state metrics based on current board and preview."""
    
    # 1. Calculate occupancy, fragmentation, and danger metrics (existing code)
    filled_cells = sum(sum(row) for row in board.grid)
    total_cells = board.rows * board.cols
    self.occupancy_ratio = filled_cells / total_cells
    
    # Find empty clusters using BFS
    empty_clusters = self._find_empty_clusters(board)
    self.fragmentation_count = len(empty_clusters)
    
    # Calculate largest empty region
    if empty_clusters:
        largest_cluster_size = max(len(cluster) for cluster in empty_clusters)
        total_empty_cells = total_cells - filled_cells
        self.largest_empty_region = largest_cluster_size / max(1, total_empty_cells)
    else:
        self.largest_empty_region = 0.0
    
    # Calculate danger score (existing formula)
    inv_frag = 1.0 / max(1, self.fragmentation_count)
    inv_largest = 1.0 - self.largest_empty_region
    self.danger_score = (
        self.occupancy_weight * self.occupancy_ratio +
        self.fragmentation_weight * inv_frag +
        self.inv_largest_weight * inv_largest
    )
    
    # 2. Calculate best fit block and position
    shapes = self.config["shapes"]
    self.best_fit_block, self.best_fit_position, lines = compute_best_fit(shapes, board)
    
    # 3. Check for game over block and opportunity
    self.opportunity, self.game_over_block = find_game_over_block(shapes, board, preview_blocks)
    
    # 4. Update imminent threat based on current state
    self.imminent_threat = self._check_imminent_threat(board, preview_blocks)
```

---

## Testing & Validation

### 1. Unit Tests

```python
def test_best_fit_block():
    """Test best fit block calculation with various board states."""
    # Test cases:
    # 1. Empty board (should prefer highest position)
    # 2. Board with gaps that can be filled
    # 3. Board with multiple line clear possibilities
    # 4. Board with same line clear count but different heights
    # 5. Board where no lines can be cleared
    
def test_game_over_detection():
    """Test game over block and opportunity detection."""
    # Test cases:
    # 1. Block that doesn't fit now, but will fit after preview blocks
    # 2. Block that doesn't fit now and won't fit after any preview arrangement
    # 3. All blocks fit now and in future
    # 4. Empty preview (should use current board only)
    # 5. Block fits on some future boards but not others
```

### 2. Edge Cases

```python
def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # 1. Nearly full board with only specific shapes fitting
    # 2. Empty board
    # 3. Board with only one possible placement spot
    # 4. Preview list is empty
    # 5. Every block can be placed now, but none after preview
```

### 3. Test Data Generation

```python
def generate_test_boards():
    """Generate test boards with known outcomes."""
    # 1. Board setup with known best fit
    # 2. Board with exactly one impossible block
    # 3. Board with multiple line clear options
    # 4. Board with no line clear options but multiple fit options
    # 5. Create test cases with known optimal/future placements
```

---

## Implementation Notes

1. **Efficiency Considerations**:
   - Use early exit in can_place_anywhere when a valid position is found
   - Limit number of future boards generated to prevent combinatorial explosion
   - Consider caching results for repetitive calculations

2. **Accuracy Priorities**:
   - Best fit block must consider ALL possible shapes, not just preview blocks
   - Game over detection must check "can't place now AND can't place in future"
   - Multiple possible futures should be considered, not just optimal placements

3. **Edge Case Handling**:
   - Handle empty preview list by checking only the current board
   - When no blocks can clear lines, select the highest placeable block
   - When no blocks can be placed anywhere, report "None" for best fit

4. **Future Extensibility**:
   - Design algorithms to handle potential changes in block behavior
   - Keep core metrics separate from display/reporting logic
   - Document assumptions about board and block behavior
---

**Important**: This is a planning document. Do not modify existing code until the plan is reviewed and approved.
---