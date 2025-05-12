# BlockHarness/engine/game_controller.py
import pygame
import ctypes
import sys
import os
from typing import Optional, Dict, Any, cast, Tuple

from engine.game_engine import GameEngine
from ui.views.main_view import MainView
from ui.layout import WINDOW_HEIGHT, WINDOW_WIDTH


class GameController:
    """Controller for handling Pygame UI and game interactions."""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Load configuration
        self.config = config

        # Create game engine
        self.engine = GameEngine(self.config)

        # Make process DPI-aware (Windows)
        if sys.platform == "win32":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        # Initialize pygame
        pygame.init()
        pygame.display.set_caption('BlockHarness')

        # Load icon
        try:
            ico_path = os.path.join(os.path.dirname(__file__), '..', 'ico.ico')
            icon = pygame.image.load(ico_path)
            pygame.display.set_icon(icon)
        except Exception:
            pass

        # Get device screen info for responsive sizing
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # For Android, we want to use full screen width and scale height proportionally
        self.scale_factor = self.screen_width / WINDOW_WIDTH
        self.scaled_height = int(WINDOW_HEIGHT * self.scale_factor)
        
        # Use fullscreen for Android
        if sys.platform == 'android':
            self.window = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            # For other platforms, maintain the aspect ratio but make it responsive
            self.window = pygame.display.set_mode((self.screen_width, self.scaled_height))
        
        # Config and view
        self.main_view = MainView()
        self.main_view.update_config_fields(self.config)
        # Internal flag for settings popup
        self.show_settings = False
        
        # Command mapping for UI actions
        self.action_handlers = {
            'apply': self.apply_config_changes,
            'restart': self.restart_game,
            'select_block': self._on_select_block,
            'place_block': self._on_place_block,
            'toggle_settings': self._toggle_settings_popup,
            'close': self._close_settings_popup,
        }

    def apply_config_changes(self, ui_action=None) -> bool:
        """Apply settings from popup to config and restart engine."""
        new_conf = self.main_view.get_config_values()
        if new_conf:
            # Merge new_conf into self.config (nested merge for DDA params)
            if 'dda_params' in new_conf and isinstance(new_conf, dict) and 'dda_params' in self.config:
                dda_params_dict = cast(Dict[str, Any], new_conf['dda_params'])
                if 'dda' in dda_params_dict and 'dda' in self.config['dda_params']:
                    self.config['dda_params']['dda'].update(dda_params_dict['dda'])
                else:
                    self.config['dda_params'].update(dda_params_dict)
            else:
                self.config.update(cast(Dict[str, Any], new_conf))
            #print how many fields were updated
            print(f"[engine/game_controller.py][84] {len(new_conf)} fields were updated")

            # Recreate engine with updated config
            self.engine = GameEngine(self.config)
            # Update view with new config values
            self.main_view.update_config_fields(self.config)
            # Close popup after applying
            self.show_settings = False
            return True
        return False

    def restart_game(self) -> None:
        """Restart the game with current config."""
        self.engine = GameEngine(self.config)
        # Make sure to close settings popup if open
        self.show_settings = False
        
    # Action handler methods
    def _on_select_block(self, data: Dict[str, Any]) -> None:
        """Handle block selection action."""
        idx = data.get('index')
        if idx is not None:
            self.engine.select_preview_block(idx)

    def _on_place_block(self, data: Dict[str, Any]) -> None:
        """Handle block placement action."""
        pos = data.get('position')
        if pos:
            self.engine.place_selected_block(*pos)

    def _toggle_settings_popup(self, ui_action=None) -> None:
        """Toggle the visibility of the settings popup."""
        self.show_settings = not self.show_settings
        
    def _close_settings_popup(self, ui_action=None) -> None:
        """Close the settings popup."""
        self.show_settings = False

    def handle_events(self) -> bool:
        """Process Pygame events and UI actions."""
        for event in pygame.event.get():
            # Handle pygame.QUIT event
            if event.type == pygame.QUIT:
                return False

            # Handle UI actions from view
            ui_action = self.main_view.handle_event(event, self.show_settings, self.engine,
                                                    self.scale_factor)
            if ui_action:
                action = ui_action.get('action')
                if action in self.action_handlers:
                    result = self.action_handlers[action](ui_action)
                    # If a handler returned False explicitly, exit the game loop
                    if result is False:
                        return False
                        
            # Handle game restart on game over screen (touch anywhere)
            if event.type == pygame.MOUSEBUTTONDOWN and self.engine.game_over:
                self.restart_game()

        return True

    def render(self) -> None:
        """Render the view and engine state."""
        # Clear the window with a background color (black or another color from your palette)
        self.window.fill((0, 0, 0))
        
        # Create a scaled surface for the game area
        game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Render the game to this surface
        self.main_view.render(game_surface, self.engine, self.show_settings)
        
        # Scale the surface to fit the window width
        scaled_surface = pygame.transform.scale(game_surface, 
                                              (self.screen_width, self.scaled_height))
        
        # Calculate the position to center vertically (if needed)
        y_position = (self.screen_height - self.scaled_height) // 2 if self.screen_height > self.scaled_height else 0
        
        # Blit the scaled surface to the window
        self.window.blit(scaled_surface, (0, y_position))
        
        pygame.display.flip()

    def loop(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            # Update animations
            self.engine.update_animations()
            # render UI and game
            self.render()
        pygame.quit() 