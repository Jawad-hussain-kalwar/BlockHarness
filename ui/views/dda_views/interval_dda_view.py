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


class IntervalDDAView:
    """View for Interval-Based DDA Algorithm Controls."""
    
    def __init__(self, parent_rect, font, small_font):
        """Initialize the IntervalDDAView.
        
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
        
        # Rescue blocks configuration
        self.rescue_section_label = (left_x, y)
        y += FIELD_HEIGHT
        
        # Steps to Rescue
        self.steps_to_rescue_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        steps_rescue_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.steps_to_rescue_field = InputField(steps_rescue_field_rect, "2", 2)
        self.input_fields.append(self.steps_to_rescue_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Number of Rescue Blocks
        self.rescue_blocks_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        rescue_blocks_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.rescue_blocks_field = InputField(rescue_blocks_field_rect, "1", 1)
        self.input_fields.append(self.rescue_blocks_field)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Awkward blocks configuration
        self.awkward_section_label = (left_x, y)
        y += FIELD_HEIGHT
        
        # Steps to Awkward
        self.steps_to_awkward_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        steps_awkward_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.steps_to_awkward_field = InputField(steps_awkward_field_rect, "2", 2)
        self.input_fields.append(self.steps_to_awkward_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Number of Awkward Blocks
        self.awkward_blocks_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        awkward_blocks_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.awkward_blocks_field = InputField(awkward_blocks_field_rect, "1", 1)
        self.input_fields.append(self.awkward_blocks_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Interval DDA explanation
        self.explanation_label = (left_x, y)
        
    def update_config_fields(self, config):
        """Update input fields from config."""
        # Get DDA parameters from config
        dda_params = config.get("dda_params", {})
        
        # Update field values with defaults if not present
        self.steps_to_rescue_field.value = str(dda_params.get("steps_to_rescue", 2))
        self.rescue_blocks_field.value = str(dda_params.get("rescue_block_count", 1))
        self.steps_to_awkward_field.value = str(dda_params.get("steps_to_awkward", 2))
        self.awkward_blocks_field.value = str(dda_params.get("awkward_block_count", 1))
        
    def draw(self, surface):
        """Draw the IntervalDDA view elements."""
        # Draw rescue section label
        rescue_label = self.font.render("Rescue Blocks Configuration", True, TEXT_PRIMARY)
        surface.blit(rescue_label, self.rescue_section_label)
        
        # Draw steps to rescue label
        label = self.font.render("Steps to Rescue:", True, TEXT_PRIMARY)
        surface.blit(label, self.steps_to_rescue_label)
        
        # Draw rescue block count label
        label = self.font.render("Number of Rescue Blocks (max 3):", True, TEXT_PRIMARY)
        surface.blit(label, self.rescue_blocks_label)
        
        # Draw awkward section label
        awkward_label = self.font.render("Awkward Blocks Configuration", True, TEXT_PRIMARY)
        surface.blit(awkward_label, self.awkward_section_label)
        
        # Draw steps to awkward label
        label = self.font.render("Steps to Awkward:", True, TEXT_PRIMARY)
        surface.blit(label, self.steps_to_awkward_label)
        
        # Draw awkward block count label
        label = self.font.render("Number of Awkward Blocks (max 3):", True, TEXT_PRIMARY)
        surface.blit(label, self.awkward_blocks_label)
        
        # Draw explanation
        explanation = self.small_font.render("Interval DDA spawns specific blocks at regular tray intervals", True, TEXT_SECONDARY)
        surface.blit(explanation, self.explanation_label)
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface)
            
    def handle_event(self, event):
        """Handle events for the IntervalDDA view."""
        # Handle input field events
        for field in self.input_fields:
            field.handle_event(event)
        
    def get_config_values(self):
        """Get the current configuration values from the IntervalDDA view.
        
        Returns:
            Dict: Configuration parameters, or None if validation fails
        """
        try:
            # Parse and validate input field values
            steps_to_rescue = int(self.steps_to_rescue_field.value)
            rescue_block_count = int(self.rescue_blocks_field.value)
            steps_to_awkward = int(self.steps_to_awkward_field.value)
            awkward_block_count = int(self.awkward_blocks_field.value)
            
            # Validate ranges
            if steps_to_rescue < 1:
                print("Steps to Rescue must be at least 1")
                return None
                
            if rescue_block_count < 1 or rescue_block_count > 3:
                print("Number of Rescue Blocks must be between 1 and 3")
                return None
                
            if steps_to_awkward < 1:
                print("Steps to Awkward must be at least 1")
                return None
                
            if awkward_block_count < 1 or awkward_block_count > 3:
                print("Number of Awkward Blocks must be between 1 and 3")
                return None
            
            # Build configuration dictionary
            return {
                "dda_params": {
                    "steps_to_rescue": steps_to_rescue,
                    "rescue_block_count": rescue_block_count,
                    "steps_to_awkward": steps_to_awkward,
                    "awkward_block_count": awkward_block_count
                }
            }
        except ValueError as e:
            print(f"Invalid configuration values: {e}")
            return None 