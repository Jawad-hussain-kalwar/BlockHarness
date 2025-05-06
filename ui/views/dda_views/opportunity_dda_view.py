import pygame
from typing import Dict, Optional
from ui.colours import (
    TEXT_PRIMARY, TEXT_SECONDARY,
    SECTION_BG, SECTION_BORDER,
    INPUT_BG, INPUT_BORDER
)
from ui.layout import (
    PADDING, FIELD_HEIGHT, FIELD_SPACING,
    LABEL_SPACING, BORDER_RADIUS
)
from ui.input_field import InputField
from ui.views.dda_views.template_dda_view import TemplateDDAView


class OpportunityDDAView(TemplateDDAView):
    """Configuration view for the Opportunity-based DDA algorithm."""
    
    def __init__(self, parent_rect, font, small_font):
        """Initialize the opportunity DDA view with UI elements.
        
        Args:
            parent_rect: Rect of the parent section
            font: Font for main labels
            small_font: Font for smaller labels
        """
        super().__init__(parent_rect, font, small_font)
        
        # Calculate positioning based on parent rectangle
        left_x = self.rect.x + PADDING
        top_y = self.rect.y + PADDING
        field_width = self.rect.width - 2 * PADDING
        
        # Initialize positions and UI elements
        y = top_y
        
        # Description
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
    
    def update_config_fields(self, config: Dict) -> None:
        """Update input fields from config.
        
        Args:
            config: Configuration dictionary
        """
        # Get opportunity DDA params from config
        dda_params = config.get("dda_params", {})
        opportunity_params = dda_params.get("opportunity_dda", {})
        
        # If no specific opportunity_dda params, check metrics_flow for defaults
        metrics_flow = config.get("metrics_flow", {})
        
        # Update input fields with values from config or defaults
        self.low_clear_rate_field.value = str(opportunity_params.get("low_clear_rate", 0.50))
        self.high_clear_rate_field.value = str(opportunity_params.get("high_clear_rate", 0.80))
        self.n_best_fit_blocks_field.value = str(opportunity_params.get("n_best_fit_blocks", 1))
        self.score_threshold_field.value = str(opportunity_params.get("score_threshold", 1000))
        self.n_game_over_blocks_field.value = str(opportunity_params.get("n_game_over_blocks", 1))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the opportunity DDA view elements.
        
        Args:
            surface: Pygame surface to draw on
        """
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
    
    def get_config_values(self) -> Optional[Dict]:
        """Get the current configuration values from the opportunity DDA view.
        
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
                print("Thresholds must satisfy: 0 < low_clear_rate < high_clear_rate < 1")
                return None
            
            # Validate counts
            if n_best_fit_blocks < 0 or n_best_fit_blocks > 3:
                print("Best fit blocks count must be between 0 and 3")
                return None
                
            if n_game_over_blocks < 0 or n_game_over_blocks > 3:
                print("Game over blocks count must be between 0 and 3")
                return None
            
            # Validate score threshold
            if score_threshold < 0:
                print("Score threshold must be positive")
                return None
            
            # Return combined configuration
            return {
                "dda_params": {
                    "opportunity_dda": {
                        "low_clear_rate": low_clear_rate,
                        "high_clear_rate": high_clear_rate,
                        "n_best_fit_blocks": n_best_fit_blocks,
                        "score_threshold": score_threshold,
                        "n_game_over_blocks": n_game_over_blocks
                    }
                }
            }
            
        except (ValueError, IndexError) as e:
            print(f"Invalid configuration values: {e}")
            return None 