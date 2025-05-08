# ui/views/hud_view.py
import pygame
from ui.colours import FG_COLOR, TEXT_SECONDARY, STAT_BOX_BG, STAT_BOX_BORDER
from ui.layout import PADDING, STATS_HEIGHT, STATS_BOX_WIDTH, STATS_BOX_HEIGHT, HINTS_HEIGHT, HINTS_PADDING

class HudView:
    def __init__(self, parent_rect, stats_height, font):
        self.parent_rect = parent_rect
        self.font = font
        
        # Create stat box rectangles
        self.stat_boxes = []
        for i in range(3):
            box_x = parent_rect.x + PADDING + i * (STATS_BOX_WIDTH + PADDING)
            box_y = parent_rect.y + PADDING
            self.stat_boxes.append(pygame.Rect(box_x, box_y, STATS_BOX_WIDTH, STATS_BOX_HEIGHT))
    
    def render(self, surface, engine):
        # render score box
        score_box = self.stat_boxes[0]
        pygame.draw.rect(surface, STAT_BOX_BG, score_box)
        pygame.draw.rect(surface, STAT_BOX_BORDER, score_box, 1)
        score_text = self.font.render("SCORE", True, FG_COLOR)
        score_value = self.font.render(f"{engine.score}", True, FG_COLOR)
        
        # Center text in the box
        surface.blit(score_text, (
            score_box.x + (score_box.width - score_text.get_width()) // 2,
            score_box.y + 10
        ))
        surface.blit(score_value, (
            score_box.x + (score_box.width - score_value.get_width()) // 2,
            score_box.y + score_box.height - score_value.get_height() - 10
        ))
        
        # render lines box
        lines_box = self.stat_boxes[1]
        pygame.draw.rect(surface, STAT_BOX_BG, lines_box)
        pygame.draw.rect(surface, STAT_BOX_BORDER, lines_box, 1)
        lines_text = self.font.render("LINES", True, FG_COLOR)
        lines_value = self.font.render(f"{engine.lines}", True, FG_COLOR)
        
        surface.blit(lines_text, (
            lines_box.x + (lines_box.width - lines_text.get_width()) // 2,
            lines_box.y + 10
        ))
        surface.blit(lines_value, (
            lines_box.x + (lines_box.width - lines_value.get_width()) // 2,
            lines_box.y + lines_box.height - lines_value.get_height() - 10
        ))
        
        # render blocks box
        blocks_box = self.stat_boxes[2]
        pygame.draw.rect(surface, STAT_BOX_BG, blocks_box)
        pygame.draw.rect(surface, STAT_BOX_BORDER, blocks_box, 1)
        blocks_text = self.font.render("BLOCKS", True, FG_COLOR)
        blocks_value = self.font.render(f"{engine.blocks_placed}", True, FG_COLOR)
        
        surface.blit(blocks_text, (
            blocks_box.x + (blocks_box.width - blocks_text.get_width()) // 2,
            blocks_box.y + 10
        ))
        surface.blit(blocks_value, (
            blocks_box.x + (blocks_box.width - blocks_value.get_width()) // 2,
            blocks_box.y + blocks_box.height - blocks_value.get_height() - 10
        ))
        
        # render hint text
        hint_y = self.parent_rect.y + STATS_HEIGHT + (HINTS_HEIGHT - self.font.get_height()) // 2
        hint1 = self.font.render("Click preview to select", True, TEXT_SECONDARY)
        hint2 = self.font.render("S = settings", True, TEXT_SECONDARY)
        hint3 = self.font.render("Esc = quit", True, TEXT_SECONDARY)
        
        hint1_width = hint1.get_width()
        hint2_width = hint2.get_width()
        hint3_width = hint3.get_width()
        
        # Calculate positions to evenly space the hints
        total_width = hint1_width + hint2_width + hint3_width
        spacing = (self.parent_rect.width - total_width) / 4
        
        surface.blit(hint1, (self.parent_rect.x + spacing, hint_y))
        surface.blit(hint2, (self.parent_rect.x + 2 * spacing + hint1_width, hint_y))
        surface.blit(hint3, (self.parent_rect.x + 3 * spacing + hint1_width + hint2_width, hint_y)) 