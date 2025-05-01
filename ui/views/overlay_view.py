# ui/views/overlay_view.py
import pygame
from ui.colours import BG_COLOR, OVERLAY, GREEN

class OverlayView:
    def __init__(self, window_size, large_font, font):
        self.window_size = window_size
        self.large_font = large_font
        self.font = font
        
        # Define button properties
        self.button_width = 150
        self.button_height = 40
        self.button_color = GREEN
        self.button_hover_color = (100, 200, 100)
        self.restart_button_rect = None
    
    def draw_game_over(self, surface, engine=None):
        # Create overlay surface
        overlay = pygame.Surface((self.window_size[0], self.window_size[1]), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        surface.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, BG_COLOR)
        text_x = (self.window_size[0] - game_over_text.get_width()) // 2
        text_y = (self.window_size[1] - game_over_text.get_height()) // 2 - 100
        surface.blit(game_over_text, (text_x, text_y))
        
        # Display game stats if engine is provided
        if engine:
            stats_y = text_y + 60
            
            # Display all game statistics
            stats = [
                f"Final Score: {engine.score}",
                f"Lines Cleared: {engine.lines}",
                f"Blocks Placed: {engine.blocks_placed}"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self.font.render(stat, True, BG_COLOR)
                stat_x = (self.window_size[0] - stat_text.get_width()) // 2
                surface.blit(stat_text, (stat_x, stats_y + i * 30))
        
        # Draw restart button
        button_x = (self.window_size[0] - self.button_width) // 2
        button_y = text_y + 200
        self.restart_button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.button_hover_color if self.restart_button_rect.collidepoint(mouse_pos) else self.button_color
        
        # Draw button
        pygame.draw.rect(surface, button_color, self.restart_button_rect, border_radius=5)
        
        # Draw button text
        restart_button_text = self.font.render("Restart Game", True, BG_COLOR)
        text_rect = restart_button_text.get_rect(center=self.restart_button_rect.center)
        surface.blit(restart_button_text, text_rect)
        
        # Draw key instruction
        restart_text = self.font.render("Press ENTER to restart", True, BG_COLOR)
        restart_x = (self.window_size[0] - restart_text.get_width()) // 2
        surface.blit(restart_text, (restart_x, button_y + self.button_height + 20))
        
    def is_restart_button_clicked(self, pos):
        """Check if the restart button was clicked at the given position"""
        if self.restart_button_rect:
            return self.restart_button_rect.collidepoint(pos)
        return False 