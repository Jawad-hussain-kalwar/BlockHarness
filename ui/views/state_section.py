# ui/views/state_section.py
import pygame
from ui.colours import (
    SIDEBAR_BG, SECTION_BG, SECTION_BORDER, TEXT_PRIMARY
)
from ui.layout import (
    SIDEBAR_WIDTH, SIDEBAR_PADDING, BORDER_RADIUS
)

class StateSection:
    """View for the Game State section that displays game state information."""
    
    def __init__(self, window_size, font, small_font):
        self.window_size = window_size
        self.font = font
        self.small_font = small_font
        
        # Calculate right sidebar position (on the right edge of the window)
        self.sidebar_width = SIDEBAR_WIDTH
        self.sidebar_x = window_size[0] - self.sidebar_width
    
    def draw(self, surface, engine):
        """Draw the Game State section.
        
        Args:
            surface: Pygame surface to draw on
            engine: Game engine instance
        """
        # Draw right sidebar background
        sidebar_rect = pygame.Rect(self.sidebar_x, 0, self.sidebar_width, self.window_size[1])
        pygame.draw.rect(surface, SIDEBAR_BG, sidebar_rect)
        
        # Draw section panel with rounded corners
        section_rect = pygame.Rect(
            self.sidebar_x + SIDEBAR_PADDING // 2, 
            SIDEBAR_PADDING // 2, 
            self.sidebar_width - SIDEBAR_PADDING, 
            self.window_size[1] - SIDEBAR_PADDING
        )
        pygame.draw.rect(surface, SECTION_BG, section_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, section_rect, width=1, border_radius=BORDER_RADIUS)
        
        # Draw section title
        title = self.font.render("Game State", True, TEXT_PRIMARY)
        title_x = self.sidebar_x + SIDEBAR_PADDING
        title_y = SIDEBAR_PADDING
        surface.blit(title, (title_x, title_y))
        
        # This section is empty for now as specified in the approved plan
        # Additional game state information will be added in future updates 