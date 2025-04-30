# ui/input_field.py
import pygame
from ui.colours import INPUT_BG, INPUT_BORDER, INPUT_FOCUS, BLACK
from ui.layout import BORDER_RADIUS

# Input field states
class InputField:
    def __init__(self, rect, value, max_chars=20, numeric=False):
        self.rect = rect
        self.value = str(value)
        self.active = False
        self.max_chars = max_chars
        self.numeric = numeric
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.unicode.isprintable():
                if self.numeric and not (event.unicode.isdigit() or event.unicode == ','):
                    return
                if len(self.value) < self.max_chars:
                    self.value += event.unicode
    
    def draw(self, surface, font):
        # Use proper background color based on state
        bg_color = INPUT_FOCUS if self.active else INPUT_BG
        
        # Draw with rounded corners
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, INPUT_BORDER, self.rect, width=1, border_radius=BORDER_RADIUS)
        
        text_surf = font.render(self.value, True, BLACK)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text_surf, text_rect) 