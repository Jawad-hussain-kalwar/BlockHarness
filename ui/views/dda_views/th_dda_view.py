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
from config.defaults import DEFAULT_WEIGHTS, HARDER_WEIGHTS, HARDEST_WEIGHTS


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
        
        # Convert defaults to string format
        default_weights_str = ",".join(str(w) for w in DEFAULT_WEIGHTS)
        
        # Initial weights input with default values
        initial_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.initial_weights_field = InputField(initial_field_rect, default_weights_str, 21)
        self.input_fields.append(self.initial_weights_field)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Threshold 1
        self.threshold1_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        
        # Threshold 1 score
        self.score1_label = (left_x, y)
        threshold1_score_rect = pygame.Rect(left_x, y + LABEL_SPACING + 5, field_width, FIELD_HEIGHT)
        self.threshold1_score_field = InputField(threshold1_score_rect, "1000", 5, numeric=True)
        self.input_fields.append(self.threshold1_score_field)
        
        # Threshold 1 weights (now below score)
        self.weights1_label = (left_x, y + FIELD_HEIGHT + FIELD_SPACING + 5)
        
        # Convert harder weights to string format
        harder_weights_str = ",".join(str(w) for w in HARDER_WEIGHTS)
        
        threshold1_weights_rect = pygame.Rect(left_x, y + FIELD_HEIGHT + FIELD_SPACING * 2 + 10, field_width, FIELD_HEIGHT)
        self.threshold1_weights_field = InputField(threshold1_weights_rect, harder_weights_str, 21)
        self.input_fields.append(self.threshold1_weights_field)
        y += FIELD_HEIGHT * 2 + FIELD_SPACING * 3 + 15
        
        # Threshold 2
        self.threshold2_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        
        # Threshold 2 score
        self.score2_label = (left_x, y)
        threshold2_score_rect = pygame.Rect(left_x, y + LABEL_SPACING + 5, field_width, FIELD_HEIGHT)
        self.threshold2_score_field = InputField(threshold2_score_rect, "3000", 5, numeric=True)
        self.input_fields.append(self.threshold2_score_field)
        
        # Threshold 2 weights (now below score)
        self.weights2_label = (left_x, y + FIELD_HEIGHT + FIELD_SPACING + 5)
        
        # Convert hardest weights to string format
        hardest_weights_str = ",".join(str(w) for w in HARDEST_WEIGHTS)
        
        threshold2_weights_rect = pygame.Rect(left_x, y + FIELD_HEIGHT + FIELD_SPACING * 2 + 10, field_width, FIELD_HEIGHT)
        self.threshold2_weights_field = InputField(threshold2_weights_rect, hardest_weights_str, 21)
        self.input_fields.append(self.threshold2_weights_field)

    def update_config_fields(self, config):
        """Update input fields from config."""
        # Get shape weights from config or use defaults
        shape_weights = config.get("shape_weights", DEFAULT_WEIGHTS)
        initial_weights = ",".join(map(str, shape_weights))
        self.initial_weights_field.value = initial_weights
        
        # Get difficulty thresholds from config or use defaults
        difficulty_thresholds = config.get("difficulty_thresholds", [
            (1000, HARDER_WEIGHTS),
            (3000, HARDEST_WEIGHTS)
        ])
        
        # Check if thresholds exist and have the right format
        if len(difficulty_thresholds) >= 2:
            # Update threshold 1
            threshold1_score = difficulty_thresholds[0][0]
            threshold1_weights = difficulty_thresholds[0][1]
            self.threshold1_score_field.value = str(threshold1_score)
            self.threshold1_weights_field.value = ",".join(map(str, threshold1_weights))
            
            # Update threshold 2
            threshold2_score = difficulty_thresholds[1][0]
            threshold2_weights = difficulty_thresholds[1][1]
            self.threshold2_score_field.value = str(threshold2_score)
            self.threshold2_weights_field.value = ",".join(map(str, threshold2_weights))

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
            if field.handle_event(event):
                return True
        return False

    def get_config_values(self):
        """Get the current configuration values from the ThresholdDDA view.
        
        Returns:
            Dict: Configuration parameters, or None if validation fails
        """
        try:
            # Parse initial weights
            initial_weights = [int(w.strip()) for w in self.initial_weights_field.value.split(",")]
            
            # Ensure we have the right number of values for shape weights
            if not initial_weights:
                initial_weights = DEFAULT_WEIGHTS.copy()
            elif len(initial_weights) < len(DEFAULT_WEIGHTS):
                initial_weights.extend([0] * (len(DEFAULT_WEIGHTS) - len(initial_weights)))
            
            # Parse threshold 1
            threshold1_score = int(self.threshold1_score_field.value)
            threshold1_weights = [int(w.strip()) for w in self.threshold1_weights_field.value.split(",")]
            
            # Ensure we have the right number of values for threshold1
            if not threshold1_weights:
                threshold1_weights = HARDER_WEIGHTS.copy()
            elif len(threshold1_weights) < len(DEFAULT_WEIGHTS):
                threshold1_weights.extend([0] * (len(DEFAULT_WEIGHTS) - len(threshold1_weights)))
            
            # Parse threshold 2
            threshold2_score = int(self.threshold2_score_field.value)
            threshold2_weights = [int(w.strip()) for w in self.threshold2_weights_field.value.split(",")]
            
            # Ensure we have the right number of values for threshold2
            if not threshold2_weights:
                threshold2_weights = HARDEST_WEIGHTS.copy()
            elif len(threshold2_weights) < len(DEFAULT_WEIGHTS):
                threshold2_weights.extend([0] * (len(DEFAULT_WEIGHTS) - len(threshold2_weights)))
            
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
            
        except ValueError as e:
            print(f"Invalid configuration values: {e}")
            return None 