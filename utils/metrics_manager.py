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
    
    def _find_best_fit_block(self, board: Board, shapes: Dict[str, List[Tuple[int, int]]]) -> str:
        """Find block that clears the most lines when placed on the board.
        
        Args:
            board: Current game board
            shapes: Dictionary of all possible block shapes
            
        Returns:
            String name of the best fit block or "None" if no block clears a line
        """
        best_block_name = "None"
        max_lines_cleared = 0
        
        # Try each block shape
        for shape_name, shape in shapes.items():
            block = Block(shape)
            
            # Try placing the block at each position
            for r in range(board.rows):
                for c in range(board.cols):
                    # Check if block can be placed at this position
                    if board.can_place(block, r, c):
                        # Create a temporary board for simulation
                        temp_board = Board.from_grid(board.grid)
                        
                        # Place the block
                        temp_board.place_block(block, r, c)
                        
                        # Count cleared cells
                        cleared_cells = temp_board.find_full_lines()
                        if cleared_cells:
                            lines_cleared = self._count_lines(cleared_cells)
                            
                            # Update best block if this one is better
                            if lines_cleared > max_lines_cleared:
                                max_lines_cleared = lines_cleared
                                best_block_name = shape_name
        
        return best_block_name
    
    def _check_game_end_opportunity(self, board: Board, shapes: Dict[str, List[Tuple[int, int]]], 
                                    preview_blocks: List[Block]) -> Tuple[bool, str]:
        """Check if game will end after placing the preview blocks.
        
        Args:
            board: Current game board
            shapes: Dictionary of all possible block shapes  
            preview_blocks: List of preview blocks
            
        Returns:
            Tuple of (opportunity_exists, game_over_block_name)
        """
        # Create a future board by simulating placement of all preview blocks
        future_board = self._create_future_board_with_preview(board, preview_blocks)
        
        # If simulation couldn't place all blocks, no future to check
        if not future_board:
            return False, "None"
        
        # Check if any shape can be placed on the future board
        for shape_name, shape in shapes.items():
            block = Block(shape)
            if not self._can_place_anywhere(future_board, block):
                # This shape would cause game over
                return True, shape_name
        
        # No game ending opportunity found
        return False, "None"
    
    def _create_future_board_with_preview(self, board: Board, preview_blocks: List[Block]) -> Optional[Board]:
        """Simulate placing all preview blocks on the board optimally.
        
        Args:
            board: Current game board
            preview_blocks: List of preview blocks
            
        Returns:
            A simulated future board or None if simulation fails
        """
        future_board = Board.from_grid(board.grid)
        
        # Try to place each preview block
        for block in preview_blocks:
            # Find best placement (clears most lines)
            best_placement = None
            best_lines_cleared = -1
            
            # Try each position
            for r in range(future_board.rows):
                for c in range(future_board.cols):
                    # Check if block can be placed
                    if future_board.can_place(block, r, c):
                        # Create a temporary board for simulation
                        temp_board = Board.from_grid(future_board.grid)
                        
                        # Place the block
                        temp_board.place_block(block, r, c)
                        
                        # Count cleared cells
                        cleared_cells = temp_board.find_full_lines()
                        if cleared_cells:
                            lines_cleared = self._count_lines(cleared_cells)
                            
                            # Update best placement if this one is better
                            if lines_cleared > best_lines_cleared:
                                best_lines_cleared = lines_cleared
                                best_placement = (r, c)
                        elif best_placement is None:
                            # Keep track of valid placement even if no lines cleared
                            best_placement = (r, c)
            
            # If no valid placement found for this block, simulation fails
            if best_placement is None:
                return None
                
            # Place the block at the best position
            r, c = best_placement
            future_board.place_block(block, r, c)
            
            # Clear any completed lines
            cleared_cells = future_board.find_full_lines()
            if cleared_cells:
                future_board.clear_cells(cleared_cells)
        
        # Successfully placed all blocks
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
    
    def _check_imminent_threat(self, board: Board, preview_blocks: List[Block]) -> bool:
        """Check if the next placeable block can be placed without causing game end.
        
        Args:
            board: Current game board
            preview_blocks: List of preview blocks
            
        Returns:
            True if there is an imminent threat, False otherwise
        """
        if not preview_blocks:
            return False
            
        # Check if current blocks can even be placed
        placeable = False
        for block in preview_blocks:
            if self._can_place_anywhere(board, block):
                placeable = True
                break
                
        if not placeable:
            # Already in game over condition
            return True
            
        # Create a future board by simulating placement of all preview blocks
        future_board = self._create_future_board_with_preview(board, preview_blocks)
        
        # If simulation couldn't place all blocks, there's a threat
        if not future_board:
            return True
            
        # Check if any shape can be placed on the future board
        for shape in self.config["shapes"].values():
            block = Block(shape)
            if self._can_place_anywhere(future_board, block):
                # Found at least one shape that can be placed, no imminent threat
                return False
        
        # No shape can be placed after preview blocks, imminent threat
        return True
    
    def _can_place_anywhere(self, board: Board, block: Block) -> bool:
        """Check if a block can be placed anywhere on the board.
        
        Args:
            board: Game board to check
            block: Block to place
            
        Returns:
            True if the block can be placed somewhere, False otherwise
        """
        for r in range(board.rows):
            for c in range(board.cols):
                if board.can_place(block, r, c):
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
    
    def _count_lines(self, cells: Set[Tuple[int, int]]) -> int:
        """Count the number of distinct rows and columns in a set of cells.
        
        Args:
            cells: Set of (row, col) tuples that would be cleared
            
        Returns:
            Number of distinct rows and columns
        """
        rows = set()
        cols = set()
        
        for r, c in cells:
            rows.add(r)
            cols.add(c)
            
        return len(rows) + len(cols)
    
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