# engine/game_engine.py
from typing import Dict, List, Tuple, Optional, Set

from engine.board import Board
from engine.block_pool import BlockPool
from engine.block import Block
from ui.animation import AnimationManager, FadeoutAnimation
from utils.metrics_manager import MetricsManager
from config.defaults import DEFAULT_WEIGHTS, SHAPES


class GameEngine:
    """Core game loop & scoring logic."""

    def __init__(self, config: Dict):
        self.config = config
        
        # Ensure required config values exist with proper default values
        if "shapes" not in self.config:
            self.config["shapes"] = SHAPES.copy()
            
        if "shape_weights" not in self.config:
            self.config["shape_weights"] = DEFAULT_WEIGHTS
        
        # Initialize board
        self.board = Board()
        self.score = 0
        self.lines = 0
        self.blocks_placed = 0
        self._game_over = False

        # Initialize metrics manager
        try:
            self.metrics_manager = MetricsManager(config)
        except Exception as e:
            print(f"[engine/game_engine.py] Error initializing MetricsManager: {e}")
            # Continue without full metrics tracking if something fails
            self.metrics_manager = MetricsManager({})

        # Initialize block pool with configuration
        try:
            self.pool = BlockPool(
                self.config["shapes"],
                self.config["shape_weights"],
                self.config
            )
        except Exception as e:
            print(f"[engine/game_engine.py] Error initializing BlockPool: {e}, using fallback defaults")
            # Fallback to default shapes and weights
            self.config["shapes"] = SHAPES.copy()
            self.config["shape_weights"] = DEFAULT_WEIGHTS
            self.pool = BlockPool(self.config["shapes"], self.config["shape_weights"])
            
        self._current_block = None
        
        # Preview management
        self._preview_blocks = []  # List of blocks (no rotation)
        self._selected_preview_index = None
        
        # Animation management
        self.animation_manager = AnimationManager()
        self.animation_duration_ms = 300  # Default animation duration in milliseconds

        # Now call refill_preview after metrics_manager is initialized
        try:
            self._refill_preview()
        except Exception as e:
            print(f"[engine/game_engine.py][68] Error filling preview: {e}")
            # If refill fails, initialize with empty preview
            self._preview_blocks = []
            self._selected_preview_index = None

    @staticmethod
    def compute_line_score(cells: int) -> int:
        """Calculate score based on number of cells cleared.
        
        Args:
            cells: Number of cells cleared
            
        Returns:
            int: Score awarded for clearing those cells
        """
        # Award 1 point per cleared cell
        return cells * 10

    # ───────────────────────── Public API ──────────────────────────

    def get_board_state(self) -> List[List[int]]:
        """Get the current board grid state (read-only)."""
        return [row[:] for row in self.board.grid]
    
    def get_preview_blocks(self) -> List[Block]:
        """Get the current preview blocks (read-only)."""
        return self._preview_blocks.copy()
    
    def get_selected_preview_index(self) -> Optional[int]:
        """Get the index of the currently selected preview block."""
        return self._selected_preview_index
    
    def get_metrics(self) -> Dict:
        """Get all current metrics.
        
        Returns:
            Dict: All current metrics data
        """
        return self.metrics_manager.get_all_metrics()
    
    def select_preview_block(self, index: int) -> bool:
        """Select a block from the preview by index.
        
        Args:
            index: Index of the block to select (0-based)
            
        Returns:
            bool: True if successfully selected, False otherwise
        """
        if 0 <= index < len(self._preview_blocks):
            self._selected_preview_index = index
            print(f"[engine/game_engine.py][286] Selected preview block at index: {index}")
            return True
        return False
    
    def get_valid_placements(self, block_index: Optional[int] = None) -> Set[Tuple[int, int]]:
        """Get all valid (row, col) positions where the specified block can be placed.
        
        Args:
            block_index: Index of the preview block (defaults to selected block)
            
        Returns:
            Set of (row, col) tuples where the block can be placed
        """
        if block_index is None:
            block_index = self._selected_preview_index
            
        if block_index is None or not (0 <= block_index < len(self._preview_blocks)):
            return set()
            
        block = self._preview_blocks[block_index]
        
        # Find all valid placements
        valid_positions = set()
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.can_place(block, r, c):
                    valid_positions.add((r, c))
                    
        return valid_positions
    
    def place_selected_block(self, row: int, col: int) -> bool:
        """Place the currently selected block at the specified position.
        
        Args:
            row: Row position (0-based, from top)
            col: Column position (0-based, from left)
            
        Returns:
            bool: True if successfully placed, False otherwise
        """
        if self._selected_preview_index is None:
            return False
        
        # Don't allow placement while animations are running
        if self.is_animating():
            return False
            
        # Get selected block
        block = self._preview_blocks[self._selected_preview_index]
        
        # Check if can place
        if not self.board.can_place(block, row, col):
            return False
            
        # Place the block
        self.board.place_block(block, row, col)
        print(f"[engine/game_engine.py][175] Placed block at {row}, {col}")
        self.blocks_placed += 1
        
        # Find cells to clear and create animation
        cells_to_clear = self.board.find_full_lines()
        line_count = self._count_lines_from_cells(cells_to_clear)
        
        # Handle line clearing with animation if lines were cleared
        if cells_to_clear:
            if self.animation_duration_ms > 0:
                # Create fadeout animation for cleared cells
                self.animation_manager.add_animation(
                    FadeoutAnimation(cells_to_clear, self.animation_duration_ms)
                )
                # Update lines count (count of lines cleared)
                self.lines += line_count
                self.metrics_manager.lines_cleared += line_count
                # Update score based on number of cells cleared
                self.score += self.compute_line_score(len(cells_to_clear))
            else:
                # Skip animation when duration is 0 (simulation mode)
                self.lines += line_count
                self.metrics_manager.lines_cleared += line_count
                self.score += self.compute_line_score(len(cells_to_clear))
                self.board.clear_cells(cells_to_clear)
        else:
            # No lines to clear, just add 1 point for block placement
            self.score += len(block.cells)
            
        # Update metrics for move completion
        self.metrics_manager.score = self.score
        self.metrics_manager.moves += 1
        self.metrics_manager.recent_clears.append(line_count)
        self.metrics_manager.clear_rate = (self.metrics_manager.lines_cleared / self.metrics_manager.moves) if self.metrics_manager.moves else 0.0
        
        # Remove from preview
        self._preview_blocks.pop(self._selected_preview_index)
        
        # Update selected index or reset if none left
        if not self._preview_blocks:
            self._refill_preview()
        else:
            self._selected_preview_index = min(self._selected_preview_index, len(self._preview_blocks) - 1)

        # Check for game over (if no animations in progress or no duration)
        if not cells_to_clear or self.animation_duration_ms == 0:
            self._check_game_over()        
        return True
    
    def update_animations(self) -> None:
        """Update all running animations and clear lines if animations complete."""
        # If any animations are complete, clear those cells from the board
        completed = self.animation_manager.update_animations()
        for animation in completed:
            if isinstance(animation, FadeoutAnimation):
                # Clear cells from the board once fadeout is complete
                self.board.clear_cells(animation.cells)
                
                # Check for game over after cells are cleared
                self._check_game_over()
        
        # Update game state metrics (every frame)
        self.metrics_manager.update_game_state_metrics(self.board, self._preview_blocks)
    
    def is_animating(self) -> bool:
        """Check if any animations are currently running."""
        return self.animation_manager.has_animations()
    
    def get_cell_opacity(self, row: int, col: int) -> Optional[float]:
        """Get the opacity (0-1) for a cell if it's being animated."""
        return self.animation_manager.get_cell_opacity(row, col)
    
    def find_next_placeable_block(self) -> Optional[int]:
        """Find the next preview block that can be placed somewhere on the board.
        
        Returns:
            Index of placeable block or None if no blocks can be placed
        """
        for i, block in enumerate(self._preview_blocks):
            for r in range(self.board.rows):
                for c in range(self.board.cols):
                    if self.board.can_place(block, r, c):
                        return i
        return None
    
    @property
    def game_over(self) -> bool:
        """True if game is over (no valid moves remain)."""
        return self._game_over
    
    # ──────────────────────── Private methods ────────────────────────

    def _refill_preview(self):
        """Fill the preview with blocks up to the target count."""
        # Update game state metrics (every frame)
        self.metrics_manager.update_block_metrics(self.board)
            
        try:
            # Get blocks directly from the enhanced BlockPool
            new_blocks = self.pool.get_next_blocks(self)
            
            # Add new blocks to preview
            self._preview_blocks.extend(new_blocks)
            
            # Select first block if none selected
            if self._selected_preview_index is None and self._preview_blocks:
                self._selected_preview_index = 0
                
            # Check if MetricsManager has update_preview_blocks method before calling
            if hasattr(self.metrics_manager, 'update_preview_blocks'):
                self.metrics_manager.update_preview_blocks(
                    self.board,
                    self._preview_blocks,
                    self._selected_preview_index
                )
            print(f"[engine/game_engine.py][286] Refilled preview with {len(self._preview_blocks)} blocks")
        except Exception as e:
            print(f"[engine/game_engine.py][288] Error in _refill_preview: {e}")
            # No fallback - if we have errors, we need to know and fix the root cause
    
    def _has_valid_placement(self, block: Block) -> bool:
        """Check if a block can be placed anywhere on the board.
        
        Returns:
            True if the block can be placed, False otherwise
        """
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.can_place(block, r, c):
                    return True
        return False
    
    def _check_game_over(self) -> bool:
        """Check if the game is over (no valid moves remain)."""
        # Game is already over
        if self._game_over:
            return True
            
        # Check if any preview block can be placed
        for block in self._preview_blocks:
            if self._has_valid_placement(block):
                return False
                
        # No valid placements for any blocks, game over
        self._game_over = True
        print(f"[engine/game_engine.py][316] Game over: score: {self.score}, lines: {self.lines}, blocks placed: {self.blocks_placed}")
        return True
    
    def _count_lines_from_cells(self, cells: Set[Tuple[int, int]]) -> int:
        """Count unique lines from a set of cells.
        
        Args:
            cells: Set of (row, col) tuples
            
        Returns:
            int: Number of unique lines (rows + columns)
        """
        # Count number of cells per row and per column
        row_counts: Dict[int, int] = {}
        col_counts: Dict[int, int] = {}
        for r, c in cells:
            row_counts[r] = row_counts.get(r, 0) + 1
            col_counts[c] = col_counts.get(c, 0) + 1

        # Rows cleared: those rows where the number of cells equals the board columns
        cleared_rows = sum(1 for r, count in row_counts.items() if count == self.board.cols)
        # Columns cleared: those columns where the number of cells equals the board rows
        cleared_cols = sum(1 for c, count in col_counts.items() if count == self.board.rows)

        return cleared_rows + cleared_cols
