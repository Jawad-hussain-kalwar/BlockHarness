# ui/views/sidebar_view.py
import pygame
from ui.colours import (
    SIDEBAR_BG, SECTION_BG, SECTION_BORDER
)
from ui.layout import (
    SIDEBAR_WIDTH, SIDEBAR_PADDING, BORDER_RADIUS,
    SECTION_SPACING
)
from ui.views.dda_section import DDASection
from ui.views.simulation_section import SimulationSection

class SidebarView:
    def __init__(self, window_size, font, small_font):
        self.window_size = window_size
        self.font = font
        self.small_font = small_font
        
        # Initialize sections
        self.create_sections()
    
    def create_sections(self):
        # Left sidebar coordinates
        left_x = SIDEBAR_PADDING
        field_width = SIDEBAR_WIDTH - (SIDEBAR_PADDING * 2)
        
        # Split the sidebar into two halves
        half_height = self.window_size[1] // 2
        separator_y = half_height - SECTION_SPACING // 2
        
        # Create DDA section (top half)
        top_y = SIDEBAR_PADDING
        self.dda_section = DDASection(left_x, top_y, field_width, self.font, self.small_font)
        
        # Create Simulation section (bottom half)
        sim_top_y = separator_y + SECTION_SPACING
        self.simulation_section = SimulationSection(left_x, sim_top_y, field_width, self.font, self.small_font)
    
    def update_config_fields(self, config):
        # Update DDA section input fields from config
        self.dda_section.update_config_fields(config)
    
    def update_ai_player_dropdown(self, ai_players):
        """Update the AI player dropdown with available AI players."""
        self.simulation_section.update_ai_player_dropdown(ai_players)
    
    def update_dda_algorithm_dropdown(self, dda_algorithms):
        """Update the DDA algorithm dropdown with available algorithms."""
        self.dda_section.update_dda_algorithm_dropdown(dda_algorithms)
    
    def draw(self, surface, simulation_running, current_run, simulation_runs):
        # Draw sidebar background
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, self.window_size[1])
        pygame.draw.rect(surface, SIDEBAR_BG, sidebar_rect)
        
        # Create section panels with rounded corners
        half_height = self.window_size[1] // 2
        separator_y = half_height - SECTION_SPACING // 2
        
        # DDA section panel
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
        
        # Draw DDA section
        self.dda_section.draw(surface)
        
        # Draw simulation section
        self.simulation_section.draw(surface, simulation_running, current_run, simulation_runs)
            
    def handle_event(self, event):
        # Handle DDA section events
        dda_action = self.dda_section.handle_event(event)
        if dda_action:
            return dda_action
        
        # Handle simulation section events
        sim_action = self.simulation_section.handle_event(event)
        if sim_action:
            return sim_action
        
        # No sidebar action taken
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