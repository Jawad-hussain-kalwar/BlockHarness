# ui/views/board_view.py
import pygame
from typing import Optional, Tuple
from ui.colours import FG_COLOR, BOARD_LINES, BLUE, CELL_BORDER
from ui.layout import BOARD_SIZE
from ui.debug import draw_debug_rect

class BoardView:
    def __init__(self, board_origin, cell_size, board_size=BOARD_SIZE):
        self.board_origin = board_origin
        self.cell_size = cell_size
        self.board_size = board_size
        self.board_cells = 8  # Number of cells in each dimension
        self.board_rect = pygame.Rect(
            board_origin[0],
            board_origin[1],
            self.board_cells * cell_size,
            self.board_cells * cell_size
        )
    
    def draw(self, surface, engine):
        
        # Draw debug border if enabled
        draw_debug_rect(surface, self.board_rect, "board")
        
        # Draw grid lines
        for i in range(self.board_cells + 1):
            # Vertical lines
            pygame.draw.line(
                surface, 
                BOARD_LINES,
                (self.board_origin[0] + i * self.cell_size, self.board_origin[1]),
                (self.board_origin[0] + i * self.cell_size, self.board_origin[1] + self.board_cells * self.cell_size)
            )
            # Horizontal lines
            pygame.draw.line(
                surface,
                BOARD_LINES,
                (self.board_origin[0], self.board_origin[1] + i * self.cell_size),
                (self.board_origin[0] + self.board_cells * self.cell_size, self.board_origin[1] + i * self.cell_size)
            )
        
        # Draw filled cells with support for animations
        for r in range(self.board_cells):
            for c in range(self.board_cells):
                if engine.board.grid[r][c]:
                    # Get cell opacity from engine animations (if being animated)
                    opacity = engine.get_cell_opacity(r, c)
                    
                    cell_rect = pygame.Rect(
                        self.board_origin[0] + c * self.cell_size,
                        self.board_origin[1] + r * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    
                    # Draw with opacity if the cell is being animated
                    if opacity is not None:
                        self._draw_cell_with_opacity(surface, cell_rect, BLUE, opacity)
                    else:
                        # Draw normal cell
                        pygame.draw.rect(surface, BLUE, cell_rect)
                        pygame.draw.rect(surface, CELL_BORDER, cell_rect, 1)
                    
    def _draw_cell_with_opacity(self, surface: pygame.Surface, rect: pygame.Rect, 
                               color: Tuple[int, int, int], opacity: float) -> None:
        """Draw a cell with the specified opacity.
        
        Args:
            surface: Surface to draw on
            rect: Rectangle to fill
            color: RGB color tuple
            opacity: Opacity value from 0.0 to 1.0
        """
        # Create a transparent surface for the cell
        cell_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Calculate the color with opacity
        opacity_int = max(0, min(255, int(opacity * 255)))
        transparent_color = (*color, opacity_int)  # RGBA
        
        # Fill the temporary surface and draw border
        cell_surface.fill(transparent_color)
        pygame.draw.rect(cell_surface, (*CELL_BORDER, opacity_int), 
                        pygame.Rect(0, 0, rect.width, rect.height), 1)
        
        # Blit the cell surface onto the main surface
        surface.blit(cell_surface, rect) 