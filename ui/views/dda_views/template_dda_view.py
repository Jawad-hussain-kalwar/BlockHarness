import pygame
from ui.colours import (
    TEXT_PRIMARY, TEXT_SECONDARY,
    SECTION_BG, SECTION_BORDER
)
from ui.layout import (
    PADDING, FIELD_HEIGHT, FIELD_SPACING,
    LABEL_SPACING, BORDER_RADIUS
)
from ui.input_field import InputField
from ui.debug import draw_debug_rect


class TemplateDDAView:
    """Template for new DDA Algorithm View implementations.
    
    To create a new DDA view:
    1. Copy this file and rename it to match your DDA algorithm (e.g., my_dda_view.py)
    2. Rename this class to match your DDA algorithm (e.g., MyDDAView)
    3. Implement the required methods below
    4. Import your new view in __init__.py
    5. Update the _update_active_dda_view method in dda_section.py
    """
    
    def __init__(self, parent_rect, font, small_font):
        """Initialize the DDA view.
        
        Args:
            parent_rect: Rect of the parent section
            font: Font for main labels
            small_font: Font for smaller labels
        """
        self.font = font
        self.small_font = small_font
        self.input_fields = []
        
        # Calculate positioning based on parent rectangle
        self.rect = parent_rect.copy()
        left_x = self.rect.x + PADDING
        top_y = self.rect.y + PADDING
        field_width = self.rect.width - 2 * PADDING
        
        # Initialize positions and UI elements
        y = top_y
        
        # Add your UI elements here
        # Example:
        # self.some_label = (left_x, y)
        # y += FIELD_HEIGHT - FIELD_SPACING
        # some_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        # self.some_field = InputField(some_field_rect, "", 20)
        # self.input_fields.append(self.some_field)
        
    def update_config_fields(self, config):
        """Update input fields from config.
        
        Args:
            config: The configuration dictionary
        """
        # Update your input fields based on the config
        # Example:
        # self.some_field.value = str(config.get("some_value", ""))
        pass
        
    def draw(self, surface):
        """Draw the DDA view elements.
        
        Args:
            surface: The pygame surface to draw on
        """
        # Draw your UI elements
        # Example:
        # label = self.font.render("Some Label:", True, TEXT_PRIMARY)
        # surface.blit(label, self.some_label)
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface)
            
    def handle_event(self, event):
        """Handle events for the DDA view.
        
        Args:
            event: The pygame event to handle
        """
        # Handle your input field events
        for field in self.input_fields:
            field.handle_event(event)
        
    def get_config_values(self):
        """Get the current configuration values from the DDA view.
        
        Returns:
            Dict: Configuration parameters, or None if validation fails
        """
        # Return a configuration dictionary based on your input fields
        # Example:
        # try:
        #     some_value = int(self.some_field.value)
        #     return {
        #         "some_value": some_value,
        #         # Add other values specific to your DDA algorithm
        #     }
        # except (ValueError, IndexError) as e:
        #     print(f"Invalid configuration values: {e}")
        #     return None
        return {} 