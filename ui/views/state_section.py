# ui/views/state_section.py
import pygame
from ui.colours import (
    SECTION_BG, SECTION_BG, SECTION_BORDER, TEXT_PRIMARY
)
from ui.layout import (
    PADDING, DDA_WIDTH, SIM_WIDTH, GAME_WIDTH, STATE_WIDTH, SECTION_HEIGHT,
    SIDEBAR_WIDTH, SIDEBAR_PADDING, BORDER_RADIUS
)
from ui.debug import draw_debug_rect

class StateSection:
    """View for the Game State section that displays game state information."""
    
    def __init__(self, window_size, font, small_font):
        self.window_size = window_size
        self.font = font
        self.small_font = small_font
        
        # Initialize section rectangle with new layout constants
        x_origin = PADDING + DDA_WIDTH + PADDING + SIM_WIDTH + PADDING + GAME_WIDTH + PADDING
        y_origin = PADDING
        self.rect = pygame.Rect(x_origin, y_origin, STATE_WIDTH, SECTION_HEIGHT)
    
    def draw(self, surface, engine):
        """Draw the Game State section.
        
        Args:
            surface: Pygame surface to draw on
            engine: Game engine instance
        """
        # Draw section background
        pygame.draw.rect(surface, SECTION_BG, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, self.rect, width=1, border_radius=BORDER_RADIUS)
        
        # Draw debug border if enabled
        draw_debug_rect(surface, self.rect, "state")
        
        # Draw section title
        title = self.font.render("Game State", True, TEXT_PRIMARY)
        title_x = self.rect.x + PADDING
        title_y = self.rect.y + PADDING
        surface.blit(title, (title_x, title_y))
        
        # This section is empty for now as specified in the approved plan
        # Additional game state information will be added in future updates 