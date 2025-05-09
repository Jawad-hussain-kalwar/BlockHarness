# BlockHarness/engine/game_controller.py
import pygame
import ctypes
import sys
import os
from typing import Optional, Dict, Any, cast

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

        # Setup fixed window size
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        
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
        
        # Keyboard event mapping
        self.key_handlers = {
            pygame.K_ESCAPE: self._on_quit,
            pygame.K_q: self._on_quit,
            pygame.K_F2: self.restart_game,
            pygame.K_s: self._toggle_settings_popup,
            pygame.K_RETURN: self._on_return_key,
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

    def _toggle_settings_popup(self) -> None:
        """Toggle the visibility of the settings popup."""
        self.show_settings = not self.show_settings
        
    def _close_settings_popup(self) -> None:
        """Close the settings popup."""
        self.show_settings = False
        
    def _on_quit(self) -> bool:
        """Handle quit event."""
        return False  # Return False to exit the game loop
        
    def _on_return_key(self) -> None:
        """Handle Enter key press."""
        if self.engine.game_over:
            self.restart_game()

    def handle_events(self) -> bool:
        """Process Pygame events and UI actions."""
        for event in pygame.event.get():
            # Handle pygame.QUIT event
            if event.type == pygame.QUIT:
                return False

            # Handle UI actions from view
            ui_action = self.main_view.handle_event(event, self.show_settings, self.engine)
            if ui_action:
                action = ui_action.get('action')
                if action in self.action_handlers:
                    result = self.action_handlers[action](ui_action)
                    # If a handler returned False explicitly, exit the game loop
                    if result is False:
                        return False

            # Handle keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_handlers:
                    result = self.key_handlers[event.key]()
                    # If a handler returned False explicitly, exit the game loop
                    if result is False:
                        return False

        return True

    def render(self) -> None:
        """Render the view and engine state."""
        self.main_view.render(self.window, self.engine, self.show_settings)
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