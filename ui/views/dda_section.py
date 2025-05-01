import pygame
from ui.colours import (
    TEXT_PRIMARY, TEXT_SECONDARY,
    BUTTON_PRIMARY_BG, TEXT_PRIMARY,
    BUTTON_BORDER,
    SECTION_BG, SECTION_BORDER
)
from ui.layout import (
    PADDING, DDA_WIDTH, SECTION_HEIGHT,
    FIELD_HEIGHT, FIELD_SPACING,
    LABEL_SPACING, BORDER_RADIUS
)
from ui.input_field import InputField
from ui.dropdown_menu import DropdownMenu
from ui.debug import draw_debug_rect


class DDASection:
    def __init__(self, left_x, top_y, field_width, font, small_font):
        self.font = font
        self.small_font = small_font
        self.input_fields = []
        self.dropdown_menus = []
        
        # Initialize section rectangle with new layout constants
        self.rect = pygame.Rect(
            PADDING,
            PADDING,
            DDA_WIDTH,
            SECTION_HEIGHT
        )
        
        # Use self.rect for positioning instead of passed parameters
        left_x = self.rect.x + PADDING
        top_y = self.rect.y + PADDING
        field_width = DDA_WIDTH - 2 * PADDING
        
        # Initialize positions and UI elements
        y = top_y
        
        # DDA section title
        self.dda_section_title = (left_x, y)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # DDA Algorithm dropdown
        self.dda_algorithm_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        dda_algorithm_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.dda_algorithm_dropdown = DropdownMenu(dda_algorithm_rect, [])
        self.dropdown_menus.append(self.dda_algorithm_dropdown)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Initial weights label
        self.initial_weights_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING + 4
        
        # Initial weights input
        initial_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.initial_weights_field = InputField(initial_field_rect, "", 20)
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
        self.threshold1_weights_field = InputField(threshold1_weights_rect, "", 20)
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
        self.threshold2_weights_field = InputField(threshold2_weights_rect, "", 20)
        self.input_fields.append(self.threshold2_weights_field)
        y += FIELD_HEIGHT * 2 + FIELD_SPACING * 3 + 15
        
        # Apply button
        self.apply_button_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT * 1.5)

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
        
        # Set default DDA algorithm if available
        if self.dda_algorithm_dropdown.options:
            dda_algorithm = config.get("dda_algorithm", "ThresholdDDA")
            for i, (value, _) in enumerate(self.dda_algorithm_dropdown.options):
                if value == dda_algorithm:
                    self.dda_algorithm_dropdown.selected_index = i
                    break

    def update_dda_algorithm_dropdown(self, dda_algorithms):
        """Update the DDA algorithm dropdown with available algorithms.
        
        Args:
            dda_algorithms: List of (name, description) tuples for available DDA algorithms
        """
        self.dda_algorithm_dropdown.options = dda_algorithms
        
        # Reset selected index to 0 if needed
        if not self.dda_algorithm_dropdown.options:
            self.dda_algorithm_dropdown.selected_index = 0

    def draw(self, surface):
        """Draw the DDA section elements."""
        # Draw section panel background and border
        pygame.draw.rect(surface, SECTION_BG, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, self.rect, width=1, border_radius=BORDER_RADIUS)
        # Draw debug border if enabled
        draw_debug_rect(surface, self.rect, "dda")
        
        # Draw DDA section title
        dda_title = self.font.render("Dynamic Difficulty Adjustment", True, TEXT_PRIMARY)
        surface.blit(dda_title, self.dda_section_title)
        
        # Draw DDA algorithm label
        label = self.font.render("DDA Algorithm:", True, TEXT_PRIMARY)
        surface.blit(label, self.dda_algorithm_label)
        
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
        
        # Draw apply button
        pygame.draw.rect(surface, BUTTON_PRIMARY_BG, self.apply_button_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, BUTTON_BORDER, self.apply_button_rect, width=1, border_radius=BORDER_RADIUS)
        apply_text = self.font.render("Apply Changes", True, TEXT_PRIMARY)
        text_x = self.apply_button_rect.x + self.apply_button_rect.width // 2 - apply_text.get_width() // 2
        text_y = self.apply_button_rect.y + self.apply_button_rect.height // 2 - apply_text.get_height() // 2
        surface.blit(apply_text, (text_x, text_y))
        
        # Draw input fields and dropdowns
        for field in self.input_fields:
            field.draw(surface)
        
        for dropdown in self.dropdown_menus:
            dropdown.draw(surface)

    def handle_event(self, event):
        """Handle events for the DDA section.
        
        Returns:
            String: "apply" if apply button was clicked, None otherwise
        """
        # Handle input field events
        for field in self.input_fields:
            field.handle_event(event)
        
        # Handle dropdown events
        for dropdown in self.dropdown_menus:
            dropdown.handle_event(event)
        
        # Check for button clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Apply button
            if self.apply_button_rect.collidepoint(mouse_pos):
                return "apply"
        
        # No DDA section action taken
        return None

    def get_config_values(self):
        """Get the current configuration values from the DDA section.
        
        Returns:
            Dict: Configuration parameters, or None if validation fails
        """
        try:
            # Parse initial weights
            initial_weights = list(map(int, self.initial_weights_field.value.split(",")))
            if len(initial_weights) != 11:
                print("Initial weights must have 8 values")
                return None
            
            # Parse threshold 1
            threshold1_score = int(self.threshold1_score_field.value)
            threshold1_weights = list(map(int, self.threshold1_weights_field.value.split(",")))
            if len(threshold1_weights) != 8:
                print("Threshold 1 weights must have 8 values")
                return None
            
            # Parse threshold 2
            threshold2_score = int(self.threshold2_score_field.value)
            threshold2_weights = list(map(int, self.threshold2_weights_field.value.split(",")))
            if len(threshold2_weights) != 8:
                print("Threshold 2 weights must have 8 values")
                return None
            
            # Get selected DDA algorithm
            dda_algorithm = None
            if self.dda_algorithm_dropdown.options:
                dda_algorithm = self.dda_algorithm_dropdown.get_selected_value()
            
            # Build configuration dictionary
            return {
                "shape_weights": initial_weights,
                "difficulty_thresholds": [
                    (threshold1_score, threshold1_weights),
                    (threshold2_score, threshold2_weights),
                ],
                "dda_algorithm": dda_algorithm or "ThresholdDDA",
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
    
    def get_selected_dda_algorithm(self):
        """Get the selected DDA algorithm from the dropdown.
        
        Returns:
            String: The selected DDA algorithm name, or None if no selection
        """
        if self.dda_algorithm_dropdown.options:
            return self.dda_algorithm_dropdown.get_selected_value()
        return None 