# ui/views/main_view.py
import pygame
from ui.colours import BG_COLOR, FG_COLOR
from ui.font_manager import font_manager
from ui.layout import GAME_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH, BORDER_RADIUS, PADDING
from ui.views.game_section import GameSection
from ui.views.settings_popup import SettingsPopup
from typing import Optional, Dict, Any, Tuple

class MainView:
    """Main view displaying only the game and a settings popup."""
    def __init__(self):
        # Fixed window size
        self.window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        # Fonts
        self.font = font_manager.get_font('Ubuntu-Regular', 18)
        self.small_font = font_manager.get_font('Ubuntu-Regular', 14)
        # Sections
        self.game_section = GameSection(self.font, self.small_font)
        self.settings_popup = SettingsPopup(self.font, self.small_font)
        
        # Settings button in top-right corner
        self.settings_btn_size = 40
        self.settings_btn_padding = 10
        self.settings_btn_rect = pygame.Rect(
            WINDOW_WIDTH - self.settings_btn_size - self.settings_btn_padding,
            self.settings_btn_padding,
            self.settings_btn_size,
            self.settings_btn_size
        )

    def update_config_fields(self, config):
        # Update settings popup fields with DDA config values
        dda_params = config.get('dda_params', {}).get('dda', {})
        if dda_params:
            self.settings_popup.input_fields["low_rate"].value = str(dda_params.get('low_clear_rate', 0.5))
            self.settings_popup.input_fields["high_rate"].value = str(dda_params.get('high_clear_rate', 0.8)) 
            self.settings_popup.input_fields["threshold"].value = str(dda_params.get('score_threshold', 99999))
            self.settings_popup.input_fields["block_count"].value = str(dda_params.get('n_best_fit_blocks', 1))

    def get_config_values(self):
        return self.settings_popup.get_values()

    def render(self, surface, engine, show_settings):
        # Clear screen
        surface.fill(BG_COLOR)
        # render game section
        self.game_section.render(surface, engine)
        
        # Render settings button in top-right corner
        pygame.draw.rect(surface, FG_COLOR, self.settings_btn_rect, border_radius=8)
        
        # Draw a simple gear icon (three lines representing settings)
        center_x = self.settings_btn_rect.centerx
        center_y = self.settings_btn_rect.centery
        icon_size = self.settings_btn_size * 0.6
        
        # Horizontal line
        pygame.draw.line(
            surface, 
            BG_COLOR,
            (center_x - icon_size/2, center_y),
            (center_x + icon_size/2, center_y),
            3
        )
        
        # Top diagonal line
        pygame.draw.line(
            surface, 
            BG_COLOR,
            (center_x - icon_size/2, center_y - icon_size/3),
            (center_x + icon_size/2, center_y - icon_size/3),
            3
        )
        
        # Bottom diagonal line
        pygame.draw.line(
            surface, 
            BG_COLOR,
            (center_x - icon_size/2, center_y + icon_size/3),
            (center_x + icon_size/2, center_y + icon_size/3),
            3
        )
        
        # render settings popup if active
        if show_settings:
            self.settings_popup.render(surface)
    
    def _handle_settings_events(self, event):
        """Handle events when settings popup is active.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            Optional[Dict]: Action dictionary or None
        """
        return self.settings_popup.handle_event(event)
    
    def _handle_preview_click(self, event, scale_factor=1.0):
        """Handle clicks on the preview area.
        
        Args:
            event: Pygame mouse event
            scale_factor: Scale factor for touch position conversion
            
        Returns:
            Optional[Dict]: Action dictionary or None
        """
        # Convert touch position to original coordinates
        touch_x = event.pos[0] / scale_factor
        touch_y = event.pos[1] / scale_factor
        
        preview_index = None
        try:
            preview_index = self.game_section.handle_preview_click(touch_x, touch_y)
        except Exception:
            preview_index = None
            
        if preview_index is not None:
            return {'action': 'select_block', 'index': preview_index}
        return None
    
    def _handle_board_click(self, event, scale_factor=1.0):
        """Handle clicks on the game board.
        
        Args:
            event: Pygame mouse event
            scale_factor: Scale factor for touch position conversion
            
        Returns:
            Optional[Dict]: Action dictionary or None
        """
        # Convert touch position to original coordinates
        touch_x = event.pos[0] / scale_factor
        touch_y = event.pos[1] / scale_factor
        
        grid_pos = None
        try:
            grid_pos = self.game_section.handle_board_click(touch_x, touch_y)
            # Ensure grid positions are integers
            if grid_pos:
                grid_pos = (int(grid_pos[0]), int(grid_pos[1]))
        except Exception:
            grid_pos = None
            
        if grid_pos:
            return {'action': 'place_block', 'position': grid_pos}
        return None
    
    def _handle_restart_button_click(self, event, engine, scale_factor=1.0):
        """Handle clicks on the restart button.
        
        Args:
            event: Pygame mouse event
            engine: Game engine instance
            scale_factor: Scale factor for touch position conversion
            
        Returns:
            Optional[Dict]: Action dictionary or None
        """
        # Convert touch position to original coordinates
        touch_x = event.pos[0] / scale_factor
        touch_y = event.pos[1] / scale_factor
        
        if engine and engine.game_over and hasattr(self.game_section, 'is_restart_button_clicked'):
            if self.game_section.is_restart_button_clicked((touch_x, touch_y)):
                return {'action': 'restart'}
        return None
        
    def _check_settings_button_click(self, event, scale_factor=1.0):
        """Check if settings button was clicked.
        
        Args:
            event: Pygame mouse event
            scale_factor: Scale factor for touch position conversion
            
        Returns:
            Optional[Dict]: Action dictionary or None
        """
        # Convert touch position to original coordinates
        touch_x = event.pos[0] / scale_factor
        touch_y = event.pos[1] / scale_factor
        
        if self.settings_btn_rect.collidepoint(touch_x, touch_y):
            return {'action': 'toggle_settings'}
        return None

    def handle_event(self, event, show_settings=False, engine=None, scale_factor=1.0):
        # Handle settings popup events only if popup is visible
        if show_settings:
            action = self._handle_settings_events(event)
            if action:
                return action
                
        # If popup is not visible, check for other clicks
        if not show_settings and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # First check if settings button was clicked
            action = self._check_settings_button_click(event, scale_factor)
            if action:
                return action
                
            # Then check game preview click
            action = self._handle_preview_click(event, scale_factor)
            if action:
                return action
                
            # Then check game board click
            action = self._handle_board_click(event, scale_factor)
            if action:
                return action
                
            # Check for restart button click
            action = self._handle_restart_button_click(event, engine, scale_factor)
            if action:
                return action
                
        return None 