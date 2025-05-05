# controllers/game_controller.py
import pygame
import time
import ctypes
import sys
from typing import Dict, Optional, Tuple

from controllers.base_controller import BaseController
from ui.views.main_view import MainView
from ui.colours import BG_COLOR
from data.stats_manager import StatsManager
from ui.layout import WINDOW_WIDTH, WINDOW_HEIGHT

from utils.window_metrics import outer_from_client 

class GameController(BaseController):
    """Controller for handling Pygame UI and game interactions."""
    
    def __init__(self, config: Dict):
        # Initialize base controller
        super().__init__(config)
        
        # --- Make process DPI-aware so we work in raw pixels (Windows only) ---
        if sys.platform == "win32":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)   # PER_MONITOR_DPI_AWARE
            except AttributeError:
                pass

        # Initialize pygame
        pygame.init()
        
        # ------------------------------------------------------------------
        # Initialize window with the defined window size constants
        # ------------------------------------------------------------------
        TARGET_CLIENT = (WINDOW_WIDTH, WINDOW_HEIGHT)
        outer_w, outer_h = outer_from_client(*TARGET_CLIENT)

        self.window = pygame.display.set_mode((outer_w, outer_h), pygame.RESIZABLE)
        self.client_size = TARGET_CLIENT          # store logical draw size
        self.window_size = (outer_w, outer_h)     # outer size (optional)
        # ------------------------------------------------------------------

        self.clock = pygame.time.Clock()
        
        # Initialize main view
        self.main_view = MainView(self.window_size)
        
        # Stats management
        self.stats_manager = StatsManager()
        
        # Flag to track if stats have been saved for current game over state
        self.stats_saved = False
        
        # Update sidebar fields from config
        self.main_view.update_config_fields(self.config)
    
    def apply_config_changes(self) -> bool:
        """Apply changes from the sidebar config inputs."""
        new_config = self.main_view.get_config_values()
        return self.update_config(new_config)
    
    def handle_board_click(self, grid_pos: Tuple[int, int]) -> bool:
        """Handle click on the game board to place a block."""
        if grid_pos:
            grid_y, grid_x = grid_pos
            # Try to place the block using controller's method
            return self.place_block(grid_y, grid_x)
        return False
    
    def handle_preview_click(self, preview_index: int) -> bool:
        """Handle click on the preview area to select a block."""
        if preview_index is not None:
            return self.select_block(preview_index)
        return False
    
    def save_game_stats(self) -> None:
        """Save current game stats to CSV when game is over."""
        if self.engine.game_over and not self.stats_saved:
            stats = {
                'score': self.engine.score,
                'lines': self.engine.lines,
                'blocks_placed': self.engine.blocks_placed
            }
            self.stats_manager.save_stats(stats)
            self.stats_saved = True
    
    def restart_game(self) -> None:
        """Reset the game with the current configuration."""
        self.reset_engine(preserve_config=True)
        # Reset the stats_saved flag for the new game
        self.stats_saved = False
    
    def _handle_core_events(self) -> bool:
        """Process core user input events. Protected method for reuse by subclasses."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                self.window_size = (event.w, event.h)
                self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
                # Update the main_view with the new window size
                self.main_view.handle_resize(self.window_size)
                self.main_view.update_config_fields(self.config)
            
            # Handle UI events via main_view
            ui_action = self.main_view.handle_event(event)
            if ui_action:
                if ui_action.get("action") == "apply":
                    self.apply_config_changes()
                elif ui_action.get("action") == "restart":
                    self.restart_game()
                elif ui_action.get("action") == "select_block":
                    self.handle_preview_click(ui_action.get("index"))
                elif ui_action.get("action") == "place_block":
                    self.handle_board_click(ui_action.get("position"))
            
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                elif event.key == pygame.K_F2:
                    self.restart_game()
                elif event.key == pygame.K_RETURN and self.engine.game_over:
                    # Restart game when Enter key is pressed and game is over
                    self.restart_game()
        
        return True
    
    def _draw_core(self, simulation_running=False, current_run=0, simulation_runs=0) -> None:
        """Core drawing logic. Protected method for reuse by subclasses."""
        # Use the main_view to draw all UI components
        self.main_view.draw(self.window, self.engine, simulation_running, current_run, simulation_runs)
        
        # Check for game over to save stats
        if self.engine.game_over and not simulation_running:
            # Save stats before displaying game over
            self.save_game_stats()
        
        pygame.display.flip()
    
    def _loop_core(self, custom_step_handler=None) -> None:
        """Core game loop logic. Protected method for reuse by subclasses.
        
        Args:
            custom_step_handler: Optional function to run custom per-frame logic
        """
        running = True
        while running:
            # Handle input events
            running = self.handle_events()
            
            # Update animations
            self.engine.update_animations()
            
            # Run any custom step logic if provided
            if custom_step_handler:
                custom_step_handler()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit()
    
    def handle_events(self) -> bool:
        """Process user input events."""
        return self._handle_core_events()
    
    def draw(self) -> None:
        """Render the game state to the screen."""
        self._draw_core(False, 0, 0)
    
    def loop(self) -> None:
        """Main game loop."""
        self._loop_core() 