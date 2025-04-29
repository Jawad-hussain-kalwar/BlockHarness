# controllers/ai_controller.py
from typing import Dict, Optional, Tuple

from controllers.base_controller import BaseController
from ai.Greedy1 import AIPlayer


class AIController(BaseController):
    """Controller that uses an AI player to make gameplay decisions."""
    
    def __init__(self, config: Dict):
        """Initialize the AI controller with the provided configuration.
        
        Args:
            config: Game configuration dictionary
        """
        super().__init__(config)
        self.ai_player = AIPlayer()
    
    def step(self) -> bool:
        """Perform a single AI-driven game step.
        
        Returns:
            bool: True if a block was placed, False if game over or no move available
        """
        # If game is over, nothing to do
        if self.engine.game_over:
            return False
            
        # Get the current selected preview index
        selected_index = self.engine.get_selected_preview_index()
        if selected_index is None:
            return False
        preview_blocks = self.engine.get_preview_blocks()
        _, current_rotation = preview_blocks[selected_index]
        
        # Let the AI choose a move
        move = self.ai_player.choose_move(self.engine, selected_index, current_rotation)
        
        if move is not None:
            # AI found a valid move, apply it
            row, col = move
            return self.place_block(row, col)
        
        # If no move with current rotation, find a valid block and rotation
        next_valid = self.find_next_valid_block()
        if next_valid is not None:
            block_index, rotation = next_valid
            
            # Select this block
            self.select_block(block_index)
            
            # Apply rotation if needed
            current_rotation = self.engine.get_preview_blocks()[block_index][1]
            if rotation != current_rotation:
                rotations_needed = (rotation - current_rotation) % 4
                self.rotate_block(rotations_needed)
            
            # Let the AI choose a move for this block+rotation
            move = self.ai_player.choose_move(self.engine, block_index, rotation)
            if move is not None:
                row, col = move
                return self.place_block(row, col)
                
        return False
    
    def run_simulation(self, num_steps: int = -1) -> Dict:
        """Run the AI simulation for a specified number of steps or until game over.
        
        Args:
            num_steps: Number of steps to run, or -1 for unlimited
            
        Returns:
            Dictionary containing final game state information
        """
        steps_taken = 0
        
        while not self.engine.game_over and (num_steps == -1 or steps_taken < num_steps):
            if not self.step():
                # If AI couldn't make a move, the game should be over
                break
            steps_taken += 1
            
        return {
            "steps_taken": steps_taken,
            "score": self.engine.score,
            "lines": self.engine.lines,
            "blocks_placed": self.engine.blocks_placed,
            "game_over": self.engine.game_over
        } 