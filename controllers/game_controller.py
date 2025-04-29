# controllers/game_controller.py
import pygame
import time
from typing import Dict, Optional, Tuple

from controllers.base_controller import BaseController
from ui.views.board_view import BoardView
from ui.views.preview_view import PreviewView
from ui.views.sidebar_view import SidebarView
from ui.views.hud_view import HudView
from ui.views.overlay_view import OverlayView
from ui.colours import WHITE
from data.stats_manager import StatsManager


class GameController(BaseController):
    """Controller for handling Pygame UI and game interactions."""
    
    def __init__(self, config: Dict):
        # Initialize base controller
        super().__init__(config)
        
        # Initialize pygame
        pygame.init()
        self.window_size = (1100, 720)  # Increased width for left sidebar
        self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE)
        pygame.display.set_caption("BlockHarness – Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 18)
        self.large_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Game state
        self.cell_size = 64
        self.preview_cell_size = 32  # Half size for preview blocks
        self.board_origin = (280, 16)  # Moved right to make space for left sidebar
        self.preview_origin = (280 + 8 * self.cell_size + 32, 16)
        self.preview_spacing = 160  # Spacing between preview blocks
        
        # Initialize views
        self.board_view = BoardView(self.board_origin, self.cell_size)
        self.preview_view = PreviewView(self.preview_origin, self.preview_cell_size, self.preview_spacing)
        self.sidebar_view = SidebarView(self.window_size, self.font, self.small_font)
        self.hud_view = HudView(self.preview_origin, self.preview_spacing, self.font)
        self.overlay_view = OverlayView(self.window_size, self.large_font, self.font)
        
        # Stats management
        self.stats_manager = StatsManager()
        
        # Flag to track if stats have been saved for current game over state
        self.stats_saved = False
        
        # Update sidebar fields from config
        self.sidebar_view.update_config_fields(self.config)
    
    def apply_config_changes(self) -> bool:
        """Apply changes from the sidebar config inputs."""
        new_config = self.sidebar_view.get_config_values()
        return self.update_config(new_config)
    
    def handle_board_click(self, x: int, y: int) -> bool:
        """Handle click on the game board to place a block."""
        board_width = 8 * self.cell_size
        board_height = 8 * self.cell_size
        board_rect = pygame.Rect(self.board_origin[0], self.board_origin[1], board_width, board_height)
        
        if board_rect.collidepoint(x, y):
            # Calculate grid position
            grid_x = (x - self.board_origin[0]) // self.cell_size
            grid_y = (y - self.board_origin[1]) // self.cell_size
            
            # Try to place the block using controller's method
            return self.place_block(grid_y, grid_x)
            
        return False
    
    def handle_preview_click(self, x: int, y: int) -> bool:
        """Handle click on the preview area to select a block."""
        preview_blocks = self.engine.get_preview_blocks()
        
        for i in range(min(3, len(preview_blocks))):
            preview_rect = pygame.Rect(
                self.preview_origin[0],
                self.preview_origin[1] + i * self.preview_spacing,
                self.preview_cell_size * 4,
                self.preview_cell_size * 4
            )
            if preview_rect.collidepoint(x, y):
                return self.select_block(i)
                
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
            
            # Handle sidebar events
            action = self.sidebar_view.handle_event(event)
            if action == "apply":
                self.apply_config_changes()
            
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                elif event.key == pygame.K_F2:
                    self.restart_game()
                elif event.key == pygame.K_r and not self.engine.game_over:
                    self.rotate_block()
                elif event.key == pygame.K_RETURN and self.engine.game_over:
                    # Restart game when Enter key is pressed and game is over
                    self.restart_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                
                # Handle restart button click when game is over
                if self.engine.game_over and self.overlay_view.is_restart_button_clicked((x, y)):
                    self.restart_game()
                    continue
                
                # Don't process game clicks if game over
                if self.engine.game_over:
                    continue
                
                # Check if click is on the preview area
                self.handle_preview_click(x, y)
                
                # Check if click is on the board area
                self.handle_board_click(x, y)
        
        return True
    
    def _draw_core(self, simulation_running=False, current_run=0, simulation_runs=0) -> None:
        """Core drawing logic. Protected method for reuse by subclasses."""
        self.window.fill(WHITE)
        
        # Draw all views
        self.sidebar_view.draw(self.window, simulation_running, current_run, simulation_runs)
        self.board_view.draw(self.window, self.engine)
        
        # Get preview data from engine
        preview_blocks = self.engine.get_preview_blocks()
        selected_index = self.engine.get_selected_preview_index()
        
        self.preview_view.draw(self.window, preview_blocks, selected_index)
        self.hud_view.draw(self.window, self.engine)
        
        # Draw game over overlay if needed and not during simulation
        if self.engine.game_over and not simulation_running:
            # Save stats before displaying game over
            self.save_game_stats()
            # Pass engine to overlay view to display stats
            self.overlay_view.draw_game_over(self.window, self.engine)
        
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