# ui/views/overlay_view.py
import pygame
from ui.colours import BG_COLOR, OVERLAY, GREEN
from ui.font_manager import font_manager
from ui.layout import WINDOW_WIDTH, WINDOW_HEIGHT

class OverlayView:
    def __init__(self, large_font, font):
        self.large_font = large_font
        self.font = font
        
        # Create additional larger fonts for the overlay screens
        self.game_over_font = font_manager.get_font('Ubuntu-Regular', 100)
        self.stats_font = font_manager.get_font('Ubuntu-Regular', 40)
        
        # Define button properties
        self.button_width = 220  # Slightly wider
        self.button_height = 60
        self.button_color = GREEN
        self.button_hover_color = (100, 200, 100)
        self.button_outline_color = (0, 100, 0)  # Dark green outline
        self.restart_button_rect = None
        
        # Define outline colors
        self.game_over_outline_color = (139, 0, 0)  # Crimson
        self.simulation_outline_color = (0, 0, 139)  # Dark blue
        self.stats_outline_color = (0, 0, 0)  # Black
        self.outline_thickness = 2
    
    def _render_text_with_outline(self, font, text, color, outline_color, outline_width):
        """Helper method to render text with outline"""
        # Render the outline by rendering the text multiple times with offsets
        text_surface = font.render(text, True, outline_color)
        outlined_surface = pygame.Surface(
            (text_surface.get_width() + outline_width*2, 
             text_surface.get_height() + outline_width*2),
            pygame.SRCALPHA
        )
        
        # render the text multiple times for the outline
        for dx in range(-outline_width, outline_width+1):
            for dy in range(-outline_width, outline_width+1):
                if dx != 0 or dy != 0:  # Skip the center position
                    outlined_surface.blit(text_surface, (outline_width + dx, outline_width + dy))
        
        # render the main text in the center
        main_text = font.render(text, True, color)
        outlined_surface.blit(main_text, (outline_width, outline_width))
        
        return outlined_surface
    
    def render_game_over(self, surface, engine=None):
        # Create overlay surface
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        surface.blit(overlay, (0, 0))
        
        # render game over text with crimson outline
        game_over_text = self._render_text_with_outline(
            self.game_over_font, "GAME OVER", (255, 255, 255), 
            self.game_over_outline_color, self.outline_thickness
        )
        text_x = (WINDOW_WIDTH - game_over_text.get_width()) // 2
        text_y = (WINDOW_HEIGHT // 3) - (game_over_text.get_height() // 2)  # Improved positioning
        surface.blit(game_over_text, (text_x, text_y))
        
        # Display game stats if engine is provided
        if engine:
            stats_y = text_y + game_over_text.get_height() + 40  # Better spacing
            
            # Display all game statistics with black outline
            stats = [
                f"Final Score: {engine.score}",
                f"Lines Cleared: {engine.lines}",
                f"Blocks Placed: {engine.blocks_placed}"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self._render_text_with_outline(
                    self.stats_font, stat, (255, 255, 255),
                    self.stats_outline_color, self.outline_thickness
                )
                stat_x = (WINDOW_WIDTH - stat_text.get_width()) // 2
                surface.blit(stat_text, (stat_x, stats_y + i * 60))  # More space between stats
        
        # render restart button with dark green outline
        button_y = WINDOW_HEIGHT * 3 // 4  # Position at 3/4 of the screen height
        button_x = (WINDOW_WIDTH - self.button_width) // 2
        self.restart_button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.button_hover_color if self.restart_button_rect.collidepoint(mouse_pos) else self.button_color
        
        # render button with outline
        pygame.draw.rect(surface, button_color, self.restart_button_rect, border_radius=8)
        pygame.draw.rect(surface, self.button_outline_color, self.restart_button_rect, 
                        width=self.outline_thickness, border_radius=8)
        
        # render button text
        restart_button_text = self.large_font.render("Restart Game", True, BG_COLOR)
        text_rect = restart_button_text.get_rect(center=self.restart_button_rect.center)
        surface.blit(restart_button_text, text_rect)
        
        # render key instructions with more space
        controls_y = button_y + self.button_height + 30
        restart_text = self.font.render("Press ENTER to restart", True, (255, 255, 255))
        restart_x = (WINDOW_WIDTH - restart_text.get_width()) // 2
        surface.blit(restart_text, (restart_x, controls_y))
        
        # Add ESC to exit instruction
        exit_text = self.font.render("Press ESC to exit", True, (255, 255, 255))
        exit_x = (WINDOW_WIDTH - exit_text.get_width()) // 2
        surface.blit(exit_text, (exit_x, controls_y + 30))
    
    def render_simulation_over(self, surface, simulation_stats=None):
        """render the simulation over screen with batch run statistics."""
        # Create overlay surface
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY)
        surface.blit(overlay, (0, 0))
        
        # render simulation over text with dark blue outline
        sim_over_text = self._render_text_with_outline(
            self.game_over_font, "SIMULATION COMPLETE", (255, 255, 255),
            self.simulation_outline_color, self.outline_thickness
        )
        text_x = (WINDOW_WIDTH - sim_over_text.get_width()) // 2
        text_y = (WINDOW_HEIGHT // 3) - (sim_over_text.get_height() // 2)  # Improved positioning
        surface.blit(sim_over_text, (text_x, text_y))
        
        # Display simulation batch stats if provided
        if simulation_stats:
            stats_y = text_y + sim_over_text.get_height() + 40  # Better spacing
            
            # Display all simulation statistics with black outline
            stats = [
                f"Total Runs: {simulation_stats['runs']}",
                f"Average Score: {simulation_stats['avg_score']:.2f}",
                f"Average Lines: {simulation_stats['avg_lines']:.2f}",
                f"Average Blocks: {simulation_stats['avg_blocks']:.2f}"
            ]
            
            for i, stat in enumerate(stats):
                stat_text = self._render_text_with_outline(
                    self.stats_font, stat, (255, 255, 255),
                    self.stats_outline_color, self.outline_thickness
                )
                stat_x = (WINDOW_WIDTH - stat_text.get_width()) // 2
                surface.blit(stat_text, (stat_x, stats_y + i * 60))  # More space between stats
        
        # render restart button with dark green outline
        button_y = WINDOW_HEIGHT * 3 // 4  # Position at 3/4 of the screen height
        button_x = (WINDOW_WIDTH - self.button_width) // 2
        self.restart_button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
        
        # Check if mouse is hovering over button
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.button_hover_color if self.restart_button_rect.collidepoint(mouse_pos) else self.button_color
        
        # render button with outline
        pygame.draw.rect(surface, button_color, self.restart_button_rect, border_radius=8)
        pygame.draw.rect(surface, self.button_outline_color, self.restart_button_rect, 
                        width=self.outline_thickness, border_radius=8)
        
        # render button text
        restart_button_text = self.large_font.render("New Simulation", True, BG_COLOR)
        text_rect = restart_button_text.get_rect(center=self.restart_button_rect.center)
        surface.blit(restart_button_text, text_rect)
        
        # render key instructions with more space
        controls_y = button_y + self.button_height + 30
        restart_text = self.font.render("Press ENTER to restart", True, (255, 255, 255))
        restart_x = (WINDOW_WIDTH - restart_text.get_width()) // 2
        surface.blit(restart_text, (restart_x, controls_y))
        
        # Add ESC to exit instruction
        exit_text = self.font.render("Press ESC to exit", True, (255, 255, 255))
        exit_x = (WINDOW_WIDTH - exit_text.get_width()) // 2
        surface.blit(exit_text, (exit_x, controls_y + 30))
        
    def is_restart_button_clicked(self, pos):
        """Check if the restart button was clicked at the given position"""
        if self.restart_button_rect:
            # Convert position to float for accurate collision detection
            x, y = float(pos[0]), float(pos[1])
            return self.restart_button_rect.collidepoint(x, y)
        return False