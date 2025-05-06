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
from ui.debug import draw_debug_rect


class DDASection:
    def __init__(self, left_x, top_y, field_width, font, small_font):
        self.font = font
        self.small_font = small_font
        self.input_fields = []
        
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
        
        # DDA Description
        self.description_label = (left_x, y)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Low clear rate threshold
        self.low_clear_rate_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        low_clear_rate_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.low_clear_rate_field = InputField(low_clear_rate_rect, "0.50", 4)
        self.input_fields.append(self.low_clear_rate_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # High clear rate threshold
        self.high_clear_rate_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        high_clear_rate_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.high_clear_rate_field = InputField(high_clear_rate_rect, "0.80", 4)
        self.input_fields.append(self.high_clear_rate_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Number of best fit blocks
        self.n_best_fit_blocks_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        n_best_fit_blocks_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.n_best_fit_blocks_field = InputField(n_best_fit_blocks_rect, "1", 1)
        self.input_fields.append(self.n_best_fit_blocks_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Score threshold
        self.score_threshold_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        score_threshold_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.score_threshold_field = InputField(score_threshold_rect, "1000", 5)
        self.input_fields.append(self.score_threshold_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Number of game over blocks
        self.n_game_over_blocks_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        n_game_over_blocks_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.n_game_over_blocks_field = InputField(n_game_over_blocks_rect, "1", 1)
        self.input_fields.append(self.n_game_over_blocks_field)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Apply button
        self.apply_button_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT * 1.5)

    def update_config_fields(self, config):
        """Update input fields from config."""
        # Get DDA params from config
        dda_params = config.get("dda_params", {})
        dda_config = dda_params.get("dda", {})
        
        # If no specific DDA params, check metrics_flow for defaults
        metrics_flow = config.get("metrics_flow", {})
        
        # Update input fields with values from config or defaults
        self.low_clear_rate_field.value = str(dda_config.get("low_clear_rate", 0.50))
        self.high_clear_rate_field.value = str(dda_config.get("high_clear_rate", 0.80))
        self.n_best_fit_blocks_field.value = str(dda_config.get("n_best_fit_blocks", 1))
        self.score_threshold_field.value = str(dda_config.get("score_threshold", 1000))
        self.n_game_over_blocks_field.value = str(dda_config.get("n_game_over_blocks", 1))

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
        
        # Draw description
        description_text = self.font.render("Opportunity Adaptive DDA", True, TEXT_PRIMARY)
        surface.blit(description_text, self.description_label)
        
        # Draw labels
        low_clear_rate_label = self.font.render("Low Clear Rate Threshold:", True, TEXT_PRIMARY)
        surface.blit(low_clear_rate_label, self.low_clear_rate_label)
        
        high_clear_rate_label = self.font.render("High Clear Rate Threshold:", True, TEXT_PRIMARY)
        surface.blit(high_clear_rate_label, self.high_clear_rate_label)
        
        n_best_fit_blocks_label = self.font.render("Best Fit Blocks Count:", True, TEXT_PRIMARY)
        surface.blit(n_best_fit_blocks_label, self.n_best_fit_blocks_label)
        
        score_threshold_label = self.font.render("Score Threshold:", True, TEXT_PRIMARY)
        surface.blit(score_threshold_label, self.score_threshold_label)
        
        n_game_over_blocks_label = self.font.render("Game Over Blocks Count:", True, TEXT_PRIMARY)
        surface.blit(n_game_over_blocks_label, self.n_game_over_blocks_label)
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface)
        
        # Draw apply button
        pygame.draw.rect(surface, BUTTON_PRIMARY_BG, self.apply_button_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, BUTTON_BORDER, self.apply_button_rect, width=1, border_radius=BORDER_RADIUS)
        apply_text = self.font.render("Apply Changes", True, TEXT_PRIMARY)
        text_x = self.apply_button_rect.x + self.apply_button_rect.width // 2 - apply_text.get_width() // 2
        text_y = self.apply_button_rect.y + self.apply_button_rect.height // 2 - apply_text.get_height() // 2
        surface.blit(apply_text, (text_x, text_y))

    def handle_event(self, event):
        """Handle events for the DDA section.
        
        Returns:
            String: "apply" if apply button was clicked, None otherwise
        """
        # Handle input field events
        for field in self.input_fields:
            field.handle_event(event)
        
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
            # Parse clear rate threshold values
            low_clear_rate = float(self.low_clear_rate_field.value)
            high_clear_rate = float(self.high_clear_rate_field.value)
            
            # Parse integer values
            n_best_fit_blocks = int(self.n_best_fit_blocks_field.value)
            score_threshold = int(self.score_threshold_field.value)
            n_game_over_blocks = int(self.n_game_over_blocks_field.value)
            
            # Validate thresholds
            if not (0 < low_clear_rate < high_clear_rate < 1):
                print("[ui/views/dda_section.py][148] Thresholds must satisfy: 0 < low_clear_rate < high_clear_rate < 1")
                return None
            
            # Validate counts
            if n_best_fit_blocks < 0 or n_best_fit_blocks > 3:
                print("[ui/views/dda_section.py][152] Best fit blocks count must be between 0 and 3")
                return None
                
            if n_game_over_blocks < 0 or n_game_over_blocks > 3:
                print("[ui/views/dda_section.py][156] Game over blocks count must be between 0 and 3")
                return None
            
            # Validate score threshold
            if score_threshold < 0:
                print("[ui/views/dda_section.py][160] Score threshold must be positive")
                return None
            
            # Return combined configuration
            return {
                "dda_params": {
                    "dda": {
                        "low_clear_rate": low_clear_rate,
                        "high_clear_rate": high_clear_rate,
                        "n_best_fit_blocks": n_best_fit_blocks,
                        "score_threshold": score_threshold,
                        "n_game_over_blocks": n_game_over_blocks
                    }
                }
            }
            
        except (ValueError, IndexError) as e:
            print(f"[ui/views/dda_section.py][175] Invalid configuration values: {e}")
            return None 