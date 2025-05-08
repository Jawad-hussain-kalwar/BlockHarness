# ui/views/preview_view.py
import pygame
from ui.colours import  BLOCK_BG, BG_COLOR, YELLOW, CELL_COLOR, PREVIEW_BOX_BORDER

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
    
    def _render_block_background(self, surface, rect, is_selected):
        """Render the background and border for a preview block.
        
        Args:
            surface: Surface to render on
            rect: Rectangle for this preview block
            is_selected: Whether this block is currently selected
        """
        # Render block background
        bg_color = BG_COLOR if is_selected else BLOCK_BG
        border_color = YELLOW if is_selected else PREVIEW_BOX_BORDER
        
        pygame.draw.rect(surface, bg_color, rect)
        pygame.draw.rect(surface, border_color, rect, 2)
    
    def _calculate_block_dimensions(self, block):
        """Calculate maximum dimensions of a block.
        
        Args:
            block: Block to calculate dimensions for
            
        Returns:
            tuple: (max_width, max_height)
        """
        max_width = max(c for _, c in block.cells) + 1 if block.cells else 1
        max_height = max(r for r, _ in block.cells) + 1 if block.cells else 1
        return max_width, max_height
    
    def _render_block_cells(self, surface, block, offset_x, offset_y):
        """Render the individual cells of a block.
        
        Args:
            surface: Surface to render on
            block: Block to render
            offset_x: X offset for rendering
            offset_y: Y offset for rendering
        """
        for r, c in block.cells:
            cell_rect = pygame.Rect(
                offset_x + c * self.preview_cell_size,
                offset_y + r * self.preview_cell_size,
                self.preview_cell_size,
                self.preview_cell_size
            )
            pygame.draw.rect(surface, CELL_COLOR, cell_rect)
            pygame.draw.rect(surface, BG_COLOR, cell_rect, 1)
    
    def render(self, surface, preview_blocks, selected_index):
        """Render the preview blocks.
        
        Args:
            surface: Surface to render on
            preview_blocks: List of blocks to render
            selected_index: Index of the currently selected block
        """
        # Render the preview blocks
        for i, block in enumerate(preview_blocks):
            if i >= len(self.preview_rects):
                break
                
            preview_rect = self.preview_rects[i]
            is_selected = (i == selected_index)
            
            # Render background and selection highlight
            self._render_block_background(surface, preview_rect, is_selected)
            
            # Calculate block dimensions and centering offset
            max_width, max_height = self._calculate_block_dimensions(block)
            offset_x = preview_rect.x + (self.preview_block_size - max_width * self.preview_cell_size) // 2
            offset_y = preview_rect.y + (self.preview_block_size - max_height * self.preview_cell_size) // 2
            
            # Render the block cells
            self._render_block_cells(surface, block, offset_x, offset_y)