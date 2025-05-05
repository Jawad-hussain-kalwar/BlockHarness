# ai/EdgeHugging.py
from typing import Dict, List, Tuple, Optional
from collections import deque
import copy
import random

from engine.game_engine import GameEngine
from engine.board import Board
from engine.block import Block
from ai.base_player import BaseAIPlayer


class EdgeHugging(BaseAIPlayer):
    """An AI player that tries to place blocks along the edges of the board."""
    
    @property
    def name(self) -> str:
        return "Edge Hugging"
    
    @property
    def description(self) -> str:
        return "Places blocks preferentially along the edges of the board."
    
    def choose_move(self, engine: GameEngine, block_index: int) -> Optional[Tuple[int, int]]:
        """Choose the best placement for the specified block.
        
        Args:
            engine: Game engine 
            block_index: Index of the block to place
            
        Returns:
            Tuple of (row, col) for best placement, or None if no valid placement
        """
        # Get the board state and block
        board_state = engine.get_board_state()
        board = Board.from_grid(board_state)
        preview_blocks = engine.get_preview_blocks()
        block = preview_blocks[block_index]
        
        # Calculate edge score for each possible placement
        best_position = None
        best_score = -float('inf')
        
        # Try placing the block at each position
        for r in range(board.rows):
            for c in range(board.cols):
                if board.can_place(block, r, c):
                    # Create a copy of the board and place the block
                    tmp_board = copy.deepcopy(board)
                    tmp_board.place_block(block, r, c)
                    
                    # Calculate edge score
                    edge_score = self._calculate_edge_score(tmp_board)
                    
                    # Calculate compactness score
                    compactness_score = self._calculate_compactness(tmp_board)
                    
                    # Calculate line clear score
                    line_clear_cells = tmp_board.find_full_lines()
                    line_clear_score = len(line_clear_cells) * 10  # High bonus for clearing lines
                    
                    # Calculate overall score (weighted)
                    total_score = (
                        edge_score * 1.5 +  # Edge score is important
                        compactness_score * 1.0 +  # Compactness is good too 
                        line_clear_score  # Line clearing is very valuable
                    )
                    
                    # Add small random factor to break ties
                    total_score += random.random() * 0.1
                    
                    # Update best position if this is better
                    if total_score > best_score:
                        best_score = total_score
                        best_position = (r, c)
        
        return best_position
    
    def _calculate_edge_score(self, board: Board) -> float:
        """Calculate how well blocks are placed along edges.
        
        Args:
            board: Board to evaluate
            
        Returns:
            Edge score (higher is better)
        """
        edge_score = 0
        rows, cols = board.rows, board.cols
        
        # Count filled cells along the edges
        edge_cells = 0
        total_edge_cells = 2 * rows + 2 * cols - 4  # Avoid double-counting corners
        
        # Check left and right edges
        for r in range(rows):
            if board.grid[r][0] == 1:  # Left edge
                edge_cells += 1
            if board.grid[r][cols-1] == 1:  # Right edge
                edge_cells += 1
                
        # Check top and bottom edges (excluding corners which were already counted)
        for c in range(1, cols-1):
            if board.grid[0][c] == 1:  # Top edge
                edge_cells += 1
            if board.grid[rows-1][c] == 1:  # Bottom edge
                edge_cells += 1
        
        # Calculate edge occupancy score
        edge_score = edge_cells / total_edge_cells if total_edge_cells > 0 else 0
        
        return edge_score * 100  # Scale to a larger range
    
    def _calculate_compactness(self, board: Board) -> float:
        """Calculate how compactly blocks are placed.
        
        Args:
            board: Board to evaluate
            
        Returns:
            Compactness score (higher is better)
        """
        # Count total filled cells
        filled_cells = sum(sum(row) for row in board.grid)
        
        # Count the number of adjacent filled cell pairs
        adjacent_count = 0
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] == 1:
                    # Check right neighbor
                    if c + 1 < board.cols and board.grid[r][c+1] == 1:
                        adjacent_count += 1
                    # Check bottom neighbor
                    if r + 1 < board.rows and board.grid[r+1][c] == 1:
                        adjacent_count += 1
        
        # Calculate compactness as ratio of adjacent pairs to filled cells
        max_adjacent = 2 * filled_cells - board.rows - board.cols
        compactness = adjacent_count / max_adjacent if max_adjacent > 0 else 0
        
        return compactness * 100  # Scale to a larger range 