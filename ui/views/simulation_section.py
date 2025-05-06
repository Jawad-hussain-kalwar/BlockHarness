import pygame
from ui.colours import (
    TEXT_PRIMARY,
    BUTTON_PRIMARY_BG, TEXT_PRIMARY,
    BUTTON_RED_BG, BUTTON_SECONDARY_BG, BUTTON_SECONDARY_TEXT,
    BUTTON_BORDER,
    SECTION_BG, SECTION_BORDER
)
from ui.layout import (
    PADDING, DDA_WIDTH, SIM_WIDTH, SECTION_HEIGHT,
    FIELD_HEIGHT, FIELD_SPACING, BORDER_RADIUS
)
from ui.input_field import InputField
from ui.dropdown_menu import DropdownMenu
from ui.debug import draw_debug_rect


class SimulationSection:
    def __init__(self, left_x, top_y, field_width, font, small_font):
        self.font = font
        self.small_font = small_font
        self.input_fields = []
        self.dropdown_menus = []
        
        # Initialize section rectangle with new layout constants
        x_origin = PADDING + DDA_WIDTH + PADDING
        y_origin = PADDING
        self.rect = pygame.Rect(x_origin, y_origin, SIM_WIDTH, SECTION_HEIGHT)
        
        # Use self.rect for positioning instead of passed parameters
        left_x = self.rect.x + PADDING
        top_y = self.rect.y + PADDING
        field_width = SIM_WIDTH - 2 * PADDING
        
        # Initialize positions and UI elements
        y = top_y
        
        # Simulation section title
        self.simulation_label = (left_x, y)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # AI Player dropdown
        self.ai_player_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        ai_player_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.ai_player_dropdown = DropdownMenu(ai_player_rect, [])
        self.dropdown_menus.append(self.ai_player_dropdown)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Steps per second input
        self.steps_per_second_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        steps_per_second_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.steps_per_second_field = InputField(steps_per_second_rect, "1.0", 5, numeric=True)
        self.input_fields.append(self.steps_per_second_field)
        y += FIELD_HEIGHT + FIELD_SPACING * 2
        
        # Number of runs input
        self.runs_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        runs_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.runs_field = InputField(runs_rect, "1", 3, numeric=True)
        self.input_fields.append(self.runs_field)
        y += FIELD_HEIGHT + FIELD_SPACING * 3
        
        # Simulation buttons
        button_height = FIELD_HEIGHT * 1.5
        self.simulate_button_rect = pygame.Rect(left_x, y, field_width, button_height)
        self.abort_button_rect = pygame.Rect(left_x, y + button_height + FIELD_SPACING, field_width, button_height)

    def update_ai_player_dropdown(self, ai_players):
        """Update the AI player dropdown with available AI players.
        
        Args:
            ai_players: List of (name, description) tuples for available AI players
        """
        self.ai_player_dropdown.options = ai_players
        
        # Reset selected index to 0 if needed
        if not self.ai_player_dropdown.options:
            self.ai_player_dropdown.selected_index = 0

    def draw(self, surface, simulation_running, current_run, simulation_runs):
        """Draw the simulation section elements."""
        # Draw section panel background and border
        pygame.draw.rect(surface, SECTION_BG, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, self.rect, width=1, border_radius=BORDER_RADIUS)
        # Draw debug border if enabled
        draw_debug_rect(surface, self.rect, "simulation")
        
        # Draw simulation section title
        sim_title = self.font.render("Simulation Controls", True, TEXT_PRIMARY)
        surface.blit(sim_title, self.simulation_label)
        
        # Draw AI player label
        label = self.font.render("AI Player:", True, TEXT_PRIMARY)
        surface.blit(label, self.ai_player_label)
        
        # Draw steps per second label
        label = self.font.render("Steps per second:", True, TEXT_PRIMARY)
        surface.blit(label, self.steps_per_second_label)
        
        # Draw runs label
        label = self.font.render("Number of runs:", True, TEXT_PRIMARY)
        surface.blit(label, self.runs_label)
        
        # Draw input fields and dropdowns
        for field in self.input_fields:
            field.draw(surface)
            
            # Display infinity symbol for steps per second = 0
            if field is self.steps_per_second_field and field.value == "0":
                field_rect = field.rect
                infinity_symbol = self.font.render("∞", True, TEXT_PRIMARY)
                x_pos = field_rect.x + field_rect.width + 5
                y_pos = field_rect.y + (field_rect.height - infinity_symbol.get_height()) // 2
                surface.blit(infinity_symbol, (x_pos, y_pos))
        
        for dropdown in self.dropdown_menus:
            dropdown.draw(surface)
        
        # Draw start button
        pygame.draw.rect(surface, BUTTON_PRIMARY_BG, self.simulate_button_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, BUTTON_BORDER, self.simulate_button_rect, width=1, border_radius=BORDER_RADIUS)
        
        if not simulation_running:
            sim_text = self.font.render("Start", True, TEXT_PRIMARY)
        else:
            # Show 1-based run count (initially 1 instead of 0)
            sim_text = self.small_font.render(f"Run {current_run or 1}/{simulation_runs}", True, TEXT_PRIMARY)
        
        text_x = self.simulate_button_rect.x + self.simulate_button_rect.width // 2 - sim_text.get_width() // 2
        text_y = self.simulate_button_rect.y + self.simulate_button_rect.height // 2 - sim_text.get_height() // 2
        surface.blit(sim_text, (text_x, text_y))
        
        # Always draw abort button (enabled only when simulation is running)
        button_color = BUTTON_RED_BG if simulation_running else BUTTON_SECONDARY_BG  # Grayed out when not running
        pygame.draw.rect(surface, button_color, self.abort_button_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, BUTTON_BORDER, self.abort_button_rect, width=1, border_radius=BORDER_RADIUS)
        
        abort_text = self.font.render("Abort", True, BUTTON_SECONDARY_TEXT if simulation_running else (150, 150, 150))
        text_x = self.abort_button_rect.x + self.abort_button_rect.width // 2 - abort_text.get_width() // 2
        text_y = self.abort_button_rect.y + self.abort_button_rect.height // 2 - abort_text.get_height() // 2
        surface.blit(abort_text, (text_x, text_y))

    def handle_event(self, event):
        """Handle events for the simulation section.
        
        Returns:
            String: "simulate" or "abort" if corresponding button was clicked, None otherwise
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
            
            # Simulate button
            if self.simulate_button_rect.collidepoint(mouse_pos):
                return "simulate"
            
            # Abort button
            if self.abort_button_rect.collidepoint(mouse_pos):
                return "abort"
        
        # No simulation section action taken
        return None

    def get_simulation_values(self):
        """Get the current simulation values from the section.
        
        Returns:
            Tuple of (steps_per_second, simulation_runs, ai_player_name)
            or None if validation fails
        """
        try:
            # Parse steps per second
            steps_per_second = float(self.steps_per_second_field.value)
            if steps_per_second < 0:
                print("[ui/views/simulation_section.py][186] Steps per second must be greater than or equal to 0")
                return None
            
            # Parse number of runs
            runs = int(self.runs_field.value)
            if runs <= 0:
                print("[ui/views/simulation_section.py][190] Number of runs must be greater than 0")
                return None
            
            # Get selected AI player
            ai_player = self.ai_player_dropdown.get_selected_value()
            
            return (steps_per_second, runs, ai_player)
            
        except ValueError as e:
            print(f"[ui/views/simulation_section.py][192] Invalid simulation values: {e}")
            return None 