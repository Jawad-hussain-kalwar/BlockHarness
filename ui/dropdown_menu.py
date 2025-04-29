import pygame
from ui.colours import WHITE, BLACK, LIGHT_GRAY, DARK_GRAY

class DropdownMenu:
    def __init__(self, rect, options, default_index=0):
        """Initialize a dropdown menu widget.
        
        Args:
            rect: The pygame.Rect for positioning and sizing the dropdown
            options: List of (value, display_text) tuples for dropdown items
            default_index: Index of the default selected option
        """
        self.rect = rect
        self.options = options
        self.selected_index = default_index if 0 <= default_index < len(options) else 0
        self.active = False
        self.expanded = False
        self.dropdown_height = len(options) * 30  # 30px per option
        
        # Define dropdown area when expanded
        self.dropdown_rect = pygame.Rect(
            rect.x, 
            rect.bottom, 
            rect.width, 
            self.dropdown_height
        )
    
    @property
    def selected_value(self):
        """Get the value (not display text) of the currently selected option."""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index][0]
        return None
    
    @property
    def selected_text(self):
        """Get the display text of the currently selected option."""
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index][1]
        return ""
    
    def set_selected_value(self, value):
        """Set the selected option by value."""
        for i, (opt_value, _) in enumerate(self.options):
            if opt_value == value:
                self.selected_index = i
                return True
        return False
    
    def handle_event(self, event):
        """Handle pygame events related to the dropdown menu.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if selection changed, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            
            # Check if click is inside main dropdown button
            if self.rect.collidepoint(x, y):
                self.active = True
                self.expanded = not self.expanded
                return False
            
            # If expanded, check if click is on an option
            if self.expanded and self.dropdown_rect.collidepoint(x, y):
                # Calculate which option was clicked
                relative_y = y - self.dropdown_rect.y
                option_index = relative_y // (self.dropdown_rect.height // len(self.options))
                
                if 0 <= option_index < len(self.options):
                    old_index = self.selected_index
                    self.selected_index = option_index
                    self.expanded = False
                    self.active = False
                    return self.selected_index != old_index
            
            # If click is outside dropdown, close it
            if self.expanded:
                self.expanded = False
                self.active = False
        
        return False
    
    def draw(self, surface, font):
        """Draw the dropdown menu on the given surface.
        
        Args:
            surface: The pygame surface to draw on
            font: The pygame font to use for text
        """
        # Draw the main dropdown button
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        
        # Draw the selected option text
        text_surf = font.render(self.selected_text, True, BLACK)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - 3),
            (self.rect.right - 5, self.rect.centery - 3),
            (self.rect.right - 10, self.rect.centery + 5)
        ]
        pygame.draw.polygon(surface, BLACK, arrow_points)
        
        # Draw expanded dropdown if active
        if self.expanded:
            # Draw dropdown background
            pygame.draw.rect(surface, WHITE, self.dropdown_rect)
            pygame.draw.rect(surface, BLACK, self.dropdown_rect, 1)
            
            # Draw each option
            for i, (_, text) in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.dropdown_rect.x, 
                    self.dropdown_rect.y + i * (self.dropdown_rect.height // len(self.options)),
                    self.dropdown_rect.width,
                    self.dropdown_rect.height // len(self.options)
                )
                
                # Highlight selected option
                if i == self.selected_index:
                    pygame.draw.rect(surface, LIGHT_GRAY, option_rect)
                
                # Draw option text
                text_surf = font.render(text, True, BLACK)
                text_rect = text_surf.get_rect(midleft=(option_rect.x + 5, option_rect.centery))
                surface.blit(text_surf, text_rect)
                
                # Draw separator line between options
                if i < len(self.options) - 1:
                    pygame.draw.line(
                        surface, 
                        DARK_GRAY, 
                        (option_rect.left, option_rect.bottom), 
                        (option_rect.right, option_rect.bottom), 
                        1
                    ) 