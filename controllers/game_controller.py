# controllers/game_controller.py
import pygame
import time
from engine.game_engine import GameEngine
from engine.block import Block
from ui.views.board_view import BoardView
from ui.views.preview_view import PreviewView
from ui.views.sidebar_view import SidebarView
from ui.views.hud_view import HudView
from ui.views.overlay_view import OverlayView
from ui.colours import WHITE

class GameController:
    def __init__(self, config):
        # Initialize pygame
        pygame.init()
        self.window_size = (1100, 720)  # Increased width for left sidebar
        self.window = pygame.display.set_mode(self.window_size, pygame.HWSURFACE)
        pygame.display.set_caption("BlockHarness – Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 18)
        self.large_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 14)
        
        # Game state
        self.cell_size = 64
        self.preview_cell_size = 32  # Half size for preview blocks
        self.board_origin = (280, 16)  # Moved right to make space for left sidebar
        self.preview_origin = (280 + 8 * self.cell_size + 32, 16)
        self.preview_spacing = 160  # Spacing between preview blocks
        
        # Config
        self.config = config
        
        # Initialize views
        self.board_view = BoardView(self.board_origin, self.cell_size)
        self.preview_view = PreviewView(self.preview_origin, self.preview_cell_size, self.preview_spacing)
        self.sidebar_view = SidebarView(self.window_size, self.font, self.small_font)
        self.hud_view = HudView(self.preview_origin, self.preview_spacing, self.font)
        self.overlay_view = OverlayView(self.window_size, self.large_font, self.font)
        
        # Update sidebar fields from config
        self.sidebar_view.update_config_fields(self.config)
        
        # Initialize game engine
        self.restart_game(self.config)
    
    def restart_game(self, config):
        """Reset the game state with the given config."""
        self.engine = GameEngine(config)
        self.preview_blocks = []
        self.selected_index = None
        self.game_over = False
        
        # Generate initial three preview blocks
        self.refill_preview()
    
    def refill_preview(self):
        """Fill preview with blocks until we have three."""
        while len(self.preview_blocks) < 3:
            self.engine.spawn()
            self.preview_blocks.append((self.engine.current_block, 0))  # (block, rotation)
        
        # If no block is selected, select the first one
        if self.selected_index is None and len(self.preview_blocks) > 0:
            self.selected_index = 0
    
    def rotate_selected(self):
        """Rotate the selected block 90 degrees clockwise."""
        if self.selected_index is not None and 0 <= self.selected_index < len(self.preview_blocks):
            block, rotation = self.preview_blocks[self.selected_index]
            # Rotate 90 degrees clockwise by updating rotation value
            self.preview_blocks[self.selected_index] = (block, (rotation + 1) % 4)
    
    def apply_config_changes(self):
        """Apply changes from the sidebar config inputs."""
        new_config = self.sidebar_view.get_config_values()
        if new_config:
            # Update config
            self.config.update(new_config)
            
            # Restart game with new config
            self.restart_game(self.config)
            return True
        return False
    
    def handle_board_click(self, x, y):
        """Handle click on the game board to place a block."""
        board_width = 8 * self.cell_size
        board_height = 8 * self.cell_size
        board_rect = pygame.Rect(self.board_origin[0], self.board_origin[1], board_width, board_height)
        
        if board_rect.collidepoint(x, y) and self.selected_index is not None:
            # Calculate grid position
            grid_x = (x - self.board_origin[0]) // self.cell_size
            grid_y = (y - self.board_origin[1]) // self.cell_size
            
            # Get selected block and its rotation
            block, rotation = self.preview_blocks[self.selected_index]
            rotated_block = self.preview_view.get_block_with_rotation(block, rotation)
            
            # Try to place the block
            if self.engine.board.can_place(rotated_block, grid_y, grid_x):
                self.engine.current_block = rotated_block
                self.engine.place(grid_y, grid_x)
                
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
                return True
        return False
    
    def handle_preview_click(self, x, y):
        """Handle click on the preview area to select a block."""
        for i in range(min(3, len(self.preview_blocks))):
            preview_rect = pygame.Rect(
                self.preview_origin[0],
                self.preview_origin[1] + i * self.preview_spacing,
                self.preview_cell_size * 4,
                self.preview_cell_size * 4
            )
            if preview_rect.collidepoint(x, y):
                self.selected_index = i
                return True
        return False
    
    def handle_events(self):
        """Process user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle sidebar events
            action = self.sidebar_view.handle_event(event)
            if action == "apply":
                self.apply_config_changes()
            
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                elif event.key == pygame.K_F2:
                    self.restart_game(self.config)
                elif event.key == pygame.K_r and not self.game_over:
                    self.rotate_selected()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
        self.sidebar_view.draw(self.window, False, 0, 0)
        self.board_view.draw(self.window, self.engine)
        self.preview_view.draw(self.window, self.preview_blocks, self.selected_index)
        self.hud_view.draw(self.window, self.engine)
        
        # Draw game over overlay if needed
        if self.game_over:
            self.overlay_view.draw_game_over(self.window)
        
        pygame.display.flip()
    
    def loop(self):
        """Main game loop."""
        running = True
        while running:
            # Handle input events
            running = self.handle_events()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        pygame.quit() 