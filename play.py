# play.py
import sys
import json
import pygame
import argparse
from typing import List, Tuple, Optional

from engine.game_engine import GameEngine
from engine.block import Block
from shapes import SHAPES

# Default configuration (same as in simulator.py)
CONFIG = {
    "shapes": SHAPES,
    "shape_weights": [2, 2, 2, 2, 1, 1, 1, 1],           # initial bias
    "difficulty_thresholds": [
        (1000, [1, 2, 2, 2, 2, 2, 2, 3]),                # harder
        (3000, [1, 1, 2, 3, 3, 3, 3, 4]),                # hardest
    ],
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
BLUE = (100, 100, 255)
GREEN = (100, 200, 100)
OVERLAY = (0, 0, 0, 128)  # Semi-transparent overlay

# Input field states
class InputField:
    def __init__(self, rect, value, max_chars=20, numeric=False):
        self.rect = rect
        self.value = str(value)
        self.active = False
        self.max_chars = max_chars
        self.numeric = numeric
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.unicode.isprintable():
                if self.numeric and not (event.unicode.isdigit() or event.unicode == ','):
                    return
                if len(self.value) < self.max_chars:
                    self.value += event.unicode
    
    def draw(self, surface, font):
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 1)
        
        text_surf = font.render(self.value, True, BLACK)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(text_surf, text_rect)

