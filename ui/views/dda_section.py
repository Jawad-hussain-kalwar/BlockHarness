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
from ui.views.dda_views import ThresholdDDAView, StaticDDAView


class DDASection:
    def __init__(self, left_x, top_y, field_width, font, small_font):
        self.font = font
        self.small_font = small_font
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
        
        # Create the DDA view container rect (everything below the dropdown)
        dda_view_height = SECTION_HEIGHT - (y - self.rect.y) - FIELD_HEIGHT * 2 - FIELD_SPACING * 2 - PADDING
        self.dda_view_rect = pygame.Rect(left_x, y, field_width, dda_view_height)
        
        # Initialize DDA views
        self.threshold_dda_view = ThresholdDDAView(self.dda_view_rect, font, small_font)
        self.static_dda_view = StaticDDAView(self.dda_view_rect, font, small_font)
        
        # Set default active view
        self.active_dda_view = self.threshold_dda_view
        
        # Apply button (positioned after the DDA view container)
        apply_button_y = self.dda_view_rect.y + self.dda_view_rect.height + FIELD_SPACING
        self.apply_button_rect = pygame.Rect(left_x, apply_button_y, field_width, FIELD_HEIGHT * 1.5)

    def update_config_fields(self, config):
        """Update input fields from config."""
        # Update the active DDA view's fields
        self.threshold_dda_view.update_config_fields(config)
        self.static_dda_view.update_config_fields(config)
        
        # Set default DDA algorithm if available
        if self.dda_algorithm_dropdown.options:
            dda_algorithm = config.get("dda_algorithm", "ThresholdDDA")
            for i, (value, _) in enumerate(self.dda_algorithm_dropdown.options):
                if value == dda_algorithm:
                    self.dda_algorithm_dropdown.selected_index = i
                    # Update the active DDA view based on selection
                    self._update_active_dda_view(value)
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
        else:
            # Set active view based on the selected algorithm
            self._update_active_dda_view(self.dda_algorithm_dropdown.get_selected_value())

    def _update_active_dda_view(self, algorithm_name):
        """Update the active DDA view based on the selected algorithm."""
        if algorithm_name == "ThresholdDDA":
            self.active_dda_view = self.threshold_dda_view
        elif algorithm_name == "StaticDDA":
            self.active_dda_view = self.static_dda_view
        # Add future DDA types here

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
        
        # Draw the active DDA view
        self.active_dda_view.draw(surface)
        
        # Draw apply button
        pygame.draw.rect(surface, BUTTON_PRIMARY_BG, self.apply_button_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, BUTTON_BORDER, self.apply_button_rect, width=1, border_radius=BORDER_RADIUS)
        apply_text = self.font.render("Apply Changes", True, TEXT_PRIMARY)
        text_x = self.apply_button_rect.x + self.apply_button_rect.width // 2 - apply_text.get_width() // 2
        text_y = self.apply_button_rect.y + self.apply_button_rect.height // 2 - apply_text.get_height() // 2
        surface.blit(apply_text, (text_x, text_y))
        
        # Draw dropdowns
        for dropdown in self.dropdown_menus:
            dropdown.draw(surface)

    def handle_event(self, event):
        """Handle events for the DDA section.
        
        Returns:
            String: "apply" if apply button was clicked, None otherwise
        """
        # Handle active DDA view events
        self.active_dda_view.handle_event(event)
        
        # Handle dropdown events
        previous_value = None
        if self.dda_algorithm_dropdown.options:
            previous_value = self.dda_algorithm_dropdown.get_selected_value()
            
        for dropdown in self.dropdown_menus:
            dropdown.handle_event(event)
        
        # Check if the DDA algorithm selection changed
        if self.dda_algorithm_dropdown.options and previous_value != self.dda_algorithm_dropdown.get_selected_value():
            self._update_active_dda_view(self.dda_algorithm_dropdown.get_selected_value())
        
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
        # Get configuration values from the active DDA view
        config_values = self.active_dda_view.get_config_values()
        if config_values is None:
            return None
            
        # Add the selected DDA algorithm
        dda_algorithm = None
        if self.dda_algorithm_dropdown.options:
            dda_algorithm = self.dda_algorithm_dropdown.get_selected_value()
            
        # Update the configuration with the selected algorithm
        config_values["dda_algorithm"] = dda_algorithm or "ThresholdDDA"
        
        return config_values
    
    def get_selected_dda_algorithm(self):
        """Get the selected DDA algorithm from the dropdown.
        
        Returns:
            String: The selected DDA algorithm name, or None if no selection
        """
        if self.dda_algorithm_dropdown.options:
            return self.dda_algorithm_dropdown.get_selected_value()
        return None 