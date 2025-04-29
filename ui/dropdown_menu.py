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
        
        # Increased height per option for better spacing (was 30)
        self.option_height = 40
        
        # Maximum number of visible options at once (to prevent overlap with other UI elements)
        self.max_visible_options = 4
        
        # Scroll position (if more options than max_visible_options)
        self.scroll_offset = 0
        
        # Calculate dropdown height (limited by max_visible_options)
        self.update_dropdown_height()
    
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
            # Use the title (value) instead of description (display_text)
            return self.options[self.selected_index][0]
        return ""
    
    def set_selected_value(self, value):
        """Set the selected option by value."""
        for i, (opt_value, _) in enumerate(self.options):
            if opt_value == value:
                self.selected_index = i
                return True
        return False
    
    def update_dropdown_height(self):
        """Update dropdown height when options change."""
        # Limit visible options to max_visible_options
        visible_options = min(max(1, len(self.options)), self.max_visible_options)
        self.dropdown_height = visible_options * self.option_height
        
        # Update dropdown rectangle
        self.dropdown_rect = pygame.Rect(
            self.rect.x, 
            self.rect.bottom, 
            self.rect.width, 
            self.dropdown_height
        )
    
    def handle_event(self, event):
        """Handle pygame events related to the dropdown menu.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if selection changed, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            # Check if click is inside main dropdown button
            if self.rect.collidepoint(x, y):
                self.active = True
                self.expanded = not self.expanded
                
                # Reset scroll position when opening dropdown
                if self.expanded:
                    # Try to position scroll so selected item is visible
                    self.ensure_selected_visible()
                return False
            
            # If expanded, check if click is on an option
            if self.expanded and self.dropdown_rect.collidepoint(x, y):
                # Calculate which option was clicked
                relative_y = y - self.dropdown_rect.y
                option_index = self.scroll_offset + (relative_y // self.option_height)
                
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
        return False
    
    def ensure_selected_visible(self):
        """Ensure the selected option is visible in the dropdown."""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_options:
            self.scroll_offset = max(0, self.selected_index - self.max_visible_options + 1)
    
    def _truncate_text(self, text, font, max_width):
        """Truncate text to fit within the specified width.
        
        Args:
            text: The text to truncate
            font: The pygame font to use for measuring text width
            max_width: The maximum width in pixels
            
        Returns:
            The truncated text
        """
        if font.size(text)[0] <= max_width:
            return text
        
        # Truncate text and add ellipsis
        for i in range(len(text), 0, -1):
            if font.size(text[:i] + "...")[0] <= max_width:
                return text[:i] + "..."
        
        return "..."
    
    def draw(self, surface, font):
        """Draw the dropdown menu on the given surface.
        
        Args:
            surface: The pygame surface to draw on
            font: The pygame font to use for text
        """
        # Update dropdown dimensions if needed
        if len(self.options) != 0 and self.dropdown_height != min(len(self.options), self.max_visible_options) * self.option_height:
            self.update_dropdown_height()
        
        # Draw the main dropdown button
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        
        # Draw the selected option text (truncated)
        truncated_text = self._truncate_text(self.selected_text, font, self.rect.width - 20)
        text_surf = font.render(truncated_text, True, BLACK)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - 3),
            (self.rect.right - 5, self.rect.centery - 3),
            (self.rect.right - 10, self.rect.centery + 5)
        ]
        pygame.draw.polygon(surface, BLACK, arrow_points)
        
        # Draw expanded dropdown if active - this should be drawn last to appear on top
        if self.expanded and self.options:
            # Create a new surface for the dropdown (for z-index control)
            dropdown_surface = pygame.Surface((self.dropdown_rect.width, self.dropdown_rect.height))
            dropdown_surface.fill(WHITE)  # Fill entire surface with white background
            
            # Calculate how many options to display
            visible_count = min(len(self.options) - self.scroll_offset, self.max_visible_options)
            
            # Draw each visible option on the dropdown surface
            for i in range(visible_count):
                actual_index = i + self.scroll_offset
                value, _ = self.options[actual_index]
                
                option_rect = pygame.Rect(
                    0,  # Relative to dropdown surface
                    i * self.option_height,
                    self.dropdown_rect.width,
                    self.option_height
                )
                
                # Highlight selected option with light gray
                if actual_index == self.selected_index:
                    # Fill with light gray but keep a white margin for clearer separation
                    highlight_rect = pygame.Rect(
                        option_rect.x + 2,
                        option_rect.y + 2,
                        option_rect.width - 4,
                        option_rect.height - 4
                    )
                    pygame.draw.rect(dropdown_surface, LIGHT_GRAY, highlight_rect)
                
                # Draw option text (truncated) - using title (value) instead of description
                truncated_text = self._truncate_text(value, font, option_rect.width - 10)
                text_surf = font.render(truncated_text, True, BLACK)
                text_rect = text_surf.get_rect(midleft=(option_rect.x + 5, option_rect.centery))
                dropdown_surface.blit(text_surf, text_rect)
                
                # Draw separator line between options
                if i < visible_count - 1:
                    pygame.draw.line(
                        dropdown_surface, 
                        DARK_GRAY, 
                        (option_rect.left, option_rect.bottom), 
                        (option_rect.right, option_rect.bottom), 
                        1
                    )
            
            # Draw scroll indicators if needed
            if len(self.options) > self.max_visible_options:
                if self.scroll_offset > 0:  # Can scroll up
                    pygame.draw.polygon(dropdown_surface, BLACK, [
                        (self.dropdown_rect.width - 15, 10),
                        (self.dropdown_rect.width - 5, 10),
                        (self.dropdown_rect.width - 10, 5)
                    ])
                
                if self.scroll_offset + self.max_visible_options < len(self.options):  # Can scroll down
                    pygame.draw.polygon(dropdown_surface, BLACK, [
                        (self.dropdown_rect.width - 15, self.dropdown_rect.height - 10),
                        (self.dropdown_rect.width - 5, self.dropdown_rect.height - 10),
                        (self.dropdown_rect.width - 10, self.dropdown_rect.height - 5)
                    ])
            
            # Draw border on the dropdown surface
            pygame.draw.rect(dropdown_surface, BLACK, 
                            pygame.Rect(0, 0, self.dropdown_rect.width, self.dropdown_rect.height), 1)
            
            # Blit the dropdown surface onto the main surface - this ensures it's drawn on top
            surface.blit(dropdown_surface, self.dropdown_rect.topleft) 