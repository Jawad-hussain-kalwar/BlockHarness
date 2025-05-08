# ui/views/game_section.py
import pygame
from ui.layout import (
    PADDING, GAME_WIDTH, SECTION_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    STATS_HEIGHT, HINTS_HEIGHT, BOARD_SIZE, BOARD_PADDING_W, PREVIEW_HEIGHT, PREVIEW_BLOCK,
    PREVIEW_PADDING_H, PREVIEW_PADDING_V, PREVIEW_GAP
)
from ui.views.board_view import BoardView
from ui.views.preview_view import PreviewView
from ui.views.hud_view import HudView
from ui.views.overlay_view import OverlayView

class GameSection:
    """Game section that consolidates board, preview, and HUD views."""
    
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        
        # Fixed position at the top of the window
        x_origin = PADDING
        y_origin = PADDING
        self.rect = pygame.Rect(x_origin, y_origin, GAME_WIDTH - 2*PADDING, SECTION_HEIGHT)
        
        # Calculate cell sizes based on board_size
        self.cell_size = BOARD_SIZE // 8  # For a 8x8 board
        self.preview_cell_size = PREVIEW_BLOCK // 5  # For 5x5 preview blocks
        
        # Initialize views with fixed positioning
        self.board_view = BoardView(
            (self.rect.x + BOARD_PADDING_W, self.rect.y + STATS_HEIGHT + HINTS_HEIGHT),
            self.cell_size,
            board_size=BOARD_SIZE
        )
        
        # Preview view starting position is below the board
        preview_x = self.rect.x
        preview_y = self.rect.y + STATS_HEIGHT + HINTS_HEIGHT + BOARD_SIZE
        self.preview_view = PreviewView(
            (preview_x, preview_y),
            self.preview_cell_size,
            PREVIEW_BLOCK,
            PREVIEW_PADDING_H,
            PREVIEW_PADDING_V,
            PREVIEW_GAP
        )
        
        # HUD view at the top of the game section
        self.hud_view = HudView(
            self.rect,
            STATS_HEIGHT,
            self.font
        )
        
        self.overlay_view = OverlayView(self.font, small_font)
    
    def render(self, surface, engine, simulation_over=False, simulation_stats=None):
        """render all game section components."""
        # render board
        self.board_view.render(surface, engine)
        
        # Get preview data from engine
        preview_blocks = engine.get_preview_blocks()
        selected_index = engine.get_selected_preview_index()
        
        # render preview blocks
        self.preview_view.render(surface, preview_blocks, selected_index)
        
        # render HUD (score, lines, blocks, hints)
        self.hud_view.render(surface, engine)
        
        # render simulation over overlay if simulation just finished
        if simulation_over:
            self.overlay_view.render_simulation_over(surface, simulation_stats)
        # Otherwise render regular game over if needed
        elif engine.game_over:
            self.overlay_view.render_game_over(surface, engine)
    
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
        board_rect = pygame.Rect(self.rect.x + BOARD_PADDING_W, self.rect.y + STATS_HEIGHT + HINTS_HEIGHT, board_width, board_height)
        
        if board_rect.collidepoint(x, y):
            # Calculate grid position
            grid_x = (x - (self.rect.x + BOARD_PADDING_W)) // self.cell_size
            grid_y = (y - (self.rect.y + STATS_HEIGHT + HINTS_HEIGHT)) // self.cell_size
            
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
        # Use the preview_view's rectangles for click detection
        for i, preview_rect in enumerate(self.preview_view.preview_rects):
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