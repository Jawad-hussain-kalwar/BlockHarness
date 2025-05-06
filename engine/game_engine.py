# engine/game_engine.py
from typing import Dict, List, Tuple, Optional, Set

from engine.board import Board
from engine.block_pool import BlockPool
from engine.block import Block
from ui.animation import AnimationManager, FadeoutAnimation
from utils.metrics_manager import MetricsManager
from dda.registry import registry as dda_registry
from config.defaults import DEFAULT_WEIGHTS, SHAPES


class GameEngine:
    """Core game loop & scoring logic."""

    def __init__(self, config: Dict):
        self.config = config
        
        # Ensure required config values exist with proper default values
        if "shapes" not in self.config:
            self.config["shapes"] = SHAPES.copy()
            
        if "shape_weights" not in self.config:
            self.config["shape_weights"] = DEFAULT_WEIGHTS.copy()
        
        # Initialize board
        self.board = Board()
        self.score = 0
        self.lines = 0
        self.blocks_placed = 0
        self._game_over = False

        # Initialize block pool with safe configuration
        try:
            self.pool = BlockPool(
                self.config["shapes"],
                self.config["shape_weights"]
            )
        except Exception as e:
            print(f"[engine/game_engine.py][40] Error initializing BlockPool: {e}, using fallback defaults")
            # Fallback to default shapes and weights
            self.config["shapes"] = SHAPES.copy()
            self.config["shape_weights"] = DEFAULT_WEIGHTS.copy()
            self.pool = BlockPool(self.config["shapes"], self.config["shape_weights"])
            
        self._current_block = None
        
        # Preview management
        self._preview_blocks = []  # List of blocks (no rotation)
        self._selected_preview_index = None
        
        # Create and initialize DDA algorithm
        try:
            dda_name = self.config.get("dda_algorithm", "OpportunityDDA")
            self.dda_algorithm = dda_registry.create_algorithm(dda_name)
            dda_params = self.config.get("dda_params", {})
            self.dda_algorithm.initialize(dda_params)
        except Exception as e:
            print(f"[engine/game_engine.py][59] Error initializing DDA algorithm: '{dda_name}', using fallback MetricsDDA")
            # Fallback to MetricsDDA
            try:
                self.dda_algorithm = dda_registry.create_algorithm("MetricsDDA")
                self.dda_algorithm.initialize({})
            except Exception as fallback_error:
                print(f"[engine/game_engine.py][65] Error initializing fallback DDA algorithm: {fallback_error}, using OpportunityDDA")
                # Try OpportunityDDA as last resort
                self.dda_algorithm = dda_registry.create_algorithm("OpportunityDDA")
                self.dda_algorithm.initialize({})
        
        # Initialize metrics manager
        try:
            self.metrics_manager = MetricsManager(config)
            # Start timing for the first move
            self.metrics_manager.start_move_timer()
        except Exception as e:
            print(f"[engine/game_engine.py][76] Error initializing MetricsManager: {e}")
            # Continue without full metrics tracking if something fails
            self.metrics_manager = MetricsManager({})
            self.metrics_manager.start_move_timer()
        
        # Now call refill_preview after metrics_manager is initialized
        try:
            self._refill_preview()
        except Exception as e:
            print(f"[engine/game_engine.py][85] Error filling preview: {e}")
            # If refill fails, initialize with empty preview
            self._preview_blocks = []
            self._selected_preview_index = None
        
        # Animation management
        self.animation_manager = AnimationManager()
        self.animation_duration_ms = 300  # Default animation duration in milliseconds

    @staticmethod
    def compute_line_score(cells: int) -> int:
        """Calculate score based on number of cells cleared.
        
        Args:
            cells: Number of cells cleared
            
        Returns:
            int: Score awarded for clearing those cells
        """
        # Award 1 point per cleared cell
        return cells

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
            # Record a placement mistake
            self.metrics_manager.record_mistake()
            return False
            
        # Place the block
        self.board.place_block(block, row, col)
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
                # Update score based on number of cells cleared
                self.score += self.compute_line_score(len(cells_to_clear))
            else:
                # Skip animation when duration is 0 (simulation mode)
                self.lines += line_count
                self.score += self.compute_line_score(len(cells_to_clear))
                # Immediately clear the cells
                # print("[engine/game_engine.py][219] Immediately clearing cells - simulation mode")
                self.board.clear_cells(cells_to_clear)
        else:
            # No lines to clear, just add 1 point for block placement
            self.score += 1
            
        # Update metrics for move completion
        self.metrics_manager.record_move_completion(line_count)
        self.metrics_manager.score = self.score
        
        # Update difficulty if needed
        self._maybe_update_difficulty()
        
        # Remove from preview
        self._preview_blocks.pop(self._selected_preview_index)
        
        # Update selected index or reset if none left
        if not self._preview_blocks:
            self._selected_preview_index = None
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

    def _spawn(self) -> Block:
        """Create a new block using the DDA algorithm."""
        # Get a single block from the DDA
        blocks = self.dda_algorithm.get_next_blocks(self, 1)
        return blocks[0]
    
    def _refill_preview(self, target_count=3):
        """Fill the preview with blocks up to the target count."""
        # Determine how many blocks to generate
        num_to_generate = max(0, target_count - len(self._preview_blocks))
        
        if num_to_generate <= 0:
            return  # Preview already has enough blocks
            
        try:
            # Try to get blocks from DDA algorithm first
            new_blocks = self.dda_algorithm.get_next_blocks(self, num_to_generate)
            
            # If the DDA algorithm didn't return enough blocks, fill with randomly selected ones
            if len(new_blocks) < num_to_generate:
                num_still_needed = num_to_generate - len(new_blocks)
                for _ in range(num_still_needed):
                    new_blocks.append(self.pool.get_block())
                    
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
            
        except Exception as e:
            print(f"[engine/game_engine.py][331] Error in _refill_preview: {e}")
            # Fallback to generating simple blocks if DDA or metrics fail
            try:
                for _ in range(num_to_generate):
                    self._preview_blocks.append(self.pool.get_block())
                
                # Select first block if none selected
                if self._selected_preview_index is None and self._preview_blocks:
                    self._selected_preview_index = 0
            except Exception as e2:
                print(f"[engine/game_engine.py][225] Critical error in block generation: {e2}")
                # Leave preview as is if all attempts fail
    
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
    
    def _maybe_update_difficulty(self):
        """Update difficulty - maintained for backward compatibility.
        
        Note: This method is primarily kept for backward compatibility.
        Modern DDA algorithms will handle difficulty adjustment directly.
        """
        # For backward compatibility with threshold-based DDAs
        for thr, new_weights in self.config.get("difficulty_thresholds", []):
            if self.score >= thr:
                self.pool.weights = new_weights
