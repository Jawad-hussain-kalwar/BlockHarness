# controllers/simulation_controller.py
import time
import pygame
from typing import Dict, Tuple

from controllers.game_controller import GameController 
from controllers.ai_controller import AIController
from ui.colours import WHITE
from ai.registry import registry


class SimulationController(GameController):
    """Controller that adds simulation capabilities to the game controller."""
    
    def __init__(self, config: Dict):
        # Initialize the game controller
        super().__init__(config)
        
        # Simulation state
        self.ai_controller = AIController(config)
        self.simulation_running = False
        self.simulation_runs = 0
        self.current_run = 0
        self.steps_per_second = 0
        self.last_simulation_step = 0
        self.simulation_stats = []
        
        # Store the default animation duration
        self.default_animation_duration = self.engine.animation_duration_ms
        
        # Initialize the AI player dropdown with available AI players
        self.sidebar_view.update_ai_player_dropdown(self.get_available_ai_players())
    
    def restart_simulation(self):
        """Restart the game but preserve simulation state variables"""
        # Reset AI controller
        self.ai_controller.reset_engine()
        
        # Ensure AI controller's engine has animation duration set to 0
        self.ai_controller.engine.animation_duration_ms = 0
        
        # Reset game controller engine
        self.reset_engine(preserve_config=True)
        
        # Disable animations for simulation runs
        self.engine.animation_duration_ms = 0
        
        # Sync the engines (they should be identical)
        print(f"Restarting simulation run {self.current_run + 1}/{self.simulation_runs}")
    
    def start_simulation(self):
        """Start the AI simulation at the specified steps per second"""
        if not self.simulation_running:
            # Get simulation parameters from sidebar
            simulation_values = self.sidebar_view.get_simulation_values()
            if simulation_values:
                self.steps_per_second, self.simulation_runs, ai_player_name = simulation_values
                
                # Set the AI player if one was selected
                if ai_player_name:
                    self.ai_controller.set_ai_player(ai_player_name)
                
                self.simulation_running = True
                self.current_run = 0
                self.last_simulation_step = time.time()
                self.simulation_stats = []
                
                # Set animation duration to 0 for instant line clears in simulation mode
                self.engine.animation_duration_ms = 0
                # Also set it in the AI controller's engine
                self.ai_controller.engine.animation_duration_ms = 0
                
                # If game was over, restart first run
                if self.engine.game_over:
                    self.restart_simulation()
    
    def abort_simulation(self):
        """Stop the AI simulation and allow manual play"""
        self.simulation_running = False
        self.current_run = 0  # Reset run count when aborting simulation
        
        # Restore normal animation duration when exiting simulation mode
        self.engine.animation_duration_ms = self.default_animation_duration
    
    def run_simulation_step(self):
        """Execute one AI step in the simulation"""
        # Make sure AI engine has animation duration set to 0
        self.ai_controller.engine.animation_duration_ms = 0
        
        # Use AI controller to make a move
        step_result = self.ai_controller.step()
        
        # Sync game state to our display engine
        if step_result:
            # Ensure existing animations are completed first
            if self.engine.is_animating():
                self.engine.update_animations()
                
            # Copy the game state from the AI engine to our display engine
            self.engine = self.ai_controller.engine
            
            # Ensure animation duration is set to 0 in the copied engine
            self.engine.animation_duration_ms = 0
            print(f"Applied AI step - engine animation duration: {self.engine.animation_duration_ms}")
    
    def save_simulation_stats(self, run_stats: Dict) -> None:
        """Save simulation run statistics to CSV."""
        stats = {
            'score': run_stats['score'],
            'lines': run_stats['lines'],
            'blocks_placed': run_stats['blocks_placed'],
            'ai_player': self.ai_controller.get_ai_player_name()
        }
        self.stats_manager.save_stats(stats)
    
    def get_available_ai_players(self):
        """Get a list of available AI players.
        
        Returns:
            A list of (value, display_text) tuples for use in a dropdown menu
        """
        return registry.get_available_players()
    
    def _handle_simulation_sidebar_actions(self, action: str) -> None:
        """Handle simulation-specific sidebar actions."""
        if action == "apply":
            self.apply_config_changes()
            # Also update AI controller config
            self.ai_controller.update_config(self.config)
            # Store updated animation duration if it has changed
            self.default_animation_duration = self.engine.animation_duration_ms
        elif action == "simulate":
            self.start_simulation()
        elif action == "abort":
            self.abort_simulation()
    
    def handle_events(self) -> bool:
        """Process user input events with simulation-specific handling."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle sidebar events with simulation-specific actions first
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                action = self.sidebar_view.handle_event(event)
                if action:
                    self._handle_simulation_sidebar_actions(action)
                    if action in ["simulate", "abort"]:  # These are simulation-specific
                        continue
            
            # Handle F2 differently to abort simulation
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                self.restart_game()
                # Also abort simulation if running
                if self.simulation_running:
                    self.simulation_running = False
                continue
            
            # Only allow certain inputs when not in simulation mode
            if self.simulation_running:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                # Skip other inputs during simulation
                continue
            
            # Handle other keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                elif event.key == pygame.K_r and not self.engine.game_over:
                    self.rotate_block()
                elif event.key == pygame.K_RETURN and self.engine.game_over:
                    self.restart_game()
            
            # Handle mouse events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                
                # Handle restart button click
                if self.engine.game_over and self.overlay_view.is_restart_button_clicked((x, y)):
                    self.restart_game()
                    continue
                
                # Skip gameplay clicks if game over
                if self.engine.game_over:
                    continue
                
                # Handle gameplay mouse events
                self.handle_preview_click(x, y)
                self.handle_board_click(x, y)
        
        return True
    
    def draw(self):
        """Render the game state to the screen."""
        self._draw_core(self.simulation_running, self.current_run, self.simulation_runs)
    
    def _simulation_step_handler(self):
        """Custom step handler for simulation logic."""
        current_time = time.time()
        
        # Run simulation step if active
        if self.simulation_running:
            # First, make sure any pending animations complete (should be instant with duration=0)
            if self.engine.is_animating():
                # Print animation state for debugging
                print(f"Animation in progress: duration={self.engine.animation_duration_ms}, " +
                     f"count={len(self.engine.animation_manager.animations)}")
                self.engine.update_animations()
            
            if self.ai_controller.engine.game_over:
                # Collect stats for this run
                run_stats = self.ai_controller.get_game_state()
                self.simulation_stats.append(run_stats)
                
                # Save simulation stats to CSV
                self.save_simulation_stats(run_stats)
                
                # Auto-restart for next simulation run
                self.current_run += 1
                if self.current_run < self.simulation_runs:
                    self.restart_simulation()
                else:
                    self.simulation_running = False
                    self.current_run = 0  # Reset run count when simulation completes
                    # Restore normal animation duration
                    self.engine.animation_duration_ms = self.default_animation_duration
                    # TODO: Display simulation results
                    print(f"Completed {self.simulation_runs} simulation runs")
                    for i, stats in enumerate(self.simulation_stats):
                        print(f"Run {i+1}: Score={stats['score']}, Lines={stats['lines']}, Blocks={stats['blocks_placed']}")
            elif self.steps_per_second == 0 or current_time - self.last_simulation_step >= 1.0 / self.steps_per_second:
                self.run_simulation_step()
                self.last_simulation_step = current_time
    
    def loop(self):
        """Main game loop with simulation support."""
        self._loop_core(self._simulation_step_handler) 