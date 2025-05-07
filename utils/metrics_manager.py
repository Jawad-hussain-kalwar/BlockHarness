# utils/metrics_manager.py
from typing import Dict, List, Set, Tuple, Optional
from collections import deque
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

        # Initialize game analysis metrics
        self.best_fit_block = "None"
        self.best_fit_position = (0, 0)
        self.clearable_lines = 0
        self.opportunity = False
        self.game_over_blocks = []
        self.num_game_over_blocks = 0


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


    def update_game_state_metrics(
        self, board: Board, preview_blocks: List[Block]
    ) -> None:
        """Update game state metrics based on current board and preview.

        Args:
            board: Current game board
            preview_blocks: List of preview blocks
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
            self.occupancy_weight * self.occupancy_ratio
            + self.fragmentation_weight * inv_frag
            + self.inv_largest_weight * inv_largest
        )

        # Check for imminent threat
        self.imminent_threat = self._check_imminent_threat(board, preview_blocks)
    
    def update_block_metrics(
        self, board: Board
    ) -> None:

        # Calculate best fit block and position
        shapes = self.config["shapes"]
        self.best_fit_block, self.best_fit_position, self.clearable_lines = self._compute_best_fit(
            shapes, board
        )

        # Check for game over blocks and opportunity
        self.opportunity, self.game_over_blocks = self._find_game_over_blocks(
            shapes, board
        )
        self.num_game_over_blocks = len(self.game_over_blocks)

    def _compute_best_fit(
        self, shapes: Dict[str, List[Tuple[int, int]]], board: Board
    ) -> Tuple[str, Tuple[int, int], int]:
        """Identify block shape and position that clears the most lines.

        Args:
            shapes: Dictionary of all possible block shapes
            board: Current game board

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

        board_center = board.cols // 2

        # Process shapes in a consistent order
        for shape_name in sorted(shapes.keys()):
            cells = shapes[shape_name]
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
                        lines = self._count_lines(cleared)

                        # Update if better
                        if lines > max_lines_cleared:
                            max_lines_cleared = lines
                            best_block_name = shape_name
                            best_position = (r, c)
                        elif lines == max_lines_cleared > 0:
                            # For equal line clears, prioritize specific blocks
                            if (
                                shape_name == "1x2-line"
                                and best_block_name != "1x2-line"
                            ):
                                best_block_name = shape_name
                                best_position = (r, c)
                            # Tie-breaking: prefer higher placements (lower r)
                            elif r < best_position[0]:
                                best_block_name = shape_name
                                best_position = (r, c)
                            # If same height, prefer more centered columns
                            elif r == best_position[0]:
                                if abs(c - board_center) < abs(
                                    best_position[1] - board_center
                                ):
                                    best_block_name = shape_name
                                    best_position = (r, c)

        # If no blocks can clear lines, use fallback
        if max_lines_cleared == 0:
            best_block_name = fallback_block
            best_position = fallback_position

        return (best_block_name, best_position, max_lines_cleared)

    def _can_place_anywhere(self, board: Board, block: Block) -> bool:
        """Check if block can be placed anywhere on the board.

        Args:
            board: Current game board
            block: Block to check

        Returns:
            True if block can be placed somewhere on the board
        """
        for r in range(board.rows):
            for c in range(board.cols):
                if board.can_place(block, r, c):
                    return True
        return False

    def _find_valid_placements(
        self, board: Board, block: Block
    ) -> List[Tuple[int, int, int]]:
        """Find all valid placements for a block with their line clear counts.

        Args:
            board: Current game board
            block: Block to place

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
                    lines = self._count_lines(cleared)

                    placements.append((r, c, lines))

        return placements

    def _place_and_clear(
        self, board: Board, block: Block, position: Tuple[int, int]
    ) -> int:
        """Place block at position and clear resulting lines. Returns lines cleared.

        Args:
            board: Board to place block on
            block: Block to place
            position: (row, col) position to place block

        Returns:
            Number of lines cleared
        """
        r, c = position
        board.place_block(block, r, c)
        cleared = board.find_full_lines()
        if cleared:
            board.clear_cells(cleared)
            return self._count_lines(cleared)
        return 0

    def _find_game_over_blocks(
        self,
        shapes: Dict[str, List[Tuple[int, int]]],
        board: Board
    ) -> Tuple[bool, List[str]]:
        """Find blocks that cannot be placed now and won't fit after placing preview blocks.

        Args:
            shapes: Dictionary of all possible block shapes
            board: Current game board

        Returns:
            Tuple of (opportunity_exists, list_of_block_names)
        """

        # Process shape names in consistent order for testing
        game_over_blocks = []

        # Check from all possible shapes if any of them can not be placed on the board
        for shape_name in sorted(shapes.keys()):
            block = Block(shapes[shape_name])
            if not self._can_place_anywhere(board, block):
                game_over_blocks.append(shape_name)

        # Return all game over blocks found
        return (
            bool(game_over_blocks),
            game_over_blocks if game_over_blocks else ["None"],
        )

    def _find_empty_clusters(self, board: Board) -> List[Set[Tuple[int, int]]]:
        """Find clusters of connected empty cells using BFS.

        Args:
            board: Current game board

        Returns:
            List of sets containing (row, col) coordinates for each cluster
        """
        # Initialize variables
        clusters = []
        visited = set()

        # Offsets for 4-directional neighbors
        offsets = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        # Iterate through all cells
        for r in range(board.rows):
            for c in range(board.cols):
                # Skip if cell is filled or already visited
                if board.grid[r][c] or (r, c) in visited:
                    continue

                # Start a new cluster
                cluster = set()
                queue = deque([(r, c)])

                # BFS to find all connected empty cells
                while queue:
                    curr_r, curr_c = queue.popleft()
                    if (curr_r, curr_c) in visited:
                        continue

                    # Add to cluster and mark as visited
                    cluster.add((curr_r, curr_c))
                    visited.add((curr_r, curr_c))

                    # Check neighbors
                    for dr, dc in offsets:
                        next_r, next_c = curr_r + dr, curr_c + dc
                        if (
                            0 <= next_r < board.rows
                            and 0 <= next_c < board.cols
                            and not board.grid[next_r][next_c]
                            and (next_r, next_c) not in visited
                        ):
                            queue.append((next_r, next_c))

                # Add cluster to list
                clusters.append(cluster)

        return clusters

    def _check_imminent_threat(self, board: Board, preview_blocks: List[Block]) -> bool:
        """Check if there is an imminent threat of game over.

        Args:
            board: Current game board
            preview_blocks: List of preview blocks

        Returns:
            True if there is an imminent threat of game over
        """
        # If we have game over opportunity, it's definitely a threat
        if self.opportunity:
            return True

        # If board is dangerously full, consider it a threat
        if self.danger_score > self.danger_cut:
            return True

        # Check if any preview blocks can't be placed
        for block in preview_blocks:
            if not self._can_place_anywhere(board, block):
                return True

        return False

    def _update_perf_band(self) -> None:
        """Update performance band based on clear rate."""
        if self.clear_rate < self.low_clear:
            self.perf_band = "Low"
        elif self.clear_rate > self.high_clear:
            self.perf_band = "High"
        else:
            self.perf_band = "Mid"

    def _update_player_level(self) -> None:
        """Update player level based on lines cleared and move count."""
        if self.lines_cleared > 100 or self.move_count > 200:
            self.player_level = "Expert"
        elif self.lines_cleared > 50 or self.move_count > 100:
            self.player_level = "Intermediate"
        else:
            self.player_level = "Novice"

    def _update_emotional_state(self) -> None:
        """Update emotional state based on recent performance."""
        if sum(self.recent_clears) > 5:
            self.emotional_state = "Focused"
        elif self.mistake_count > 5:
            self.emotional_state = "Frustrated"
        else:
            self.emotional_state = "Calm"

    def _update_phase(self) -> None:
        """Update game phase based on occupancy and move count."""
        if self.occupancy_ratio > 0.6 or self.move_count > 50:
            self.phase = "late"
        elif self.occupancy_ratio > 0.3 or self.move_count > 20:
            self.phase = "mid"
        else:
            self.phase = "early"

    def _count_lines(self, cells: Set[Tuple[int, int]]) -> int:
        """Count number of distinct rows and columns in the cleared set.

        Args:
            cells: Set of (row, col) coordinates to count

        Returns:
            Number of distinct rows and columns in the set
        """
        rows = set()
        cols = set()

        for r, c in cells:
            rows.add(r)
            cols.add(c)

        return len(rows) + len(cols)

    def get_all_metrics(self) -> Dict:
        """Get all metrics as a dictionary for display."""
        return {
            # Game Analysis Metrics
            "best_fit_block": self.best_fit_block,
            "best_fit_position": self.best_fit_position,
            "clearable_lines": self.clearable_lines,
            "opportunity": self.opportunity,
            "game_over_blocks": self.game_over_blocks,
            "num_game_over_blocks": len(self.game_over_blocks),
            # Game State Metrics
            "imminent_threat": self.imminent_threat,
            "occupancy_ratio": self.occupancy_ratio,
            "fragmentation_count": self.fragmentation_count,
            "largest_empty_region": self.largest_empty_region,
            "danger_score": self.danger_score,
            "phase": self.phase,
            # Player State Metrics
            "move_count": self.move_count,
            "lines_cleared": self.lines_cleared,
            "score": self.score,
            "clear_rate": self.clear_rate,
            "recent_clears": list(self.recent_clears),
            "perf_band": self.perf_band,
            "player_level": self.player_level,
            "emotional_state": self.emotional_state,
        }
