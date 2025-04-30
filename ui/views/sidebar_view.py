# ui/views/sidebar_view.py
import pygame
from ui.colours import (
    BLACK, WHITE, BLUE, GREEN, DARK_GRAY,
    SIDEBAR_BG, SECTION_BG, SECTION_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY,
    INPUT_BG, INPUT_BORDER, INPUT_FOCUS,
    BUTTON_PRIMARY_BG, BUTTON_PRIMARY_TEXT,
    BUTTON_SECONDARY_BG, BUTTON_SECONDARY_TEXT,
    BUTTON_BORDER
)
from ui.layout import (
    SIDEBAR_WIDTH, SIDEBAR_PADDING, FIELD_HEIGHT, FIELD_SPACING,
    SECTION_SPACING, LABEL_SPACING, BORDER_RADIUS
)
from ui.input_field import InputField
from ui.dropdown_menu import DropdownMenu

class SidebarView:
    def __init__(self, window_size, font, small_font):
        self.window_size = window_size
        self.font = font
        self.small_font = small_font
        
        # Initialize positions and rects
        self.create_config_inputs()
    
    def create_config_inputs(self):
        # Left sidebar coordinates
        left_x = SIDEBAR_PADDING
        top_y = SIDEBAR_PADDING
        field_width = SIDEBAR_WIDTH - (SIDEBAR_PADDING * 2)  # Adjust field width to fit sidebar
        
        self.input_fields = []
        self.dropdown_menus = []
        self.apply_button_rect = None
        
        # Split the sidebar into two halves
        half_height = self.window_size[1] // 2
        separator_y = half_height - SECTION_SPACING // 2
        
        # Top half - DDA (Dynamic Difficulty Adjustment) section
        # -----------------------------------------------------
        y = top_y
        
        # DDA section title
        self.dda_section_title = (left_x, y)
        y += FIELD_HEIGHT
        
        # Initial weights label
        self.initial_weights_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING + 4
        
        # Initial weights input
        initial_field_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.initial_weights_field = InputField(initial_field_rect, "", 20)
        self.input_fields.append(self.initial_weights_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Threshold 1
        y += FIELD_SPACING
        self.threshold1_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        
        # Threshold 1 score
        threshold1_score_rect = pygame.Rect(left_x, y, field_width // 2 - 5, FIELD_HEIGHT)
        self.threshold1_score_field = InputField(threshold1_score_rect, "", 5, numeric=True)
        self.input_fields.append(self.threshold1_score_field)
        
        # Threshold 1 weights
        threshold1_weights_rect = pygame.Rect(left_x + field_width // 2 + 5, y, field_width // 2 - 5, FIELD_HEIGHT)
        self.threshold1_weights_field = InputField(threshold1_weights_rect, "", 20)
        self.input_fields.append(self.threshold1_weights_field)
        y += FIELD_HEIGHT + LABEL_SPACING + 10  # Add space for helper labels
        
        # Threshold 2
        y += FIELD_SPACING
        self.threshold2_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        
        # Threshold 2 score
        threshold2_score_rect = pygame.Rect(left_x, y, field_width // 2 - 5, FIELD_HEIGHT)
        self.threshold2_score_field = InputField(threshold2_score_rect, "", 5, numeric=True)
        self.input_fields.append(self.threshold2_score_field)
        
        # Threshold 2 weights
        threshold2_weights_rect = pygame.Rect(left_x + field_width // 2 + 5, y, field_width // 2 - 5, FIELD_HEIGHT)
        self.threshold2_weights_field = InputField(threshold2_weights_rect, "", 20)
        self.input_fields.append(self.threshold2_weights_field)
        y += FIELD_HEIGHT + LABEL_SPACING + 10  # Add space for helper labels
        
        # Apply button
        y += SECTION_SPACING
        self.apply_button_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT * 1.5)
        
        # Bottom half - Simulation Controls section
        # -----------------------------------------------------
        y = separator_y + SECTION_SPACING
        
        # Simulation section title
        self.simulation_label = (left_x, y)
        y += FIELD_HEIGHT
        
        # AI Player dropdown
        self.ai_player_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        ai_player_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.ai_player_dropdown = DropdownMenu(ai_player_rect, [])  # Will be populated later
        self.dropdown_menus.append(self.ai_player_dropdown)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Steps per second input
        self.steps_per_second_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        steps_per_second_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.steps_per_second_field = InputField(steps_per_second_rect, "1.0", 5, numeric=True)
        self.input_fields.append(self.steps_per_second_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Number of runs input
        self.runs_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        runs_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.runs_field = InputField(runs_rect, "1", 3, numeric=True)
        self.input_fields.append(self.runs_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Simulation buttons
        self.simulate_button_rect = pygame.Rect(left_x, y, field_width // 2 - 5, FIELD_HEIGHT * 1.5)
        self.abort_button_rect = pygame.Rect(left_x + field_width // 2 + 5, y, field_width // 2 - 5, FIELD_HEIGHT * 1.5)
    
    def update_config_fields(self, config):
        # Update input fields from config
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
        # Draw sidebar background
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, self.window_size[1])
        pygame.draw.rect(surface, SIDEBAR_BG, sidebar_rect)
        
        # Create section panels with rounded corners
        # DDA section panel
        half_height = self.window_size[1] // 2
        separator_y = half_height - SECTION_SPACING // 2
        
        dda_panel_rect = pygame.Rect(
            SIDEBAR_PADDING // 2, 
            SIDEBAR_PADDING // 2, 
            SIDEBAR_WIDTH - SIDEBAR_PADDING, 
            separator_y - SIDEBAR_PADDING // 2
        )
        pygame.draw.rect(surface, SECTION_BG, dda_panel_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, dda_panel_rect, width=1, border_radius=BORDER_RADIUS)
        
        # Simulation controls panel
        sim_panel_rect = pygame.Rect(
            SIDEBAR_PADDING // 2, 
            separator_y + SIDEBAR_PADDING // 2, 
            SIDEBAR_WIDTH - SIDEBAR_PADDING, 
            self.window_size[1] - separator_y - SIDEBAR_PADDING
        )
        pygame.draw.rect(surface, SECTION_BG, sim_panel_rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, sim_panel_rect, width=1, border_radius=BORDER_RADIUS)
        
        # Draw DDA section title
        dda_title = self.font.render("Dynamic Difficulty Adjustment", True, TEXT_PRIMARY)
        surface.blit(dda_title, self.dda_section_title)
        
        # Draw initial weights label
        label = self.font.render("Initial Shape Weights (0-10):", True, TEXT_PRIMARY)
        surface.blit(label, self.initial_weights_label)
        
        # Draw threshold 1 label
        label = self.font.render("Difficulty Threshold 1:", True, TEXT_PRIMARY)
        surface.blit(label, self.threshold1_label)
        
        # Draw threshold 2 label
        label = self.font.render("Difficulty Threshold 2:", True, TEXT_PRIMARY)
        surface.blit(label, self.threshold2_label)
        
        # Draw threshold helper labels
        score_label = self.small_font.render("Score", True, TEXT_SECONDARY)
        weights_label = self.small_font.render("Weights", True, TEXT_SECONDARY)
        
        # Position labels UNDER the input fields with consistent spacing
        surface.blit(score_label, (self.threshold1_score_field.rect.x, 
                                  self.threshold1_score_field.rect.y + self.threshold1_score_field.rect.height + LABEL_SPACING))
        surface.blit(weights_label, (self.threshold1_weights_field.rect.x, 
                                     self.threshold1_weights_field.rect.y + self.threshold1_weights_field.rect.height + LABEL_SPACING))
        
        surface.blit(score_label, (self.threshold2_score_field.rect.x, 
                                  self.threshold2_score_field.rect.y + self.threshold2_score_field.rect.height + LABEL_SPACING))
        surface.blit(weights_label, (self.threshold2_weights_field.rect.x, 
                                     self.threshold2_weights_field.rect.y + self.threshold2_weights_field.rect.height + LABEL_SPACING))
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface, self.font)
        
        # Draw apply button with rounded corners
        if self.apply_button_rect:
            pygame.draw.rect(surface, BUTTON_PRIMARY_BG, self.apply_button_rect, border_radius=BORDER_RADIUS)
            pygame.draw.rect(surface, BUTTON_BORDER, self.apply_button_rect, width=1, border_radius=BORDER_RADIUS)
            
            apply_text = self.font.render("Apply Changes", True, BUTTON_PRIMARY_TEXT)
            text_rect = apply_text.get_rect(center=self.apply_button_rect.center)
            surface.blit(apply_text, text_rect)
        
        # Draw simulation section title
        simulation_title = self.font.render("Simulation Controls", True, TEXT_PRIMARY)
        surface.blit(simulation_title, self.simulation_label)
        
        # Draw AI player dropdown label
        ai_player_label = self.font.render("AI Player:", True, TEXT_SECONDARY)
        surface.blit(ai_player_label, self.ai_player_label)
        
        # Draw steps per second label
        steps_label = self.font.render("Steps per second:", True, TEXT_SECONDARY)
        surface.blit(steps_label, self.steps_per_second_label)
        
        # Draw runs label
        runs_label = self.font.render("Number of runs:", True, TEXT_SECONDARY)
        surface.blit(runs_label, self.runs_label)
        
        # Draw simulation buttons with rounded corners
        if self.simulate_button_rect:
            pygame.draw.rect(surface, BUTTON_PRIMARY_BG, self.simulate_button_rect, border_radius=BORDER_RADIUS)
            pygame.draw.rect(surface, BUTTON_BORDER, self.simulate_button_rect, width=1, border_radius=BORDER_RADIUS)
            
            simulate_text = self.font.render("Simulate", True, BUTTON_PRIMARY_TEXT)
            text_rect = simulate_text.get_rect(center=self.simulate_button_rect.center)
            surface.blit(simulate_text, text_rect)
        
        if self.abort_button_rect:
            pygame.draw.rect(surface, BUTTON_SECONDARY_BG, self.abort_button_rect, border_radius=BORDER_RADIUS)
            pygame.draw.rect(surface, BUTTON_BORDER, self.abort_button_rect, width=1, border_radius=BORDER_RADIUS)
            
            abort_text = self.font.render("Abort", True, BUTTON_SECONDARY_TEXT)
            text_rect = abort_text.get_rect(center=self.abort_button_rect.center)
            surface.blit(abort_text, text_rect)
        
        # Draw simulation status if running
        if simulation_running:
            status_y = self.abort_button_rect.bottom + FIELD_SPACING
            status_text = self.font.render(f"Run: {current_run + 1}/{simulation_runs}", True, BLUE)
            surface.blit(status_text, (self.simulate_button_rect.x, status_y))
        
        # Draw dropdown menus last to ensure expanded dropdowns are on top
        for dropdown in self.dropdown_menus:
            dropdown.draw(surface, self.font)
    
    def handle_event(self, event):
        # Handle input field events
        for field in self.input_fields:
            field.handle_event(event)
        
        # Handle dropdown menu events
        for dropdown in self.dropdown_menus:
            dropdown.handle_event(event)
        
        # Return clicked button or None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            
            if self.apply_button_rect and self.apply_button_rect.collidepoint(x, y):
                return "apply"
            
            if self.simulate_button_rect and self.simulate_button_rect.collidepoint(x, y):
                return "simulate"
            
            if self.abort_button_rect and self.abort_button_rect.collidepoint(x, y):
                return "abort"
        
        return None
    
    def get_config_values(self):
        try:
            # Parse initial weights
            initial_weights = list(map(int, self.initial_weights_field.value.split(',')))
            
            # Import shapes here to avoid circular imports
            from engine.shapes import SHAPES
            
            # Validate weights count
            if len(initial_weights) != len(SHAPES):
                raise ValueError(f"Initial weights must have {len(SHAPES)} values")
            
            # Parse threshold 1
            threshold1_score = int(self.threshold1_score_field.value)
            threshold1_weights = list(map(int, self.threshold1_weights_field.value.split(',')))
            if len(threshold1_weights) != len(SHAPES):
                raise ValueError(f"Threshold 1 weights must have {len(SHAPES)} values")
            
            # Parse threshold 2
            threshold2_score = int(self.threshold2_score_field.value)
            threshold2_weights = list(map(int, self.threshold2_weights_field.value.split(',')))
            if len(threshold2_weights) != len(SHAPES):
                raise ValueError(f"Threshold 2 weights must have {len(SHAPES)} values")
            
            # Return parsed values
            return {
                "shape_weights": initial_weights,
                "difficulty_thresholds": [
                    (threshold1_score, threshold1_weights),
                    (threshold2_score, threshold2_weights)
                ]
            }
        except (ValueError, IndexError) as e:
            print(f"Config error: {e}")
            return None
    
    def get_simulation_values(self):
        try:
            steps_per_second = float(self.steps_per_second_field.value)
            runs = int(self.runs_field.value)
            
            # Get selected AI player
            ai_player_name = self.ai_player_dropdown.selected_value if self.ai_player_dropdown.options else None
            
            return steps_per_second, runs, ai_player_name
        except ValueError as e:
            print(f"Simulation value error: {e}")
            return None 