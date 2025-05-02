# controllers/base_controller.py
from typing import Dict, Optional, Tuple

from engine.game_engine import GameEngine


class BaseController:
    """Base controller interface that all game controllers should implement."""
    
    def __init__(self, config: Dict):
        """Initialize the controller with the provided configuration.
        
        Args:
            config: Game configuration dictionary
        """
        self.config = config
        self.engine = GameEngine(config)
    
    def reset_engine(self, preserve_config: bool = True) -> None:
        """Re-initialize the game engine and clear controller flags.
        
        Args:
            preserve_config: If True, keep the current configuration
                            If False, also reset config (not implemented yet)
        """
        # Preserve animation duration if engine exists
        animation_duration_ms = None
        if hasattr(self, 'engine'):
            animation_duration_ms = self.engine.animation_duration_ms
            
        # Re-create the game engine from config
        self.engine = GameEngine(self.config)
        
        # Restore animation duration if it was saved
        if animation_duration_ms is not None:
            self.engine.animation_duration_ms = animation_duration_ms
            
        # BaseController has no other flags to reset
    
    def restart_game(self):
        """Reset the game with the current configuration."""
        self.reset_engine(preserve_config=True)
    
    def update_config(self, new_config: Dict) -> bool:
        """Update the game configuration and restart.
        
        Args:
            new_config: New configuration parameters
            
        Returns:
            bool: True if successfully applied, False otherwise
        """
        if not new_config:
            return False
            
        # Update config
        self.config.update(new_config)
        
        # Restart game with new config
        self.restart_game()
        return True
    
    def select_block(self, index: int) -> bool:
        """Select a block from the preview.
        
        Args:
            index: Index of the block to select
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.engine.select_preview_block(index)
    
    def rotate_block(self, rotations: int = 1) -> bool:
        """Rotate the currently selected block.
        
        Args:
            rotations: Number of 90-degree clockwise rotations
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.engine.rotate_selected_block(rotations)
    
    def place_block(self, row: int, col: int) -> bool:
        """Place the currently selected block at the specified position.
        
        Args:
            row: Row position
            col: Column position
            
        Returns:
            bool: True if successfully placed, False otherwise
        """
        return self.engine.place_selected_block(row, col)
    
    def find_next_valid_block(self) -> Optional[Tuple[int, int]]:
        """Find the next placeable block in the preview.
        
        Returns:
            Tuple of (block_index, rotation) or None if no block can be placed
        """
        return self.engine.find_next_placeable_block()
    
    def get_game_metrics(self) -> Dict:
        """Get the current game metrics.
        
        Returns:
            Dictionary containing all game metrics
        """
        return self.engine.get_metrics()
    
    def get_game_state(self) -> Dict:
        """Get the current game state as a dictionary.
        
        Returns:
            Dictionary containing game state information
        """
        return {
            "board": self.engine.get_board_state(),
            "preview_blocks": self.engine.get_preview_blocks(),
            "selected_index": self.engine.get_selected_preview_index(),
            "score": self.engine.score,
            "lines": self.engine.lines,
            "blocks_placed": self.engine.blocks_placed,
            "game_over": self.engine.game_over,
            "metrics": self.engine.get_metrics()
        } 