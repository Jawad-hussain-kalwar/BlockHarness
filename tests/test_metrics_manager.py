# tests/test_metrics_manager.py
import unittest
from engine.board import Board
from utils.metrics_manager import MetricsManager
from engine.shapes import SHAPES

class TestMetricsManager(unittest.TestCase):
    """Test suite for the MetricsManager class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Mock configuration for testing
        self.config = {
            "shapes": SHAPES,
            "metrics_weights": {
                "occupancy": 0.5,
                "fragmentation": 0.3,
                "inv_largest": 0.2
            },
            "metrics_flow": {
                "low_clear": 0.3,
                "high_clear": 0.7,
                "danger_cut": 0.8
            },
            "metrics_timing": {
                "max_time_per_move": 8.0
            },
            "viewable_metrics": {
                "best_fit_block": True,
                "best_fit_position": True,
                "opportunity": True,
                "game_over_block": True
            }
        }
        
        # Create metrics manager
        self.metrics_manager = MetricsManager(self.config)
    
    def test_best_fit_empty_board(self):
        """Test best fit block calculation on an empty board."""
        # Create empty board
        board = Board(8, 8)
        
        # Update metrics
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        
        # On an empty board, any block can be placed, but no lines can be cleared
        # The best fit should be the first block checked (fallback to 1x1-square)
        # The best position should be top-left (0, 0) as that's the first valid position
        self.assertIn(self.metrics_manager.best_fit_block, list(self.config["shapes"].keys()))
        self.assertEqual(self.metrics_manager.best_fit_position, (0, 0))
    
    def test_best_fit_with_line_clear_1(self):
        """Test best fit block that can clear lines."""
        # Create a board with a nearly full row missing one cell
        board = Board(8, 8)
        
        # Fill all cells in the first row except the last one
        board.grid=[[0,1,0,1,0,1,0,1],
                    [1,0,1,0,1,1,1,0],
                    [1,1,1,1,1,0,1,1],
                    [1,0,1,0,1,1,0,0],
                    [0,1,0,1,0,0,1,0],
                    [1,0,1,0,1,1,0,1],
                    [0,1,1,0,1,0,1,0],
                    [1,0,1,1,0,1,1,0]]
        
        # Update metrics
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)

        # The best fit should be a 1x1-square at position (2, 5)
        # because it will clear the first row
        self.assertEqual(self.metrics_manager.best_fit_block, "1x1-square")
        self.assertEqual(self.metrics_manager.best_fit_position, (2, 5))

    
    def test_best_fit_with_line_clear_2(self):
        # 3x2-T-CC at (2, 6) will clear 3 rows
        board = Board(8, 8)
        board.grid=[[0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [1,1,1,1,1,1,1,0],
                    [1,1,1,1,1,1,0,0],
                    [1,1,1,1,1,1,1,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "3x2-T-CC")
        self.assertEqual(self.metrics_manager.best_fit_position, (2, 6))
    
    def test_best_fit_with_line_clear_3(self):
        # 3x2-T-U at (2, 5) will clear 3 columns
        board = Board(8, 8)
        board.grid=[[1,0,1,1,1,0,0,0],
                    [1,0,1,1,1,0,0,0],
                    [1,0,1,1,1,0,0,0],
                    [1,0,1,1,1,0,0,0],
                    [1,0,1,1,1,0,0,0],
                    [1,0,1,0,1,0,0,0],
                    [1,0,0,0,0,0,0,0],
                    [0,0,1,1,1,0,0,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "2x3-T-U")
        self.assertEqual(self.metrics_manager.best_fit_position, (5, 2))

    def test_best_fit_with_line_clear_4(self):
        # 2x3-Z at (3, 1) will clear 2 rows
        board = Board(8, 8)
        board.grid=[[0,0,0,0,0,0,1,0],
                    [0,0,0,1,0,1,0,0],
                    [0,0,0,0,0,1,1,0],
                    [1,0,0,1,1,1,1,1],
                    [1,1,0,0,1,1,1,1],
                    [0,1,0,0,1,1,0,0],
                    [0,0,1,0,0,1,0,0],
                    [0,0,0,0,0,1,0,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "2x3-Z")
        self.assertEqual(self.metrics_manager.best_fit_position, (3, 1))

    def test_best_fit_with_line_clear_5(self):
        # 3x3-L-tl at (0,2) will clear 3 columns
        board = Board(8, 8)
        board.grid=[[0,0,0,0,0,0,0,1],
                    [0,0,0,1,1,0,0,1],
                    [0,0,0,1,1,0,0,1],
                    [0,0,1,1,1,0,0,1],
                    [0,0,1,1,1,0,0,1],
                    [0,0,1,1,1,0,0,1],
                    [0,0,1,1,1,0,0,0],
                    [0,0,1,1,1,0,0,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "3x3-L-tl")
        self.assertEqual(self.metrics_manager.best_fit_position, (0, 2))

    def test_best_fit_with_line_clear_6(self):
        # 3x2-L-tr at (5, 4) will clear 2 columns
        board = Board(8, 8)
        board.grid=[[0,0,0,0,0,1,1,0],
                    [0,0,1,0,0,1,1,0],
                    [0,0,0,0,0,1,1,0],
                    [0,0,0,0,0,1,1,0],
                    [1,0,0,1,1,0,0,0],
                    [0,0,0,0,0,1,0,0],
                    [0,1,0,0,0,1,0,1],
                    [1,1,1,1,1,1,1,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "3x2-L-tr")
        self.assertEqual(self.metrics_manager.best_fit_position, (4, 5))

    def test_best_fit_with_line_clear_7(self):
        # 3x2-L-bl at (3,5) will clear 2 columns
        board = Board(8, 8)
        board.grid=[[0,0,0,0,0,1,1,0],
                    [1,0,0,0,0,1,1,0],
                    [1,0,0,0,0,1,1,0],
                    [1,0,0,0,0,0,1,0],
                    [1,0,0,0,0,0,1,0],
                    [1,0,0,0,0,0,0,0],
                    [1,0,0,0,0,1,1,0],
                    [1,0,1,1,1,1,1,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "3x2-L-bl")
        self.assertEqual(self.metrics_manager.best_fit_position, (3, 5))

    def test_best_fit_with_line_clear_8(self):
        # 2x2-L-br at (4, 4) will clear 2 columns
        board = Board(8, 8)
        board.grid=[[0,0,0,0,1,1,0,0],
                    [0,1,0,0,1,1,0,0],
                    [0,0,0,0,1,1,0,0],
                    [0,0,1,0,1,1,0,0],
                    [0,0,0,0,1,0,0,0],
                    [0,1,0,0,0,0,0,0],
                    [0,0,1,0,1,1,0,0],
                    [0,0,1,0,1,1,0,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "2x2-L-br")
        self.assertEqual(self.metrics_manager.best_fit_position, (4, 4))

    def test_best_fit_with_line_clear_9(self):
        # 3x3-square at (1, 1) will clear 3 columns
        board = Board(8, 8)
        board.grid=[[0,1,1,1,1,0,1,0],
                    [0,0,0,0,0,0,1,0],
                    [0,0,0,0,0,0,1,0],
                    [0,0,0,0,0,0,1,0],
                    [0,1,1,1,0,1,1,0],
                    [0,1,1,1,0,0,0,0],
                    [0,1,1,1,0,1,1,0],
                    [0,1,1,1,0,1,1,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "3x3-square")
        self.assertEqual(self.metrics_manager.best_fit_position, (1, 1))

    def test_best_fit_with_line_clear_10(self):
        # 2x3-rect at (2, 2) will clear 3 columns
        board = Board(8, 8)
        board.grid=[[0,0,1,1,1,0,1,1],
                    [0,0,1,1,1,0,1,0],
                    [0,0,0,0,0,0,1,0],
                    [0,0,0,0,0,0,1,0],
                    [0,0,1,1,1,0,1,0],
                    [0,0,1,1,1,0,1,0],
                    [0,0,1,1,1,0,1,0],
                    [0,0,1,1,1,0,0,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "2x3-rect")
        self.assertEqual(self.metrics_manager.best_fit_position, (2, 2))

    def test_best_fit_with_line_clear_11(self):
        # 1x5-line at (2, 2) will clear 6 rows
        board = Board(8, 8)
        board.grid=[[0,0,1,1,1,1,1,0],
                    [0,0,1,1,1,1,1,0],
                    [1,1,0,0,0,0,0,1],
                    [0,0,1,1,1,1,1,0],
                    [0,0,1,1,1,1,1,0],
                    [0,0,1,1,1,1,1,0],
                    [0,0,1,1,1,1,1,0],
                    [0,0,1,1,1,1,1,0]]
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        self.assertEqual(self.metrics_manager.best_fit_block, "1x5-line")
        self.assertEqual(self.metrics_manager.best_fit_position, (2, 2))

    def test_game_over_block_detection_1(self):
        """Test game over block detection with nearly full board."""
        # Create a board with only one empty cell
        board = Board(8, 8)
        
        # Fill all cells except (0, 0)
        for r in range(8):
            for c in range(8):
                if not (r == 0 and c == 0):
                    board.grid[r][c] = 1
        
        # Only the 1x1-square can fit at (0, 0)
        # Update metrics with no preview blocks
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        
        # There should be an opportunity for game over
        # All blocks other than 1x1-square can't be placed
        self.assertTrue(self.metrics_manager.opportunity)
        
        # Check which block is identified as the game over block
        # It should be one of the larger blocks (2x2-square)
        # self.assertEqual(self.metrics_manager.game_over_block, "2x2-square")
        
        # Verify game_over_blocks contains multiple blocks
        self.assertGreater(len(self.metrics_manager.game_over_blocks), 1)
        self.assertIn("2x2-square", self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_2(self):
        """Test game over block detection with L-shaped empty area."""
        board = Board(8, 8)
        
        # Fill all cells except an L-shaped area at top-left
        for r in range(8):
            for c in range(8):
                if not ((r == 0 and c < 2) or (r == 1 and c == 0)):
                    board.grid[r][c] = 1
        
        # Only L-shaped blocks and smaller can fit
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)

        self.assertTrue(self.metrics_manager.opportunity)
        
        # Blocks like 2x2-square and 3x3-square shouldn't fit
        self.assertIn("2x2-square", self.metrics_manager.game_over_blocks)
        self.assertIn("3x3-square", self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_3(self):
        """Test game over block detection with checkerboard pattern (no blocks can fit)."""
        board = Board(8, 8)
        
        # Create checkerboard pattern
        for r in range(8):
            for c in range(8):
                board.grid[r][c] = (r + c) % 2
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        # All blocks should be game over blocks (except 1x1)
        self.assertTrue(self.metrics_manager.opportunity)
        
        # Check that most shapes are in game_over_blocks
        for shape_name in self.config["shapes"].keys():
            if shape_name not in ["1x1-square", "2x2-diag", "2x2-diag-b", "3x3-diag", "3x3-diag-b"]:
                self.assertIn(shape_name, self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_4(self):
        """Test game over block detection with thin vertical gap (excludes wide blocks)."""
        board = Board(8, 8)
        
        # Fill all cells except a vertical line in the middle
        for r in range(8):
            for c in range(8):
                if c != 3:  # Leave column 3 empty
                    board.grid[r][c] = 1
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)

        self.assertTrue(self.metrics_manager.opportunity)
        
        # Wide blocks should be in game_over_blocks
        self.assertIn("2x2-square", self.metrics_manager.game_over_blocks)
        self.assertIn("3x3-square", self.metrics_manager.game_over_blocks)
        
        # Vertical line blocks should not be in game_over_blocks
        self.assertNotIn("3x1-line", self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_5(self):
        """Test game over block detection with thin horizontal gap (excludes tall blocks)."""
        board = Board(8, 8)
        
        # Fill all cells except a horizontal line in the middle
        for r in range(8):
            for c in range(8):
                if r != 4:  # Leave row 4 empty
                    board.grid[r][c] = 1
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        
        self.assertTrue(self.metrics_manager.opportunity)
        
        # Tall blocks should be in game_over_blocks
        self.assertIn("2x2-square", self.metrics_manager.game_over_blocks)
        self.assertIn("3x3-square", self.metrics_manager.game_over_blocks)
        
        # Horizontal line blocks should not be in game_over_blocks
        self.assertNotIn("1x2-line", self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_6(self):
        """Test game over block detection with scattered small gaps."""
        board = Board(8, 8)
        
        # Fill board except for isolated single cells
        board.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)

        self.assertTrue(self.metrics_manager.opportunity)
        
        # Only 1x1 blocks should fit
        for shape_name in self.config["shapes"].keys():
            if shape_name != "1x1-square":
                self.assertIn(shape_name, self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_8(self):
        """Test game over block detection with completely empty board (no game over blocks)."""
        board = Board(8, 8)
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)

        # Empty board should fit all blocks
        self.assertFalse(self.metrics_manager.opportunity)
        self.assertEqual(self.metrics_manager.game_over_blocks, ["None"])
    
    def test_game_over_block_detection_9(self):
        """Test game over block detection with zigzag pattern that only allows specific shapes."""
        board = Board(8, 8)
        
        # Create a zigzag pattern of filled cells
        board.grid = [
            [1, 1, 0, 0, 1, 1, 0, 0],
            [1, 1, 0, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [1, 1, 0, 0, 1, 1, 0, 0],
            [1, 1, 0, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1]
        ]
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        
        self.assertTrue(self.metrics_manager.opportunity)
        
        # Large blocks can't fit in this pattern
        self.assertIn("3x3-square", self.metrics_manager.game_over_blocks)
        
        # 2x2 blocks should fit
        self.assertNotIn("2x2-square", self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_10(self):
        """Test game over block detection with spiral pattern that restricts certain shapes."""
        board = Board(8, 8)
        
        # Create a spiral pattern
        board.grid = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        
        self.assertTrue(self.metrics_manager.opportunity)
        
        # 3x3 blocks can't fit in this pattern
        self.assertIn("3x3-square", self.metrics_manager.game_over_blocks)
    
        
    def test_game_over_block_detection_12(self):
        """Test game over block detection with a board that only has space for vertical blocks."""
        board = Board(8, 8)
        
        # Fill all cells except a vertical channel
        for c in range(8):
            for r in range(8):
                if not (r == 3 or r == 4):
                    board.grid[r][c] = 1
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        
        self.assertTrue(self.metrics_manager.opportunity)
        
        # Horizontal and large blocks can't fit
        for shape_name in self.config["shapes"].keys():
            big_shapes = [shape for shape in SHAPES if shape.startswith("3x") or shape.startswith("4x") or shape.startswith("5x")]
            if shape_name in big_shapes:
                self.assertIn(shape_name, self.metrics_manager.game_over_blocks)
        
        # Vertical blocks can fit
        self.assertNotIn("1x2-line", self.metrics_manager.game_over_blocks)
    
    def test_game_over_block_detection_13(self):
        """Test game over block detection with a board having only diagonal spaces."""
        board = Board(8, 8)
        
        # Fill all cells except a diagonal pattern
        for r in range(8):
            for c in range(8):
                board.grid[r][c] = 1 if (r != c) else 0
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        
        self.assertTrue(self.metrics_manager.opportunity)
        
        # Most blocks can't fit on a diagonal pattern
        for shape_name in self.config["shapes"].keys():
            if shape_name not in ["1x1-square", "2x2-diag", "2x2-diag-b", "3x3-diag", "3x3-diag-b"]:
                self.assertIn(shape_name, self.metrics_manager.game_over_blocks)
    
    def test_game_over_blocks_used_in_metrics(self):
        """Test that game_over_blocks are correctly included in the metrics dictionary."""
        board = Board(8, 8)
        
        # Fill most cells to create game over condition for larger blocks
        for r in range(6):
            for c in range(6):
                board.grid[r][c] = 1
        
        self.metrics_manager.update_game_state_metrics(board, [])
        self.metrics_manager.update_block_metrics(board)
        # Get all metrics
        metrics = self.metrics_manager.get_all_metrics()
        
        # Verify game_over_blocks is included
        self.assertIn("game_over_blocks", metrics)
        
        # Verify values match instance attributes
        self.assertEqual(metrics["game_over_blocks"], self.metrics_manager.game_over_blocks)

if __name__ == "__main__":
    unittest.main() 