# controllers/simulation_controller.py
import time
import pygame
from typing import Dict, Tuple, List

from controllers.game_controller import GameController 
from controllers.ai_controller import AIController
from ui.colours import BG_COLOR
from ai.registry import registry as ai_registry
from dda.registry import registry as dda_registry
from data.stats_manager import StatsManager


class SimulationStatsManager:
    """Manages statistics for simulation runs"""
    
    def __init__(self):
        """Initialize the simulation stats manager"""
        self.stats_manager = StatsManager()
        self.simulation_stats = []
    
    def add_run_stats(self, run_stats: Dict, ai_player_name: str) -> None:
        """Add statistics for a simulation run.
        
        Args:
            run_stats: Dictionary with run statistics
            ai_player_name: Name of the AI player used
        """
        stats = {
            'score': run_stats['score'],
            'lines': run_stats['lines'],
            'blocks_placed': run_stats['blocks_placed'],
            'ai_player': ai_player_name
        }
        self.simulation_stats.append(stats)
        self.save_stats(stats)
    
    def save_stats(self, stats: Dict) -> None:
        """Save simulation statistics to CSV.
        
        Args:
            stats: Statistics dictionary to save
        """
        self.stats_manager.save_stats(stats)
    
    def clear_stats(self) -> None:
        """Clear all simulation statistics"""
        self.simulation_stats = []
    
    def get_stats_summary(self) -> Dict:
        """Get a summary of simulation statistics.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.simulation_stats:
            return {
                'avg_score': 0,
                'avg_lines': 0,
                'avg_blocks': 0,
                'runs': 0
            }
        
        total_score = sum(s['score'] for s in self.simulation_stats)
        total_lines = sum(s['lines'] for s in self.simulation_stats)
        total_blocks = sum(s['blocks_placed'] for s in self.simulation_stats)
        runs = len(self.simulation_stats)
        
        return {
            'avg_score': total_score / runs,
            'avg_lines': total_lines / runs,
            'avg_blocks': total_blocks / runs,
            'runs': runs
        }


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
        self.steps_per_second = 1
        self.last_simulation_step = 0
        
        # Initialize simulation stats manager
        self.simulation_stats_manager = SimulationStatsManager()
        
        # Store the default animation duration
        self.default_animation_duration = self.engine.animation_duration_ms
        
        # Initialize the AI player dropdown with available AI players
        self.main_view.update_ai_player_dropdown(self.get_available_ai_players())
        
        # Initialize the DDA algorithm dropdown with available algorithms
        self.main_view.update_dda_algorithm_dropdown(self.get_available_dda_algorithms())
    
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
            # Get simulation parameters from main view
            simulation_values = self.main_view.get_simulation_values()
            if simulation_values:
                self.steps_per_second, self.simulation_runs, ai_player_name = simulation_values
                
                # Set the AI player if one was selected
                if ai_player_name:
                    self.ai_controller.set_ai_player(ai_player_name)
                
                self.simulation_running = True
                self.current_run = 0
                self.last_simulation_step = time.time()
                self.simulation_stats_manager.clear_stats()
                
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
    
    def get_available_ai_players(self):
        """Get a list of available AI players.
        
        Returns:
            A list of (value, display_text) tuples for use in a dropdown menu
        """
        return ai_registry.get_available_players()
    
    def get_available_dda_algorithms(self):
        """Get a list of available DDA algorithms.
        
        Returns:
            A list of (value, display_text) tuples for use in a dropdown menu
        """
        return dda_registry.get_available_algorithms()
    
    def apply_config_changes(self):
        """Apply configuration changes from the main view."""
        # Get config values from main view
        new_config = self.main_view.get_config_values()
        if new_config:
            # Update config
            self.config.update(new_config)
            
            # Update engine config
            self.reset_engine(preserve_config=True)
            
            print("Applied configuration changes")
            return True
        return False
    
    def _handle_simulation_sidebar_actions(self, ui_action: Dict) -> None:
        """Handle simulation-specific sidebar actions."""
        action = ui_action.get("action")
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
            
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                self.window_size = (event.w, event.h)
                self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
                # Update the main_view with the new window size
                self.main_view.handle_resize(self.window_size)
                self.main_view.update_config_fields(self.config)
            
            # Handle main view events with simulation-specific actions first
            ui_action = self.main_view.handle_event(event)
            if ui_action:
                action = ui_action.get("action")
                if action in ["simulate", "abort", "apply"]:
                    self._handle_simulation_sidebar_actions(ui_action)
                elif not self.simulation_running:
                    # Handle standard game actions only if not in simulation mode
                    if action == "restart":
                        self.restart_game()
                    elif action == "select_block" and not self.engine.game_over:
                        self.handle_preview_click(ui_action.get("index"))
                    elif action == "place_block" and not self.engine.game_over:
                        self.handle_board_click(ui_action.get("position"))
            
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
                elif event.key == pygame.K_RETURN and self.engine.game_over:
                    self.restart_game()
        
        return True
    
    def draw(self) -> None:
        """Render the game state with simulation information to the screen."""
        self._draw_core(self.simulation_running, self.current_run, self.simulation_runs)
    
    def _simulation_step_handler(self) -> None:
        """Handle simulation steps with the appropriate timing."""
        # Only run simulation if it's active
        if self.simulation_running:
            # Check if current run's game is over - start next run if so
            if self.engine.game_over:
                # Save stats for this run
                run_stats = {
                    'score': self.engine.score,
                    'lines': self.engine.lines,
                    'blocks_placed': self.engine.blocks_placed
                }
                self.simulation_stats_manager.add_run_stats(run_stats, self.ai_controller.get_ai_player_name())
                
                # Move to next run or end simulation
                self.current_run += 1
                if self.current_run >= self.simulation_runs:
                    # End of simulation
                    self.abort_simulation()
                    # Restart the game for manual play
                    self.restart_game()
                else:
                    # Start next run
                    self.restart_simulation()
                
                # Reset simulation timer for new run
                self.last_simulation_step = time.time()
                return
            
            # Check if it's time for another simulation step
            current_time = time.time()
            if self.steps_per_second == 0 or current_time - self.last_simulation_step >= 1.0 / self.steps_per_second:
                # Run a simulation step
                self.run_simulation_step()
                
                # Update the last step time
                self.last_simulation_step = current_time
    
    def loop(self):
        """Main game loop with simulation support."""
        self._loop_core(self._simulation_step_handler) 