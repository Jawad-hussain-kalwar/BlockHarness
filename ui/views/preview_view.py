# ui/views/preview_view.py
import pygame
from ui.colours import BLACK, GRAY, WHITE, YELLOW, BLUE
from engine.block import Block
from typing import List, Tuple

class PreviewView:
    def __init__(self, preview_origin, preview_cell_size, preview_spacing):
        self.preview_origin = preview_origin
        self.preview_cell_size = preview_cell_size
        self.preview_spacing = preview_spacing
    
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
    
    def draw(self, surface, preview_blocks, selected_index):
        # Draw the preview blocks
        for i, (block, rotation) in enumerate(preview_blocks):
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
            pygame.draw.rect(surface, GRAY if i != selected_index else WHITE, preview_rect)
            pygame.draw.rect(surface, YELLOW if i == selected_index else BLACK, preview_rect, 2)
            
            # Draw block cells - using preview_cell_size
            for r, c in rotated_block.cells:
                cell_rect = pygame.Rect(
                    self.preview_origin[0] + offset_x + c * self.preview_cell_size,
                    self.preview_origin[1] + i * self.preview_spacing + offset_y + r * self.preview_cell_size,
                    self.preview_cell_size,
                    self.preview_cell_size
                )
                pygame.draw.rect(surface, BLUE, cell_rect)
                pygame.draw.rect(surface, BLACK, cell_rect, 1) 