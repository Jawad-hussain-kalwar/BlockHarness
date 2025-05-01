# ui/views/main_view.py
import pygame
from ui.colours import BG_COLOR
from ui.layout import SIDEBAR_WIDTH, SIDEBAR_PADDING, BORDER_RADIUS, SECTION_WIDTH
from ui.font_manager import font_manager

from ui.views.dda_section import DDASection
from ui.views.simulation_section import SimulationSection
from ui.views.game_section import GameSection
from ui.views.state_section import StateSection

class MainView:
    """Main view that orchestrates all UI sections."""
    
    def __init__(self, window_size):
        self.window_size = window_size
        
        # Initialize fonts
        self.font = font_manager.get_font('Ubuntu-Regular', 18)
        self.large_font = font_manager.get_font('Ubuntu-Regular', 36)
        self.small_font = font_manager.get_font('Ubuntu-Regular', 14)
        
        # Initialize section components
        self.create_sections()
    
    def create_sections(self):
        # Left section for DDA (left side of sidebar)
        left_x = SIDEBAR_PADDING
        top_y = SIDEBAR_PADDING
        self.dda_section = DDASection(left_x, top_y, SECTION_WIDTH, self.font, self.small_font)
        
        # Right section for Simulation controls (right side of sidebar)
        right_x = SIDEBAR_PADDING * 2 + SECTION_WIDTH
        self.simulation_section = SimulationSection(right_x, top_y, SECTION_WIDTH, self.font, self.small_font)
        
        # Game section (board, preview, HUD)
        self.game_section = GameSection(self.window_size, self.font, self.small_font)
        
        # State section (right sidebar)
        self.state_section = StateSection(self.window_size, self.font, self.small_font)
    
    def handle_resize(self, new_size):
        """Handle window resize events."""
        self.window_size = new_size
        self.create_sections()
        return self
    
    def update_config_fields(self, config):
        """Update DDA section input fields from config."""
        self.dda_section.update_config_fields(config)
    
    def update_ai_player_dropdown(self, ai_players):
        """Update the AI player dropdown with available AI players."""
        self.simulation_section.update_ai_player_dropdown(ai_players)
    
    def update_dda_algorithm_dropdown(self, dda_algorithms):
        """Update the DDA algorithm dropdown with available algorithms."""
        self.dda_section.update_dda_algorithm_dropdown(dda_algorithms)
    
    def draw(self, surface, engine, simulation_running=False, current_run=0, simulation_runs=0):
        """Draw all UI sections."""
        # Clear the screen
        surface.fill(BG_COLOR)
        
        # Draw individual sections
        self.dda_section.draw(surface)
        self.simulation_section.draw(surface, simulation_running, current_run, simulation_runs)
        self.game_section.draw(surface, engine)
        self.state_section.draw(surface, engine)
    
    def handle_event(self, event):
        """Handle UI-specific events for all sections.
        
        Returns:
            dict: Action and parameters if action needed, or None if no action
        """
        # Handle DDA section events
        dda_action = self.dda_section.handle_event(event)
        if dda_action:
            return {"action": dda_action}
        
        # Handle simulation section events
        sim_action = self.simulation_section.handle_event(event)
        if sim_action:
            return {"action": sim_action}
        
        # Handle game events
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            
            # Check if restart button was clicked
            if self.is_restart_button_clicked((x, y)):
                return {"action": "restart"}
            
            # Check if click is on the preview area
            preview_index = self.handle_preview_click(x, y)
            if preview_index is not None:
                return {"action": "select_block", "index": preview_index}
            
            # Check if click is on the board area
            grid_pos = self.handle_board_click(x, y)
            if grid_pos:
                return {"action": "place_block", "position": grid_pos}
        
        # No UI action taken
        return None
    
    def get_config_values(self):
        """Get the current configuration values from the DDA section."""
        return self.dda_section.get_config_values()
    
    def get_simulation_values(self):
        """Get the current simulation values from the simulation section."""
        return self.simulation_section.get_simulation_values()
    
    def get_selected_dda_algorithm(self):
        """Get the selected DDA algorithm from the dropdown."""
        return self.dda_section.get_selected_dda_algorithm()
    
    def handle_board_click(self, x, y):
        """Handle click on the game board."""
        return self.game_section.handle_board_click(x, y)
    
    def handle_preview_click(self, x, y):
        """Handle click on the preview area."""
        return self.game_section.handle_preview_click(x, y)
    
    def is_restart_button_clicked(self, pos):
        """Check if the restart button was clicked."""
        return self.game_section.is_restart_button_clicked(pos) 