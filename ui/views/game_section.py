# ui/views/game_section.py
import pygame
from ui.layout import SIDEBAR_WIDTH
from ui.views.board_view import BoardView
from ui.views.preview_view import PreviewView
from ui.views.hud_view import HudView
from ui.views.overlay_view import OverlayView

class GameSection:
    """Game section that consolidates board, preview, and HUD views."""
    
    def __init__(self, window_size, font, small_font):
        self.window_size = window_size
        self.font = font
        self.small_font = small_font
        
        # Game configuration
        self.cell_size = 64
        self.preview_cell_size = 32  # Half size for preview blocks
        self.board_origin = (SIDEBAR_WIDTH + 20, 16)  # Adjust board position based on sidebar width
        self.preview_origin = (SIDEBAR_WIDTH + 20 + 8 * self.cell_size + 32, 16)
        self.preview_spacing = 160  # Spacing between preview blocks
        
        # Initialize views
        self.board_view = BoardView(self.board_origin, self.cell_size)
        self.preview_view = PreviewView(self.preview_origin, self.preview_cell_size, self.preview_spacing)
        self.hud_view = HudView(self.preview_origin, self.preview_spacing, self.font)
        self.overlay_view = OverlayView(self.window_size, font, small_font)
    
    def draw(self, surface, engine):
        """Draw all game section components."""
        # Draw board
        self.board_view.draw(surface, engine)
        
        # Get preview data from engine
        preview_blocks = engine.get_preview_blocks()
        selected_index = engine.get_selected_preview_index()
        
        # Draw preview blocks
        self.preview_view.draw(surface, preview_blocks, selected_index)
        
        # Draw HUD (score, lines, blocks, hints)
        self.hud_view.draw(surface, engine)
        
        # Draw game over overlay if needed
        if engine.game_over:
            self.overlay_view.draw_game_over(surface, engine)
    
    def handle_board_click(self, x, y):
        """Handle click on the game board to place a block.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Boolean: True if board was clicked, False otherwise
        """
        board_width = 8 * self.cell_size
        board_height = 8 * self.cell_size
        board_rect = pygame.Rect(self.board_origin[0], self.board_origin[1], board_width, board_height)
        
        if board_rect.collidepoint(x, y):
            # Calculate grid position
            grid_x = (x - self.board_origin[0]) // self.cell_size
            grid_y = (y - self.board_origin[1]) // self.cell_size
            
            # Return the grid position for the controller to handle
            return (grid_y, grid_x)
            
        return None
    
    def handle_preview_click(self, x, y):
        """Handle click on the preview area to select a block.
        
        Args:
            x: X coordinate of click
            y: Y coordinate of click
            
        Returns:
            Integer: Index of clicked preview block, or None if no preview was clicked
        """
        for i in range(3):  # We display 3 preview blocks
            preview_rect = pygame.Rect(
                self.preview_origin[0],
                self.preview_origin[1] + i * self.preview_spacing,
                self.preview_cell_size * 4,
                self.preview_cell_size * 4
            )
            if preview_rect.collidepoint(x, y):
                return i
                
        return None
    
    def is_restart_button_clicked(self, pos):
        """Check if the restart button was clicked.
        
        Args:
            pos: (x, y) coordinates of click
            
        Returns:
            Boolean: True if restart button was clicked, False otherwise
        """
        return self.overlay_view.is_restart_button_clicked(pos) 