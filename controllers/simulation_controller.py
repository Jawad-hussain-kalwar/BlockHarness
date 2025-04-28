# controllers/simulation_controller.py
import time
import pygame
from engine.ai_player import AIPlayer
from engine.game_engine import GameEngine
from controllers.game_controller import GameController
from ui.colours import WHITE

class SimulationController(GameController):
    def __init__(self, config):
        super().__init__(config)
        
        # Simulation state
        self.ai_player = AIPlayer()
        self.simulation_running = False
        self.simulation_runs = 0
        self.current_run = 0
        self.steps_per_second = 1.0
        self.last_simulation_step = 0
    
    def restart_simulation(self):
        """Restart the game but preserve simulation state variables"""
        self.engine = GameEngine(self.config)
        self.preview_blocks = []
        self.selected_index = None
        self.game_over = False
        
        # Generate initial three preview blocks
        self.refill_preview()
        
        # Don't reset simulation status variables
        print(f"Restarting simulation run {self.current_run + 1}/{self.simulation_runs}")
    
    def start_simulation(self):
        """Start the AI simulation at the specified steps per second"""
        if not self.simulation_running:
            # Get simulation parameters from sidebar
            self.steps_per_second, self.simulation_runs = self.sidebar_view.get_simulation_values()
            
            self.simulation_running = True
            self.current_run = 0
            self.last_simulation_step = time.time()
            
            # Initialize AI player if not already done
            if not self.ai_player:
                self.ai_player = AIPlayer()
            
            # If game was over, restart first run
            if self.game_over:
                self.restart_simulation()
    
    def abort_simulation(self):
        """Stop the AI simulation and allow manual play"""
        self.simulation_running = False
    
    def run_simulation_step(self):
        """Execute one AI step in the simulation"""
        # If no preview blocks, refill
        if not self.preview_blocks:
            self.refill_preview()
            self.selected_index = 0
        
        # Choose a move using the AI
        if self.selected_index is not None:
            # Get the selected block and rotation
            block, rotation = self.preview_blocks[self.selected_index]
            rotated_block = self.preview_view.get_block_with_rotation(block, rotation)
            
            # Set as current block so AI can use it
            self.engine.current_block = rotated_block
            
            # Get AI's move
            move = self.ai_player.choose(self.engine)
            
            if move:
                row, col = move
                
                # Place the block
                if self.engine.board.can_place(rotated_block, row, col):
                    self.engine.place(row, col)
                    
                    # Remove the placed block from preview
                    self.preview_blocks.pop(self.selected_index)
                    
                    # Update selected index or reset if none left
                    if not self.preview_blocks:
                        self.selected_index = None
                        self.refill_preview()
                    else:
                        self.selected_index = min(self.selected_index, len(self.preview_blocks) - 1)
                    
                    # Check for game over
                    self.game_over = self.engine.no_move_left()
            else:
                # If AI can't find a move, consider it game over
                self.game_over = True
    
    def handle_events(self):
        """Process user input events with simulation handling."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle sidebar events
            action = self.sidebar_view.handle_event(event)
            if action == "apply":
                self.apply_config_changes()
            elif action == "simulate":
                self.start_simulation()
            elif action == "abort":
                self.abort_simulation()
            
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                elif event.key == pygame.K_F2:
                    self.restart_game(self.config)
                    # Stop simulation if running
                    self.simulation_running = False
                elif event.key == pygame.K_r and not self.game_over and not self.simulation_running:
                    self.rotate_selected()
            
            # Only process mouse click events if not in simulation
            if not self.simulation_running and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                
                # Don't process game clicks if game over
                if self.game_over:
                    continue
                
                # Check if click is on the preview area
                self.handle_preview_click(x, y)
                
                # Check if click is on the board area
                self.handle_board_click(x, y)
        
        return True
    
    def draw(self):
        """Render the game state to the screen."""
        self.window.fill(WHITE)
        
        # Draw all views
        self.sidebar_view.draw(self.window, self.simulation_running, self.current_run, self.simulation_runs)
        self.board_view.draw(self.window, self.engine)
        self.preview_view.draw(self.window, self.preview_blocks, self.selected_index)
        self.hud_view.draw(self.window, self.engine)
        
        # Draw game over overlay if needed but not during simulation
        if self.game_over and not self.simulation_running:
            self.overlay_view.draw_game_over(self.window)
        
        pygame.display.flip()
    
    def loop(self):
        """Main game loop with simulation support."""
        running = True
        while running:
            current_time = time.time()
            
            # Handle input events
            running = self.handle_events()
            
            # Run simulation step if active
            if self.simulation_running:
                if self.game_over:
                    # Auto-restart for next simulation run
                    self.current_run += 1
                    if self.current_run < self.simulation_runs:
                        self.restart_simulation()  # Use specialized restart that preserves simulation state
                    else:
                        self.simulation_running = False
                elif current_time - self.last_simulation_step >= 1.0 / self.steps_per_second:
                    self.run_simulation_step()
                    self.last_simulation_step = current_time
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit() 