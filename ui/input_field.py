# ui/input_field.py
import pygame
from ui.colours import INPUT_BG, INPUT_BORDER, INPUT_FOCUS, FG_COLOR
from ui.layout import BORDER_RADIUS
from ui.font_manager import font_manager

# Input field states
class InputField:
    def __init__(self, rect, value, max_chars=20, numeric=False):
        self.rect = rect
        self.value = str(value)
        self.active = False
        self.max_chars = max_chars
        self.numeric = numeric
        self.font = font_manager.get_font('Ubuntu-Regular', 18)  # Default font
    
    def _handle_mouse(self, event):
        """Handle mouse events for the input field.
        
        Args:
            event: Pygame mouse event
        """
        self.active = self.rect.collidepoint(event.pos)
        
    def _handle_keyboard(self, event):
        """Handle keyboard events for the input field when active.
        
        Args:
            event: Pygame keyboard event
        """
        if not self.active:
            return
            
        if event.key == pygame.K_RETURN:
            self.active = False
        elif event.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
        elif event.unicode.isprintable():
            # Check if numeric input is allowed
            if self.numeric and not (event.unicode.isdigit() or event.unicode == '.'):
                return
            # Check max length
            if len(self.value) < self.max_chars:
                self.value += event.unicode
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse(event)
        
        elif event.type == pygame.KEYDOWN:
            self._handle_keyboard(event)
    
    def render(self, surface, font=None):
        # Use provided font or default font
        render_font = font or self.font
        
        # Use proper background color based on state
        bg_color = INPUT_FOCUS if self.active else INPUT_BG
        
        # render with rounded corners
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, INPUT_BORDER, self.rect, width=1, border_radius=BORDER_RADIUS)
        
        text_surf = render_font.render(self.value, True, FG_COLOR)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text_surf, text_rect) 