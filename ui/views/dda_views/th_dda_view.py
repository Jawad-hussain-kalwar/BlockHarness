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


class ThresholdDDAView:
    """View for Threshold DDA Algorithm Controls."""
    
    def __init__(self, parent_rect, font, small_font):
        """Initialize the ThresholdDDAView.
        
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
        
        # Initial weights input
        initial_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.initial_weights_field = InputField(initial_field_rect, "", 21)
        self.input_fields.append(self.initial_weights_field)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Threshold 1
        self.threshold1_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        
        # Threshold 1 score
        self.score1_label = (left_x, y)
        threshold1_score_rect = pygame.Rect(left_x, y + LABEL_SPACING + 5, field_width, FIELD_HEIGHT)
        self.threshold1_score_field = InputField(threshold1_score_rect, "", 5, numeric=True)
        self.input_fields.append(self.threshold1_score_field)
        
        # Threshold 1 weights (now below score)
        self.weights1_label = (left_x, y + FIELD_HEIGHT + FIELD_SPACING + 5)
        threshold1_weights_rect = pygame.Rect(left_x, y + FIELD_HEIGHT + FIELD_SPACING * 2 + 10, field_width, FIELD_HEIGHT)
        self.threshold1_weights_field = InputField(threshold1_weights_rect, "", 21)
        self.input_fields.append(self.threshold1_weights_field)
        y += FIELD_HEIGHT * 2 + FIELD_SPACING * 3 + 15
        
        # Threshold 2
        self.threshold2_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        
        # Threshold 2 score
        self.score2_label = (left_x, y)
        threshold2_score_rect = pygame.Rect(left_x, y + LABEL_SPACING + 5, field_width, FIELD_HEIGHT)
        self.threshold2_score_field = InputField(threshold2_score_rect, "", 5, numeric=True)
        self.input_fields.append(self.threshold2_score_field)
        
        # Threshold 2 weights (now below score)
        self.weights2_label = (left_x, y + FIELD_HEIGHT + FIELD_SPACING + 5)
        threshold2_weights_rect = pygame.Rect(left_x, y + FIELD_HEIGHT + FIELD_SPACING * 2 + 10, field_width, FIELD_HEIGHT)
        self.threshold2_weights_field = InputField(threshold2_weights_rect, "", 21)
        self.input_fields.append(self.threshold2_weights_field)

    def update_config_fields(self, config):
        """Update input fields from config."""
        initial_weights = ",".join(map(str, config["shape_weights"]))
        self.initial_weights_field.value = initial_weights
        
        threshold1_score = config["difficulty_thresholds"][0][0]
        threshold1_weights = ",".join(map(str, config["difficulty_thresholds"][0][1]))
        self.threshold1_score_field.value = str(threshold1_score)
        self.threshold1_weights_field.value = threshold1_weights
        
        threshold2_score = config["difficulty_thresholds"][1][0]
        threshold2_weights = ",".join(map(str, config["difficulty_thresholds"][1][1]))
        self.threshold2_score_field.value = str(threshold2_score)
        self.threshold2_weights_field.value = threshold2_weights

    def draw(self, surface):
        """Draw the ThresholdDDA view elements."""
        # Draw initial weights label
        label = self.font.render("Initial Shape Weights (0-10):", True, TEXT_PRIMARY)
        surface.blit(label, self.initial_weights_label)
        
        # Draw threshold 1 label
        label = self.font.render("Difficulty Threshold 1:", True, TEXT_PRIMARY)
        surface.blit(label, self.threshold1_label)
        
        # Draw score/weights labels for threshold 1
        score_label = self.small_font.render("Score", True, TEXT_SECONDARY)
        surface.blit(score_label, self.score1_label)
        
        weights_label = self.small_font.render("Weights", True, TEXT_SECONDARY)
        surface.blit(weights_label, self.weights1_label)
        
        # Draw threshold 2 label
        label = self.font.render("Difficulty Threshold 2:", True, TEXT_PRIMARY)
        surface.blit(label, self.threshold2_label)
        
        # Draw score/weights labels for threshold 2
        score_label = self.small_font.render("Score", True, TEXT_SECONDARY)
        surface.blit(score_label, self.score2_label)
        
        weights_label = self.small_font.render("Weights", True, TEXT_SECONDARY)
        surface.blit(weights_label, self.weights2_label)
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface)

    def handle_event(self, event):
        """Handle events for the ThresholdDDA view."""
        # Handle input field events
        for field in self.input_fields:
            field.handle_event(event)

    def get_config_values(self):
        """Get the current configuration values from the ThresholdDDA view.
        
        Returns:
            Dict: Configuration parameters, or None if validation fails
        """
        try:
            # Parse initial weights
            initial_weights = list(map(int, self.initial_weights_field.value.split(",")))
            if len(initial_weights) != 11:
                print("Initial weights must have 11 values")
                return None
            
            # Parse threshold 1
            threshold1_score = int(self.threshold1_score_field.value)
            threshold1_weights = list(map(int, self.threshold1_weights_field.value.split(",")))
            if len(threshold1_weights) != 11:
                print("Threshold 1 weights must have 11 values")
                return None
            
            # Parse threshold 2
            threshold2_score = int(self.threshold2_score_field.value)
            threshold2_weights = list(map(int, self.threshold2_weights_field.value.split(",")))
            if len(threshold2_weights) != 11:
                print("Threshold 2 weights must have 11 values")
                return None
            
            # Build configuration dictionary
            return {
                "shape_weights": initial_weights,
                "difficulty_thresholds": [
                    (threshold1_score, threshold1_weights),
                    (threshold2_score, threshold2_weights),
                ],
                "dda_params": {
                    "thresholds": [
                        (threshold1_score, threshold1_weights),
                        (threshold2_score, threshold2_weights),
                    ]
                }
            }
            
        except (ValueError, IndexError) as e:
            print(f"Invalid configuration values: {e}")
            return None 