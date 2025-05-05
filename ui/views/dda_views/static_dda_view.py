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


class StaticDDAView:
    """View for Static DDA Algorithm Controls."""
    
    def __init__(self, parent_rect, font, small_font):
        """Initialize the StaticDDAView.
        
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
        
        # Initial weights label
        self.initial_weights_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING + 4
        
        # Initial weights input with fixed value
        initial_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.initial_weights_field = InputField(initial_field_rect, "1,0,0,0,0,0,0,0,0,0,0", 21)
        self.input_fields.append(self.initial_weights_field)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Static DDA explanation
        self.explanation_label = (left_x, y)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Sample visualization
        self.visualization_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT * 3)
        
    def update_config_fields(self, config):
        """Update input fields from config."""
        # For static DDA, we always use equal weights (1,0,0,0,0,0,0,0,0,0,0)
        self.initial_weights_field.value = "1,0,0,0,0,0,0,0,0,0,0"
        
    def draw(self, surface):
        """Draw the StaticDDA view elements."""
        # Draw initial weights label
        label = self.font.render("Initial Shape Weights (Fixed):", True, TEXT_PRIMARY)
        surface.blit(label, self.initial_weights_label)
        
        # Draw explanation
        explanation = self.font.render("Static DDA does not adjust difficulty during gameplay.", True, TEXT_PRIMARY)
        surface.blit(explanation, self.explanation_label)
        
        # Draw sample visualization (simple bar chart showing equal distribution)
        pygame.draw.rect(surface, SECTION_BG, self.visualization_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, self.visualization_rect, width=1, border_radius=BORDER_RADIUS)
        
        # Draw equal bars inside visualization
        bar_width = (self.visualization_rect.width - 20) / 11
        bar_height = self.visualization_rect.height * 0.6
        
        for i in range(11):
            bar_rect = pygame.Rect(
                self.visualization_rect.x + 10 + i * bar_width,
                self.visualization_rect.y + self.visualization_rect.height - bar_height - 10,
                bar_width - 5,
                bar_height
            )
            pygame.draw.rect(surface, TEXT_PRIMARY, bar_rect)
            
            # Draw block number
            block_label = self.small_font.render(f"{i+1}", True, TEXT_SECONDARY)
            label_x = self.visualization_rect.x + 10 + i * bar_width + bar_width/2 - block_label.get_width()/2
            label_y = self.visualization_rect.y + self.visualization_rect.height - 5 - block_label.get_height()
            surface.blit(block_label, (label_x, label_y))
            
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface)
            
    def handle_event(self, event):
        """Handle events for the StaticDDA view.
        
        Note: We still process events but don't allow changing the values
        """
        pass
        
    def get_config_values(self):
        """Get the current configuration values from the StaticDDA view.
        
        Returns:
            Dict: Configuration parameters with static weights
        """
        # Always use fixed weights [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        weights = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Build configuration dictionary
        return {
            "shape_weights": weights,
            "difficulty_thresholds": [
                (100, weights.copy()),  # Add dummy thresholds to maintain compatibility
                (200, weights.copy()),  # with the existing config structure
            ],
            "dda_params": {
                "weights": weights
            }
        } 