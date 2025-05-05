# utils/metrics_manager.py
from typing import Dict, List, Set, Tuple, Optional, Deque
from collections import deque
import time
from engine.board import Board
from engine.block import Block


class MetricsManager:
    """Manages game metrics collection and calculation."""

    def __init__(self, config: Dict):
        """Initialize the metrics manager with config parameters.
        
        Args:
            config: Game configuration dictionary
        """
        self.config = config
        
        # Weights for danger score calculation
        self.occupancy_weight = config["metrics_weights"]["occupancy"]  
        self.fragmentation_weight = config["metrics_weights"]["fragmentation"]
        self.inv_largest_weight = config["metrics_weights"]["inv_largest"]
        
        # Flow parameters
        self.low_clear = config["metrics_flow"]["low_clear"]
        self.high_clear = config["metrics_flow"]["high_clear"]
        self.danger_cut = config["metrics_flow"]["danger_cut"]
        
        # Timing parameters
        self.max_time_per_move = config["metrics_timing"]["max_time_per_move"]
        
        # Initialize game analysis metrics
        self.best_fit_block = "None"
        self.opportunity = False
        self.game_over_block = "None"
        
        # Initialize game state metrics
        self.imminent_threat = False
        self.occupancy_ratio = 0.0
        self.fragmentation_count = 0
        self.largest_empty_region = 1.0
        self.danger_score = 0.0
        self.phase = "early"
        
        # Initialize player state metrics
        self.move_count = 0
        self.lines_cleared = 0
        self.score = 0
        self.clear_rate = 0.0
        self.recent_clears = deque(maxlen=10)  # Ring buffer for last 10 clears
        self.perf_band = "OK"
        self.player_level = "Novice"
        self.emotional_state = "Calm"
        self.time_per_move = 0.0
        self.avg_time_per_move = 0.0
        self._move_times = deque(maxlen=10)  # Ring buffer for last 10 move times
        self.placement_efficiency = 0.0  # Placeholder for future implementation
        self.mistake_flag = False
        self.mistake_count = 0
        self.mistake_rate = 0.0
        self._recent_mistakes = deque([0] * 10, maxlen=10)  # Ring buffer for last 10 mistakes
        
        # Timing tracking
        self._last_move_start_time = time.time()
        
        # Shape names directly from shapes.py comments for consistency
        self.shape_names = [
            "single",
            "1×2",
            "2×2 square",
            "3×1 line",
            "L-shape",
            "long L-shape",
            "T-shape",
            "Z-shape",
            "S-shape",
            "Plus-shape",
            "longT-shape"
        ]
    
    def start_move_timer(self) -> None:
        """Start timing a new move."""
        self._last_move_start_time = time.time()
    
    def record_move_completion(self, lines_cleared: int) -> None:
        """Record completion of a move with timing.
        
        Args:
            lines_cleared: Number of lines cleared in this move
        """
        # Calculate time for this move
        current_time = time.time()
        self.time_per_move = current_time - self._last_move_start_time
        
        # Update move tracking
        self.move_count += 1
        self.lines_cleared += lines_cleared
        
        # Update ring buffers
        self._move_times.append(self.time_per_move)
        self.recent_clears.append(lines_cleared)
        
        # Calculate average time per move
        if self._move_times:
            self.avg_time_per_move = sum(self._move_times) / len(self._move_times)
        
        # Calculate clear rate
        self.clear_rate = self.lines_cleared / max(1, self.move_count)
        
        # Update derived metrics
        self._update_perf_band()
        self._update_player_level()
        self._update_emotional_state()
        self._update_phase()
        
        # Start timing for next move
        self.start_move_timer()
    
    def record_mistake(self) -> None:
        """Record an attempt to place a block where it doesn't fit."""
        self.mistake_flag = True
        self.mistake_count += 1
        
        # Update recent mistakes
        self._recent_mistakes.append(1)
        
        # Calculate mistake rate
        self.mistake_rate = self.mistake_count / max(1, self.move_count)
    
    def update_game_state_metrics(self, board: Board, preview_blocks: List[Tuple[Block, int]]) -> None:
        """Update game state metrics based on current board and preview.
        
        Args:
            board: Current game board
            preview_blocks: List of preview blocks with rotations
        """
        # Calculate occupancy ratio
        filled_cells = sum(sum(row) for row in board.grid)
        total_cells = board.rows * board.cols
        self.occupancy_ratio = filled_cells / total_cells
        
        # Find empty clusters using BFS
        empty_clusters = self._find_empty_clusters(board)
        self.fragmentation_count = len(empty_clusters)
        
        # Calculate largest empty region ratio
        if empty_clusters:
            largest_cluster_size = max(len(cluster) for cluster in empty_clusters)
            total_empty_cells = total_cells - filled_cells
            self.largest_empty_region = largest_cluster_size / max(1, total_empty_cells)
        else:
            self.largest_empty_region = 0.0
        
        # Calculate danger score
        inv_frag = 1.0 / max(1, self.fragmentation_count)
        inv_largest = 1.0 - self.largest_empty_region
        self.danger_score = (
            self.occupancy_weight * self.occupancy_ratio +
            self.fragmentation_weight * inv_frag +
            self.inv_largest_weight * inv_largest
        )
        
        # Check for imminent threat
        self.imminent_threat = self._check_imminent_threat(board, preview_blocks)
        
        # Calculate game analysis metrics
        self._update_game_analysis_metrics(board, preview_blocks)
    
    def _update_game_analysis_metrics(self, board: Board, preview_blocks: List[Tuple[Block, int]]) -> None:
        """Update game analysis metrics based on the current board state.
        
        Args:
            board: Current game board
            preview_blocks: List of preview blocks with rotations
        """
        # Get all possible blocks from the shapes configuration
        all_shapes = self.config["shapes"]
        
        # Find the best fit block (one that clears the most lines)
        self.best_fit_block = self._find_best_fit_block(board, all_shapes)
        
        # Check for game end opportunity and game over block after preview blocks
        self.opportunity, self.game_over_block = self._check_game_end_opportunity(board, all_shapes, preview_blocks)
    
    def _find_best_fit_block(self, board: Board, shapes: List[List[List[int]]]) -> str:
        """Find block that clears the most lines when placed on the board.
        
        Args:
            board: Current game board
            shapes: List of all possible block shapes
            
        Returns:
            String name of the best fit block or "None" if no block clears a line
        """
        best_block_idx = -1
        max_lines_cleared = 0
        
        # Try each block shape
        for shape_idx, shape in enumerate(shapes):
            block = Block(shape)
            
            # Try all rotations
            for rotation in range(4):
                rotated_block = block.rotate_clockwise(rotation)
                
                # Try all placements
                for r in range(board.rows):
                    for c in range(board.cols):
                        if board.can_place(rotated_block, r, c):
                            # Create a copy of the board
                            temp_board = Board(board.rows, board.cols)
                            temp_board.grid = [row[:] for row in board.grid]  # Deep copy
                            
                            # Place the block on the temporary board
                            temp_board.place_block(rotated_block, r, c)
                            
                            # Find cells to clear
                            cells_to_clear = temp_board.find_full_lines()
                            
                            # Count the number of unique lines (rows + columns)
                            # Based on game_engine._count_lines_from_cells logic
                            row_counts = {}
                            col_counts = {}
                            for r_cell, c_cell in cells_to_clear:
                                row_counts[r_cell] = row_counts.get(r_cell, 0) + 1
                                col_counts[c_cell] = col_counts.get(c_cell, 0) + 1
                                
                            cleared_rows = sum(1 for r_val, count in row_counts.items() 
                                             if count == temp_board.cols)
                            cleared_cols = sum(1 for c_val, count in col_counts.items() 
                                             if count == temp_board.rows)
                            
                            lines_cleared = cleared_rows + cleared_cols
                            
                            # Update best block if this one clears more lines
                            if lines_cleared > max_lines_cleared:
                                max_lines_cleared = lines_cleared
                                best_block_idx = shape_idx
        
        # Return the name of the best block or "None" if no block clears any lines
        if best_block_idx >= 0 and max_lines_cleared > 0:
            if best_block_idx < len(self.shape_names):
                return self.shape_names[best_block_idx]
            else:
                return f"Shape {best_block_idx}"  # Fallback if shape names array is shorter
        else:
            return "None"
    
    def _check_game_end_opportunity(self, board: Board, shapes: List[List[List[int]]], 
                                    preview_blocks: List[Tuple[Block, int]]) -> Tuple[bool, str]:
        """Check if there's an opportunity to end the game by finding a block that doesn't fit.
        Takes into account preview blocks as if they're already placed.
        
        Args:
            board: Current game board
            shapes: List of all possible block shapes
            preview_blocks: List of preview blocks with rotations
            
        Returns:
            Tuple of (opportunity exists, block that doesn't fit)
        """
        # First create a future board state with all preview blocks placed optimally
        future_board = self._create_future_board_with_preview(board, preview_blocks)
        
        # If future board creation fails, game is likely already over
        if future_board is None:
            return False, "None"
            
        # Try each block shape on the future board
        for shape_idx, shape in enumerate(shapes):
            block = Block(shape)
            can_place_anywhere = False
            
            # Try all rotations
            for rotation in range(4):
                rotated_block = block.rotate_clockwise(rotation)
                
                # Try all placements
                for r in range(future_board.rows):
                    for c in range(future_board.cols):
                        if future_board.can_place(rotated_block, r, c):
                            can_place_anywhere = True
                            break
                    if can_place_anywhere:
                        break
                if can_place_anywhere:
                    break
            
            # If this block can't be placed anywhere on the future board
            if not can_place_anywhere:
                return True, self.shape_names[shape_idx] if shape_idx < len(self.shape_names) else f"Shape {shape_idx}"
        
        # All blocks can be placed somewhere
        return False, "None"
    
    def _create_future_board_with_preview(self, board: Board, preview_blocks: List[Tuple[Block, int]]) -> Optional[Board]:
        """Create a future board state with all preview blocks placed optimally.
        
        Args:
            board: Current game board
            preview_blocks: List of preview blocks with rotations
            
        Returns:
            Future board state or None if preview blocks cannot be placed
        """
        # Create a copy of the board
        future_board = Board(board.rows, board.cols)
        future_board.grid = [row[:] for row in board.grid]  # Deep copy
        
        # Try to place each preview block in a location that would clear the most lines
        for block, rotation in preview_blocks:
            rotated_block = block.rotate_clockwise(rotation)
            best_placement = None
            max_lines_cleared = -1
            
            # Find the best placement for this block
            for r in range(future_board.rows):
                for c in range(future_board.cols):
                    if future_board.can_place(rotated_block, r, c):
                        # Try placing the block here
                        temp_board = Board(future_board.rows, future_board.cols)
                        temp_board.grid = [row[:] for row in future_board.grid]  # Deep copy
                        temp_board.place_block(rotated_block, r, c)
                        
                        # Find cells to clear
                        cells_to_clear = temp_board.find_full_lines()
                        
                        # Count lines that would be cleared (simplistic approach)
                        lines_cleared = len(cells_to_clear) // max(future_board.rows, future_board.cols)
                        
                        # Update best placement if this one is better
                        if lines_cleared > max_lines_cleared:
                            max_lines_cleared = lines_cleared
                            best_placement = (r, c)
            
            # If we couldn't place this block anywhere, return None
            if best_placement is None:
                return None
                
            # Place the block at the best location
            r, c = best_placement
            future_board.place_block(rotated_block, r, c)
            
            # Clear any full lines
            cells_to_clear = future_board.find_full_lines()
            if cells_to_clear:
                future_board.clear_cells(cells_to_clear)
                
        return future_board
    
    def _find_empty_clusters(self, board: Board) -> List[Set[Tuple[int, int]]]:
        """Find all connected empty regions on the board using BFS.
        
        Args:
            board: Current game board
            
        Returns:
            List of sets containing (row, col) coordinates for each empty cluster
        """
        visited = set()
        empty_clusters = []
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        
        # Perform BFS from each unvisited empty cell
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] == 0 and (r, c) not in visited:
                    # Start a new cluster
                    cluster = set()
                    queue = [(r, c)]
                    visited.add((r, c))
                    
                    # BFS to find all connected empty cells
                    while queue:
                        curr_r, curr_c = queue.pop(0)
                        cluster.add((curr_r, curr_c))
                        
                        # Check all four adjacent cells
                        for dr, dc in directions:
                            nr, nc = curr_r + dr, curr_c + dc
                            if (0 <= nr < board.rows and 0 <= nc < board.cols and 
                                board.grid[nr][nc] == 0 and (nr, nc) not in visited):
                                queue.append((nr, nc))
                                visited.add((nr, nc))
                    
                    empty_clusters.append(cluster)
        
        return empty_clusters
    
    def _check_imminent_threat(self, board: Board, preview_blocks: List[Tuple[Block, int]]) -> bool:
        """Check if any of the preview blocks can't be placed on the board.
        
        Args:
            board: Current game board
            preview_blocks: List of preview blocks with rotations
            
        Returns:
            True if any preview block can't be placed, False otherwise
        """
        if not preview_blocks:
            return False
            
        for block, rotation in preview_blocks:
            can_place = False
            rotated_block = block.rotate_clockwise(rotation)
            
            # Check if the block can be placed anywhere on the board
            for r in range(board.rows):
                for c in range(board.cols):
                    if board.can_place(rotated_block, r, c):
                        can_place = True
                        break
                if can_place:
                    break
            
            # If any block can't be placed, there's an imminent threat
            if not can_place:
                return True
        
        return False
    
    def _update_perf_band(self) -> None:
        """Update performance band based on clear rate."""
        if self.clear_rate < self.low_clear:
            self.perf_band = "Hard"
        elif self.clear_rate > self.high_clear:
            self.perf_band = "Easy"
        else:
            self.perf_band = "OK"
    
    def _update_player_level(self) -> None:
        """Update player level based on clear rate."""
        if self.clear_rate < 0.2:
            self.player_level = "Novice"
        elif self.clear_rate < 0.6:
            self.player_level = "Intermediate"
        else:
            self.player_level = "Expert"
    
    def _update_emotional_state(self) -> None:
        """Update emotional state based on timing and clear rate."""
        if self.time_per_move > 0.8 * self.max_time_per_move:
            self.emotional_state = "Frustrated"
        elif self.time_per_move < 0.2 * self.max_time_per_move and self.clear_rate > 0.7:
            self.emotional_state = "Bored"
        else:
            self.emotional_state = "Calm"
    
    def _update_phase(self) -> None:
        """Update game phase based on move count."""
        if self.move_count <= 9:
            self.phase = "early"
        elif self.move_count <= 29:
            self.phase = "mid"
        else:
            self.phase = "late"
    
    @property
    def mistake_sw(self) -> int:
        """Get the number of mistakes in the sliding window."""
        return sum(self._recent_mistakes)
    
    def get_all_metrics(self) -> Dict:
        """Get all metrics as a dictionary.
        
        Returns:
            Dictionary containing all current metrics
        """
        return {
            # Game analysis metrics
            "best_fit_block": self.best_fit_block,
            "opportunity": self.opportunity,
            "game_over_block": self.game_over_block,
            
            # Game state metrics
            "imminent_threat": self.imminent_threat,
            "occupancy_ratio": round(self.occupancy_ratio, 2),
            "fragmentation_count": self.fragmentation_count,
            "largest_empty_region": round(self.largest_empty_region, 2),
            "danger_score": round(self.danger_score, 2),
            "phase": self.phase,
            
            # Player state metrics
            "move_count": self.move_count,
            "lines_cleared": self.lines_cleared,
            "score": self.score,
            "clear_rate": round(self.clear_rate, 2),
            "recent_clears": list(self.recent_clears),
            "perf_band": self.perf_band,
            "player_level": self.player_level,
            "emotional_state": self.emotional_state,
            "time_per_move": round(self.time_per_move, 2),
            "avg_time_per_move": round(self.avg_time_per_move, 2),
            "placement_efficiency": round(self.placement_efficiency, 2),
            "mistake_flag": self.mistake_flag,
            "mistake_count": self.mistake_count,
            "mistake_rate": round(self.mistake_rate, 2),
            "mistake_sw": self.mistake_sw
        } 