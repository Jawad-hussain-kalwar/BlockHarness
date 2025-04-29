# ai/EdgeHugging.py
from typing import Tuple, Optional, List

from engine.game_engine import GameEngine
from ai.base_player import BaseAIPlayer


class EdgeHuggingAIPlayer(BaseAIPlayer):
    """Edge hugging strategy: prefer placements along the edges of the board."""
    
    @property
    def name(self) -> str:
        return "Edge Hugger"
    
    @property
    def description(self) -> str:
        return "Prefers placing blocks along the edges of the board."
    
    def _calculate_edge_score(self, engine: GameEngine, row: int, col: int, block_index: int, rotation: int) -> int:
        """Calculate a score based on how many cells would be along edges.
        
        Args:
            engine: The game engine
            row: Row placement position
            col: Column placement position
            block_index: Index of the block to place
            rotation: Rotation to apply to the block
            
        Returns:
            Score representing how many cells would be along edges
        """
        # Get the block with rotation
        block_list = engine.get_preview_blocks()
        if not 0 <= block_index < len(block_list):
            return 0
            
        block, _ = block_list[block_index]
        rotated_block = block.rotate_clockwise(rotation)
        
        # Calculate edges of the board
        board_width = engine.board.width
        board_height = engine.board.height
        
        # Calculate edge score
        edge_score = 0
        
        # Iterate through the block cells
        for r in range(len(rotated_block.grid)):
            for c in range(len(rotated_block.grid[0])):
                if rotated_block.grid[r][c]:
                    # Calculate board position of this cell
                    board_r = row + r
                    board_c = col + c
                    
                    # Check if cell is along an edge
                    if (board_r == 0 or board_r == board_height - 1 or 
                        board_c == 0 or board_c == board_width - 1):
                        edge_score += 1
        
        return edge_score
    
    def choose_move(self, engine: GameEngine, block_index: int, rotation: int) -> Optional[Tuple[int, int]]:
        """Choose the best placement for a block.
        
        Args:
            engine: The game engine
            block_index: Index of the block to place
            rotation: Rotation to apply to the block
            
        Returns:
            Tuple of (row, col) for best placement or None if no valid placement
        """
        best_moves: List[Tuple[int, int]] = []
        best_score = -1
        
        # Get all valid placements for this block+rotation
        valid_placements = engine.get_valid_placements(block_index, rotation)
        
        if not valid_placements:
            return None
            
        # Score each placement using edge hugging heuristic
        for r, c in valid_placements:
            # Calculate edge score
            edge_score = self._calculate_edge_score(engine, r, c, block_index, rotation)
            
            # Check if we clear any lines as a secondary objective
            from copy import deepcopy
            tmp_board = deepcopy(engine.board)
            
            # Get the block with rotation
            block_list = engine.get_preview_blocks()
            if not 0 <= block_index < len(block_list):
                continue
                
            block, _ = block_list[block_index]
            rotated_block = block.rotate_clockwise(rotation)
            
            # Place the block
            tmp_board.place_block(rotated_block, r, c)
            
            # Check how many lines would be cleared
            cleared = tmp_board.clear_full_lines()
            clear_score = len(cleared) * 10  # Weigh line clears more heavily
            
            # Combined score
            score = edge_score + clear_score
            
            if score > best_score:
                best_score = score
                best_moves = [(r, c)]
            elif score == best_score:
                best_moves.append((r, c))
                
        # If we have multiple moves with the same score, pick the leftmost one
        if best_moves:
            best_moves.sort(key=lambda pos: pos[1])  # Sort by column
            return best_moves[0]
                
        return None 