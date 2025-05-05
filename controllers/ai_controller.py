# controllers/ai_controller.py
from typing import Dict, Optional, Tuple

from controllers.base_controller import BaseController
from ai.base_player import BaseAIPlayer
from ai.registry import registry


class AIController(BaseController):
    """Controller that uses an AI player to make gameplay decisions."""
    
    def __init__(self, config: Dict, ai_player_name: Optional[str] = None):
        """Initialize the AI controller with the provided configuration.
        
        Args:
            config: Game configuration dictionary
            ai_player_name: Optional name of the AI player to use. If None, uses the default Greedy AI.
        """
        super().__init__(config)
        
        # Use the specified AI player, or fall back to Greedy
        if ai_player_name:
            try:
                self.ai_player = registry.create_player(ai_player_name)
            except KeyError:
                print(f"AI player '{ai_player_name}' not found, falling back to Greedy")
                self.ai_player = registry.create_player("Greedy")
        else:
            self.ai_player = registry.create_player("Greedy")
    
    def set_ai_player(self, ai_player_name: str) -> bool:
        """Set the AI player to use.
        
        Args:
            ai_player_name: Name of the AI player to use
            
        Returns:
            True if the AI player was set successfully, False otherwise
        """
        try:
            self.ai_player = registry.create_player(ai_player_name)
            return True
        except KeyError:
            print(f"AI player '{ai_player_name}' not found")
            return False
    
    def get_ai_player_name(self) -> str:
        """Get the name of the current AI player.
        
        Returns:
            The name of the current AI player
        """
        return self.ai_player.name
    
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
        
        # Let the AI choose a move
        move = self.ai_player.choose_move(self.engine, selected_index)
        
        if move is not None:
            # AI found a valid move, apply it
            row, col = move
            return self.place_block(row, col)
        
        # If no move with current block, find another valid block
        next_valid = self.find_next_valid_block()
        if next_valid is not None:
            # Select this block
            self.select_block(next_valid)
            
            # Let the AI choose a move for this block
            move = self.ai_player.choose_move(self.engine, next_valid)
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