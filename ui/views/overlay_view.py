# ui/views/overlay_view.py
import pygame
from ui.colours import WHITE, OVERLAY

class OverlayView:
    def __init__(self, window_size, large_font, font):
        self.window_size = window_size
        self.large_font = large_font
        self.font = font
    
    def draw_game_over(self, surface):
        # Create overlay surface
        overlay = pygame.Surface((self.window_size[0], self.window_size[1]), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        surface.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, WHITE)
        restart_text = self.font.render("F2 to restart", True, WHITE)
        
        text_x = (self.window_size[0] - game_over_text.get_width()) // 2
        text_y = (self.window_size[1] - game_over_text.get_height()) // 2
        
        surface.blit(game_over_text, (text_x, text_y))
        surface.blit(restart_text, (text_x + 50, text_y + 50)) 