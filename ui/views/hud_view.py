# ui/views/hud_view.py
import pygame
from ui.colours import BLACK, DARK_GRAY

class HudView:
    def __init__(self, preview_origin, preview_spacing, font):
        self.preview_origin = preview_origin
        self.preview_spacing = preview_spacing
        self.font = font
    
    def draw(self, surface, engine):
        # Draw game stats - adjusted positioning based on new preview spacing
        stats_y = self.preview_origin[1] + 3 * self.preview_spacing + 32
        
        score_text = self.font.render(f"Score: {engine.score}", True, BLACK)
        surface.blit(score_text, (self.preview_origin[0], stats_y))
        
        lines_text = self.font.render(f"Lines: {engine.lines}", True, BLACK)
        surface.blit(lines_text, (self.preview_origin[0], stats_y + 24))
        
        blocks_text = self.font.render(f"Blocks: {engine.blocks_placed}", True, BLACK)
        surface.blit(blocks_text, (self.preview_origin[0], stats_y + 48))
        
        # Draw hint text
        hint_y = stats_y + 100
        hint1 = self.font.render("Click preview to select", True, DARK_GRAY)
        hint2 = self.font.render("R = rotate", True, DARK_GRAY)
        hint3 = self.font.render("Esc = quit", True, DARK_GRAY)
        
        surface.blit(hint1, (self.preview_origin[0], hint_y))
        surface.blit(hint2, (self.preview_origin[0], hint_y + 24))
        surface.blit(hint3, (self.preview_origin[0], hint_y + 48)) 