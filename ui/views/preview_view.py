# ui/views/preview_view.py
import pygame
from ui.colours import FG_COLOR, BLOCK_BG, BG_COLOR, YELLOW, CELL_COLOR, PREVIEW_BOX_BORDER, CELL_BORDER
from ui.layout import PREVIEW_CELL_RADIUS
from engine.block import Block
from typing import List, Tuple
from ui.debug import draw_debug_rect

class PreviewView:
    def __init__(self, preview_origin, preview_cell_size, preview_block_size, padding_h, padding_v, gap):
        self.preview_origin = preview_origin
        self.preview_cell_size = preview_cell_size
        self.preview_block_size = preview_block_size
        self.padding_h = padding_h
        self.padding_v = padding_v
        self.gap = gap
        
        # Create rectangles for each preview block
        self.preview_rects = []
        
        # First block
        x1 = preview_origin[0] + padding_h
        y1 = preview_origin[1] + padding_v
        self.preview_rects.append(pygame.Rect(x1, y1, preview_block_size, preview_block_size))
        
        # Second block
        x2 = x1 + preview_block_size + gap
        y2 = y1
        self.preview_rects.append(pygame.Rect(x2, y2, preview_block_size, preview_block_size))
        
        # Third block
        x3 = x2 + preview_block_size + gap
        y3 = y1
        self.preview_rects.append(pygame.Rect(x3, y3, preview_block_size, preview_block_size))
    
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
            if i >= len(self.preview_rects):
                break
                
            preview_rect = self.preview_rects[i]
            
            # Draw debug border if enabled
            draw_debug_rect(surface, preview_rect, "preview")
            
            rotated_block = self.get_block_with_rotation(block, rotation)
            
            # Calculate the max dimensions of the rotated block
            max_width = max(c for _, c in rotated_block.cells) + 1 if rotated_block.cells else 1
            max_height = max(r for r, _ in rotated_block.cells) + 1 if rotated_block.cells else 1
            
            # Calculate centering offset
            offset_x = preview_rect.x + (self.preview_block_size - max_width * self.preview_cell_size) // 2
            offset_y = preview_rect.y + (self.preview_block_size - max_height * self.preview_cell_size) // 2
            
            # Draw block background
            pygame.draw.rect(surface, BLOCK_BG if i != selected_index else BG_COLOR, preview_rect)
            # Draw block border
            pygame.draw.rect(surface, YELLOW if i == selected_index else PREVIEW_BOX_BORDER, preview_rect, 2)
            
            # Draw block cells
            for r, c in rotated_block.cells:
                cell_rect = pygame.Rect(
                    offset_x + c * self.preview_cell_size,
                    offset_y + r * self.preview_cell_size,
                    self.preview_cell_size,
                    self.preview_cell_size
                )
                pygame.draw.rect(surface, CELL_COLOR, cell_rect)
                pygame.draw.rect(surface, BG_COLOR, cell_rect, 1)