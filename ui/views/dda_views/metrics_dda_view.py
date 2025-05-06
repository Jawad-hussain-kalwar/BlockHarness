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


class MetricsDDAView(TemplateDDAView):
    """Configuration view for the Metrics-based DDA algorithm."""
    
    def __init__(self, parent_rect, font, small_font):
        """Initialize the metrics DDA view with UI elements.
        
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
        
        # Initial difficulty level
        self.init_difficulty_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        init_difficulty_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.init_difficulty_field = InputField(init_difficulty_rect, "3", 2)
        self.input_fields.append(self.init_difficulty_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Low clear rate threshold
        self.low_clear_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        low_clear_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.low_clear_field = InputField(low_clear_rect, "0.30", 4)
        self.input_fields.append(self.low_clear_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # High clear rate threshold
        self.high_clear_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        high_clear_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.high_clear_field = InputField(high_clear_rect, "0.70", 4)
        self.input_fields.append(self.high_clear_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Danger score threshold
        self.danger_cut_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        danger_cut_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.danger_cut_field = InputField(danger_cut_rect, "0.80", 4)
        self.input_fields.append(self.danger_cut_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Rescue shape weights - first two values (other values are 0)
        self.rescue_weights_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        rescue_weights_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.rescue_weights_field = InputField(rescue_weights_rect, "10,8", 10)
        self.input_fields.append(self.rescue_weights_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Size caps - concise representation
        self.size_caps_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        size_caps_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.size_caps_field = InputField(size_caps_rect, "3,3,3,4,4,4,5,5,5,5", 25)
        self.input_fields.append(self.size_caps_field)
    
    def update_config_fields(self, config: Dict) -> None:
        """Update input fields from config.
        
        Args:
            config: Configuration dictionary
        """
        # Get metrics DDA params from config
        dda_params = config.get("dda_params", {})
        metrics_params = dda_params.get("metrics_dda", {})
        
        # If no specific metrics_dda params, check metrics_flow for defaults
        metrics_flow = config.get("metrics_flow", {})
        
        # Update input fields with values from config or defaults
        self.init_difficulty_field.value = str(metrics_params.get("initial_difficulty", 3))
        self.low_clear_field.value = str(metrics_params.get("low_clear", metrics_flow.get("low_clear", 0.30)))
        self.high_clear_field.value = str(metrics_params.get("high_clear", metrics_flow.get("high_clear", 0.70)))
        self.danger_cut_field.value = str(metrics_params.get("danger_cut", metrics_flow.get("danger_cut", 0.80)))
        
        # Update rescue weights (first two values, rest are 0)
        rescue_weights = metrics_params.get("rescue_shape_weights", [10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.rescue_weights_field.value = f"{rescue_weights[0]},{rescue_weights[1]}"
        
        # Update size caps
        size_caps = metrics_params.get("size_caps", [3, 3, 3, 4, 4, 4, 5, 5, 5, 5])
        self.size_caps_field.value = ",".join(str(cap) for cap in size_caps)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the metrics DDA view elements.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw description
        description_text = self.font.render("Metrics-Based Adaptive DDA", True, TEXT_PRIMARY)
        surface.blit(description_text, self.description_label)
        
        # Draw labels
        difficulty_label = self.font.render("Initial Difficulty (1-10):", True, TEXT_PRIMARY)
        surface.blit(difficulty_label, self.init_difficulty_label)
        
        low_clear_label = self.font.render("Low Clear Rate Threshold:", True, TEXT_PRIMARY)
        surface.blit(low_clear_label, self.low_clear_label)
        
        high_clear_label = self.font.render("High Clear Rate Threshold:", True, TEXT_PRIMARY)
        surface.blit(high_clear_label, self.high_clear_label)
        
        danger_cut_label = self.font.render("Danger Score Threshold:", True, TEXT_PRIMARY)
        surface.blit(danger_cut_label, self.danger_cut_label)
        
        rescue_weights_label = self.font.render("Rescue Shape Weights (1x1,1x2):", True, TEXT_PRIMARY)
        surface.blit(rescue_weights_label, self.rescue_weights_label)
        
        size_caps_label = self.font.render("Size Caps Per Difficulty Level:", True, TEXT_PRIMARY)
        surface.blit(size_caps_label, self.size_caps_label)
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface)
    
    def get_config_values(self) -> Optional[Dict]:
        """Get the current configuration values from the metrics DDA view.
        
        Returns:
            Dict: Configuration parameters, or None if validation fails
        """
        try:
            # Parse initial difficulty
            initial_difficulty = int(self.init_difficulty_field.value)
            if not (1 <= initial_difficulty <= 10):
                print("[ui/views/dda_views/metrics_dda_view.py][158] Initial difficulty must be between 1 and 10")
                return None
            
            # Parse threshold values
            low_clear = float(self.low_clear_field.value)
            high_clear = float(self.high_clear_field.value)
            danger_cut = float(self.danger_cut_field.value)
            
            # Validate thresholds
            if not (0 < low_clear < high_clear < 1):
                print("[ui/views/dda_views/metrics_dda_view.py][160] Thresholds must satisfy: 0 < low_clear < high_clear < 1")
                return None
            
            if not (0 < danger_cut < 1):
                print("[ui/views/dda_views/metrics_dda_view.py][162] Danger threshold must be between 0 and 1")
                return None
            
            # Parse rescue weights (format: "w1,w2")
            rescue_weight_parts = self.rescue_weights_field.value.split(",")
            if len(rescue_weight_parts) != 2:
                print("[ui/views/dda_views/metrics_dda_view.py][164] Rescue weights must be two comma-separated values")
                return None
                
            w1 = int(rescue_weight_parts[0])
            w2 = int(rescue_weight_parts[1])
            rescue_shape_weights = [w1, w2] + [0] * 9  # Zero weights for remaining shapes
            
            # Parse size caps (format: "c1,c2,c3,c4,c5,c6,c7,c8,c9,c10")
            size_cap_parts = self.size_caps_field.value.split(",")
            if len(size_cap_parts) != 10:
                print("[ui/views/dda_views/metrics_dda_view.py][166] Size caps must have 10 comma-separated values")
                return None
                
            size_caps = [int(cap) for cap in size_cap_parts]
            if not all(1 <= cap <= 10 for cap in size_caps):
                print("[ui/views/dda_views/metrics_dda_view.py][168] Size caps must be between 1 and 10")
                return None
            
            # Return combined configuration
            return {
                "dda_params": {
                    "metrics_dda": {
                        "initial_difficulty": initial_difficulty,
                        "low_clear": low_clear,
                        "high_clear": high_clear,
                        "danger_cut": danger_cut,
                        "rescue_shape_weights": rescue_shape_weights,
                        "size_caps": size_caps
                    }
                }
            }
            
        except (ValueError, IndexError) as e:
            print(f"[ui/views/dda_views/metrics_dda_view.py][170] Invalid configuration values: {e}")
            return None 