class GameUI:
    def __init__(self):
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="BlockHarness - Pygame")
        parser.add_argument("--config", help="Path to config JSON file")
        args = parser.parse_args()
        
        # Load config
        self.config = CONFIG.copy()
        if args.config:
            try:
                with open(args.config, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
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
        
        # Create config input fields
        self.create_config_inputs()
        
        # Initialize game engine
        self.restart_game(self.config)

    def create_config_inputs(self):
        # Left sidebar coordinates
        left_x = 16
        top_y = 16
        field_width = 240
        field_height = 30
        section_gap = 20
        
        self.input_fields = []
        self.apply_button_rect = None
        
        # Initial weights section
        y = top_y
        
        # Label
        self.initial_weights_label = (left_x, y)
        y += 25
        
        # Initial weights input
        initial_weights = ",".join(map(str, self.config["shape_weights"]))
        initial_field_rect = pygame.Rect(left_x, y, field_width, field_height)
        self.initial_weights_field = InputField(initial_field_rect, initial_weights, 20)
        self.input_fields.append(self.initial_weights_field)
        y += field_height + 10
        
        # Threshold 1
        y += section_gap
        self.threshold1_label = (left_x, y)
        y += 25
        
        # Threshold 1 score
        threshold1_score = self.config["difficulty_thresholds"][0][0]
        threshold1_score_rect = pygame.Rect(left_x, y, field_width // 2 - 5, field_height)
        self.threshold1_score_field = InputField(threshold1_score_rect, threshold1_score, 5, numeric=True)
        self.input_fields.append(self.threshold1_score_field)
        
        # Threshold 1 weights
        threshold1_weights = ",".join(map(str, self.config["difficulty_thresholds"][0][1]))
        threshold1_weights_rect = pygame.Rect(left_x + field_width // 2 + 5, y, field_width // 2 - 5, field_height)
        self.threshold1_weights_field = InputField(threshold1_weights_rect, threshold1_weights, 20)
        self.input_fields.append(self.threshold1_weights_field)
        y += field_height + 10
        
        # Threshold 2
        y += section_gap
        self.threshold2_label = (left_x, y)
        y += 25
        
        # Threshold 2 score
        threshold2_score = self.config["difficulty_thresholds"][1][0]
        threshold2_score_rect = pygame.Rect(left_x, y, field_width // 2 - 5, field_height)
        self.threshold2_score_field = InputField(threshold2_score_rect, threshold2_score, 5, numeric=True)
        self.input_fields.append(self.threshold2_score_field)
        
        # Threshold 2 weights
        threshold2_weights = ",".join(map(str, self.config["difficulty_thresholds"][1][1]))
        threshold2_weights_rect = pygame.Rect(left_x + field_width // 2 + 5, y, field_width // 2 - 5, field_height)
        self.threshold2_weights_field = InputField(threshold2_weights_rect, threshold2_weights, 20)
        self.input_fields.append(self.threshold2_weights_field)
        y += field_height + 10
        
        # Apply button
        y += section_gap * 2
        self.apply_button_rect = pygame.Rect(left_x, y, field_width, field_height * 1.5)

    def apply_config_changes(self):
        try:
            # Parse initial weights
            initial_weights = list(map(int, self.initial_weights_field.value.split(',')))
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
            
            # Update config
            self.config["shape_weights"] = initial_weights
            self.config["difficulty_thresholds"] = [
                (threshold1_score, threshold1_weights),
                (threshold2_score, threshold2_weights)
            ]
            
            # Restart game with new config
            self.restart_game(self.config)
            return True
        except (ValueError, IndexError) as e:
            print(f"Config error: {e}")
            return False

    def restart_game(self, config):
        self.engine = GameEngine(config)
        self.preview_blocks = []
        self.selected_index = None
        self.game_over = False
        
        # Generate initial three preview blocks
        self.refill_preview()
    
    def refill_preview(self):
        # Fill preview with blocks until we have three
        while len(self.preview_blocks) < 3:
            self.engine.spawn()
            self.preview_blocks.append((self.engine.current_block, 0))  # (block, rotation)
        
        # If no block is selected, select the first one
        if self.selected_index is None and len(self.preview_blocks) > 0:
            self.selected_index = 0
    
    def rotate_selected(self):
        if self.selected_index is not None and 0 <= self.selected_index < len(self.preview_blocks):
            block, rotation = self.preview_blocks[self.selected_index]
            # Rotate 90 degrees clockwise by updating rotation value
            self.preview_blocks[self.selected_index] = (block, (rotation + 1) % 4)
    
    def get_rotated_cells(self, block: Block, rotation: int) -> List[Tuple[int, int]]:
        """Return rotated cell positions based on rotation (0-3)"""
        if rotation == 0:
            return block.cells
        
        rotated_cells = []
        for r, c in block.cells:
            if rotation == 1:  # 90 degrees clockwise
                rotated_cells.append((c, -r + block.height - 1))
            elif rotation == 2:  # 180 degrees
                rotated_cells.append((-r + block.height - 1, -c + block.width - 1))
            elif rotation == 3:  # 270 degrees clockwise
                rotated_cells.append((-c + block.width - 1, r))
                
        return rotated_cells
    
    def get_block_with_rotation(self, block: Block, rotation: int) -> Block:
        """Create a new block with rotated cells"""
        rotated_block = Block(self.get_rotated_cells(block, rotation))
        return rotated_block
    
    def main_loop(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Handle input field events
                for field in self.input_fields:
                    field.handle_event(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key == pygame.K_F2:
                        self.restart_game(self.engine.cfg)
                    elif event.key == pygame.K_r and not self.game_over:
                        self.rotate_selected()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    
                    # Check if apply button was clicked
                    if self.apply_button_rect and self.apply_button_rect.collidepoint(x, y):
                        self.apply_config_changes()
                    
                    # Don't process game clicks if game over
                    if self.game_over:
                        continue
                    
                    # Check if click is on the preview area - updated to use preview_cell_size
                    for i in range(min(3, len(self.preview_blocks))):
                        preview_rect = pygame.Rect(
                            self.preview_origin[0],
                            self.preview_origin[1] + i * self.preview_spacing,
                            self.preview_cell_size * 4,  # Use preview_cell_size
                            self.preview_cell_size * 4   # Use preview_cell_size
                        )
                        if preview_rect.collidepoint(x, y):
                            self.selected_index = i
                            break
                    
                    # Check if click is on the board area
                    board_width = 8 * self.cell_size
                    board_height = 8 * self.cell_size
                    board_rect = pygame.Rect(self.board_origin[0], self.board_origin[1], board_width, board_height)
                    
                    if board_rect.collidepoint(x, y) and self.selected_index is not None:
                        # Calculate grid position
                        grid_x = (x - self.board_origin[0]) // self.cell_size
                        grid_y = (y - self.board_origin[1]) // self.cell_size
                        
                        # Get selected block and its rotation
                        block, rotation = self.preview_blocks[self.selected_index]
                        rotated_block = self.get_block_with_rotation(block, rotation)
                        
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
            
            # Draw everything
            self.window.fill(WHITE)
            self._draw_config_sidebar()
            self._draw_board()
            self._draw_preview()
            self._draw_hud()
            
            # Draw game over overlay if needed
            if self.game_over:
                self._draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def _draw_config_sidebar(self):
        # Draw sidebar background
        sidebar_rect = pygame.Rect(0, 0, 260, self.window_size[1])
        pygame.draw.rect(self.window, LIGHT_GRAY, sidebar_rect)
        pygame.draw.line(self.window, BLACK, (260, 0), (260, self.window_size[1]), 1)
        
        # Draw initial weights label
        label = self.font.render("Initial Shape Weights (0-10):", True, BLACK)
        self.window.blit(label, self.initial_weights_label)
        
        # Draw threshold 1 label
        label = self.font.render("Difficulty Threshold 1:", True, BLACK)
        self.window.blit(label, self.threshold1_label)
        
        # Draw threshold 2 label
        label = self.font.render("Difficulty Threshold 2:", True, BLACK)
        self.window.blit(label, self.threshold2_label)
        
        # Draw threshold helper labels
        score_label = self.small_font.render("Score", True, DARK_GRAY)
        weights_label = self.small_font.render("Weights", True, DARK_GRAY)
        
        # Position labels UNDER the input fields (not above)
        self.window.blit(score_label, (self.threshold1_score_field.rect.x, self.threshold1_score_field.rect.y + self.threshold1_score_field.rect.height + 2))
        self.window.blit(weights_label, (self.threshold1_weights_field.rect.x, self.threshold1_weights_field.rect.y + self.threshold1_weights_field.rect.height + 2))
        
        self.window.blit(score_label, (self.threshold2_score_field.rect.x, self.threshold2_score_field.rect.y + self.threshold2_score_field.rect.height + 2))
        self.window.blit(weights_label, (self.threshold2_weights_field.rect.x, self.threshold2_weights_field.rect.y + self.threshold2_weights_field.rect.height + 2))
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(self.window, self.font)
        
        # Draw apply button
        if self.apply_button_rect:
            pygame.draw.rect(self.window, GREEN, self.apply_button_rect)
            pygame.draw.rect(self.window, BLACK, self.apply_button_rect, 1)
            
            apply_text = self.font.render("Apply Changes", True, BLACK)
            text_rect = apply_text.get_rect(center=self.apply_button_rect.center)
            self.window.blit(apply_text, text_rect)
    
    def _draw_board(self):
        # Draw the board outline
        board_rect = pygame.Rect(
            self.board_origin[0], 
            self.board_origin[1], 
            8 * self.cell_size, 
            8 * self.cell_size
        )
        pygame.draw.rect(self.window, BLACK, board_rect, 2)
        
        # Draw grid lines
        for i in range(9):
            # Vertical lines
            pygame.draw.line(
                self.window, 
                GRAY,
                (self.board_origin[0] + i * self.cell_size, self.board_origin[1]),
                (self.board_origin[0] + i * self.cell_size, self.board_origin[1] + 8 * self.cell_size)
            )
            # Horizontal lines
            pygame.draw.line(
                self.window,
                GRAY,
                (self.board_origin[0], self.board_origin[1] + i * self.cell_size),
                (self.board_origin[0] + 8 * self.cell_size, self.board_origin[1] + i * self.cell_size)
            )
        
        # Draw filled cells
        for r in range(8):
            for c in range(8):
                if self.engine.board.grid[r][c]:
                    cell_rect = pygame.Rect(
                        self.board_origin[0] + c * self.cell_size,
                        self.board_origin[1] + r * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(self.window, BLUE, cell_rect)
                    pygame.draw.rect(self.window, BLACK, cell_rect, 1)
    
    def _draw_preview(self):
        # Draw the preview blocks
        for i, (block, rotation) in enumerate(self.preview_blocks):
            rotated_block = self.get_block_with_rotation(block, rotation)
            
            # Calculate the max dimensions of the rotated block
            max_width = max(c for _, c in rotated_block.cells) + 1 if rotated_block.cells else 1
            max_height = max(r for r, _ in rotated_block.cells) + 1 if rotated_block.cells else 1
            
            # Calculate centering offset - using preview_cell_size instead of cell_size
            offset_x = (4 - max_width) * self.preview_cell_size // 2
            offset_y = (4 - max_height) * self.preview_cell_size // 2
            
            # Draw block background
            preview_rect = pygame.Rect(
                self.preview_origin[0],
                self.preview_origin[1] + i * self.preview_spacing,
                4 * self.preview_cell_size,  # Use preview_cell_size
                4 * self.preview_cell_size   # Use preview_cell_size
            )
            pygame.draw.rect(self.window, GRAY if i != self.selected_index else WHITE, preview_rect)
            pygame.draw.rect(self.window, YELLOW if i == self.selected_index else BLACK, preview_rect, 2)
            
            # Draw block cells - using preview_cell_size
            for r, c in rotated_block.cells:
                cell_rect = pygame.Rect(
                    self.preview_origin[0] + offset_x + c * self.preview_cell_size,
                    self.preview_origin[1] + i * self.preview_spacing + offset_y + r * self.preview_cell_size,
                    self.preview_cell_size,
                    self.preview_cell_size
                )
                pygame.draw.rect(self.window, BLUE, cell_rect)
                pygame.draw.rect(self.window, BLACK, cell_rect, 1)
    
    def _draw_hud(self):
        # Draw game stats - adjusted positioning based on new preview spacing
        stats_y = self.preview_origin[1] + 3 * self.preview_spacing + 32
        
        score_text = self.font.render(f"Score: {self.engine.score}", True, BLACK)
        self.window.blit(score_text, (self.preview_origin[0], stats_y))
        
        lines_text = self.font.render(f"Lines: {self.engine.lines}", True, BLACK)
        self.window.blit(lines_text, (self.preview_origin[0], stats_y + 24))
        
        blocks_text = self.font.render(f"Blocks: {self.engine.blocks_placed}", True, BLACK)
        self.window.blit(blocks_text, (self.preview_origin[0], stats_y + 48))
        
        # Draw hint text
        hint_y = stats_y + 100
        hint1 = self.font.render("Click preview to select", True, DARK_GRAY)
        hint2 = self.font.render("R = rotate", True, DARK_GRAY)
        hint3 = self.font.render("Esc = quit", True, DARK_GRAY)
        
        self.window.blit(hint1, (self.preview_origin[0], hint_y))
        self.window.blit(hint2, (self.preview_origin[0], hint_y + 24))
        self.window.blit(hint3, (self.preview_origin[0], hint_y + 48))
    
    def _draw_game_over(self):
        # Create overlay surface
        overlay = pygame.Surface((self.window_size[0], self.window_size[1]), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.window.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, WHITE)
        restart_text = self.font.render("F2 to restart", True, WHITE)
        
        text_x = (self.window_size[0] - game_over_text.get_width()) // 2
        text_y = (self.window_size[1] - game_over_text.get_height()) // 2
        
        self.window.blit(game_over_text, (text_x, text_y))
        self.window.blit(restart_text, (text_x + 50, text_y + 50))


if __name__ == "__main__":
    GameUI().main_loop() 