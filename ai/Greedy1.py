# ai/Greedy1.py
from typing import Tuple, Optional
import copy

from engine.game_engine import GameEngine
from engine.board import Board
from ai.base_player import BaseAIPlayer


class Greedy1(BaseAIPlayer):
    """Greedy AI player that prioritizes line clears."""
    
    @property
    def name(self) -> str:
        return "Greedy"
        
    @property
    def description(self) -> str:
        return "Prioritizes placements that clear the most lines."
    
    def choose_move(self, engine: GameEngine, block_index: int) -> Optional[Tuple[int, int]]:
        """Choose the best placement for a block.
        
        Args:
            engine: The game engine
            block_index: Index of the block to place
            
        Returns:
            Tuple of (row, col) for best placement or None if no valid placement
        """
        # Get the board and block
        board_state = engine.get_board_state()
        board = Board.from_grid(board_state)
        
        preview_blocks = engine.get_preview_blocks()
        block = preview_blocks[block_index]
        
        best_position = None
        best_score = -1
        
        # Try each possible position
        for r in range(board.rows):
            for c in range(board.cols):
                if board.can_place(block, r, c):
                    # Create a temporary board
                    tmp_board = copy.deepcopy(board)
                    
                    # Place the block
                    tmp_board.place_block(block, r, c)
                    
                    # Count the number of lines that would be cleared
                    clear_cells = tmp_board.find_full_lines()
                    score = len(clear_cells)
                    
                    # Choose the placement that clears the most cells
                    if score > best_score:
                        best_score = score
                        best_position = (r, c)
                    # If scores are tied, prefer upper rows and leftmost columns
                    elif score == best_score and best_position is not None:
                        best_r, best_c = best_position
                        if r < best_r or (r == best_r and c < best_c):
                            best_position = (r, c)
        
        return best_position


# For backwards compatibility - this will maintain compatibility with existing code
AIPlayer = Greedy1
