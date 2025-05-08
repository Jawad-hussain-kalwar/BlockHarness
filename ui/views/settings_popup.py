import pygame
from ui.colours import BG_COLOR, FG_COLOR, INPUT_BG, INPUT_BORDER, INPUT_FOCUS, GREEN
from ui.input_field import InputField
from ui.layout import BORDER_RADIUS, WINDOW_WIDTH, WINDOW_HEIGHT

class SettingsPopup:
    """Minimal popup for adjusting DDA parameters."""
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        # Center popup in fixed window
        width, height = 350, 250
        win_w, win_h = WINDOW_WIDTH, WINDOW_HEIGHT
        x = (win_w - width) // 2
        y = (win_h - height) // 2
        self.rect = pygame.Rect(x, y, width, height)
        # Title
        self.title = "DDA Settings"
        
        # Define input fields using proper InputField component
        field_h = 30
        field_w = 120
        
        # Create label positions
        label_x1 = x + 25
        label_x2 = x + width - field_w - 25
        field_y1 = y + 65
        field_y2 = y + 125
        
        # Create actual InputField objects
        self.input_fields = {
            "low_rate": InputField(
                pygame.Rect(label_x1, field_y1, field_w, field_h), 
                "0.5", 
                numeric=True
            ),
            "high_rate": InputField(
                pygame.Rect(label_x2, field_y1, field_w, field_h), 
                "0.8", 
                numeric=True
            ),
            "threshold": InputField(
                pygame.Rect(label_x1, field_y2, field_w, field_h), 
                "99999", 
                numeric=True
            ),
            "block_count": InputField(
                pygame.Rect(label_x2, field_y2, field_w, field_h), 
                "1", 
                numeric=True
            )
        }
        
        # Labels for fields
        self.labels = {
            "low_rate": "Low Clear Rate",
            "high_rate": "High Clear Rate",
            "threshold": "Score Threshold",
            "block_count": "Block Count"
        }
        
        # Create buttons
        button_y = y + height - 50
        button_width = 120
        button_height = 35
        
        # Apply button
        self.apply_button = pygame.Rect(
            x + 30, 
            button_y, 
            button_width, 
            button_height
        )
        
        # Cancel button
        self.cancel_button = pygame.Rect(
            x + width - button_width - 30, 
            button_y, 
            button_width, 
            button_height
        )
        
        # Hover state
        self.button_hover = {
            "apply": False,
            "cancel": False
        }

    def render(self, surface):
        # render popup background with rounded corners
        pygame.draw.rect(surface, BG_COLOR, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, FG_COLOR, self.rect, 2, border_radius=BORDER_RADIUS)
        
        # render title
        title_surf = self.font.render(self.title, True, FG_COLOR)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 30))
        surface.blit(title_surf, title_rect)
        
        # render fields and labels
        for key, field in self.input_fields.items():
            # render label
            label_surf = self.small_font.render(self.labels[key], True, FG_COLOR)
            surface.blit(label_surf, (field.rect.x, field.rect.y - 25))
            
            # render input field
            field.render(surface, self.small_font)
        
        # render buttons
        # Apply button (green)
        button_color = GREEN if self.button_hover["apply"] else (0, 150, 0)
        pygame.draw.rect(surface, button_color, self.apply_button, border_radius=BORDER_RADIUS)
        
        # Apply text
        apply_text = self.small_font.render("Apply", True, (255, 255, 255))
        apply_rect = apply_text.get_rect(center=self.apply_button.center)
        surface.blit(apply_text, apply_rect)
        
        # Cancel button (grey)
        cancel_color = (100, 100, 100) if self.button_hover["cancel"] else (80, 80, 80)
        pygame.draw.rect(surface, cancel_color, self.cancel_button, border_radius=BORDER_RADIUS)
        
        # Cancel text
        cancel_text = self.small_font.render("Cancel", True, (255, 255, 255))
        cancel_rect = cancel_text.get_rect(center=self.cancel_button.center)
        surface.blit(cancel_text, cancel_rect)

    def handle_event(self, event):
        # Handle mouse movement for button hover
        if event.type == pygame.MOUSEMOTION:
            self.button_hover["apply"] = self.apply_button.collidepoint(event.pos)
            self.button_hover["cancel"] = self.cancel_button.collidepoint(event.pos)
            
        # Handle click on buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.apply_button.collidepoint(event.pos):
                return {"action": "apply"}
            if self.cancel_button.collidepoint(event.pos):
                return {"action": "close"}
                
            # If not on buttons, check if click is inside popup
            if not self.rect.collidepoint(event.pos):
                return {"action": "close"}
        
        # Pass events to input fields
        for field in self.input_fields.values():
            field.handle_event(event)
            
        return None

    def get_values(self) -> dict:
        # Parse input field values for config
        try:
            low_rate = float(self.input_fields["low_rate"].value)
            high_rate = float(self.input_fields["high_rate"].value) 
            threshold = int(self.input_fields["threshold"].value)
            count = int(self.input_fields["block_count"].value)
        except (ValueError, AttributeError):
            # Default values if parsing fails
            low_rate, high_rate = 0.5, 0.8
            threshold, count = 99999, 1
            
        return {
            "dda_params": {"dda": {
                "low_clear_rate": low_rate,
                "high_clear_rate": high_rate,
                "score_threshold": threshold,
                "n_best_fit_blocks": count,
                "n_game_over_blocks": count
            }}
        } 