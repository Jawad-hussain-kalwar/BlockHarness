# ui/views/board_view.py
import pygame
from ui.colours import BLACK, GRAY, BLUE

class BoardView:
    def __init__(self, board_origin, cell_size):
        self.board_origin = board_origin
        self.cell_size = cell_size
    
    def draw(self, surface, engine):
        # Draw the board outline
        board_rect = pygame.Rect(
            self.board_origin[0], 
            self.board_origin[1], 
            8 * self.cell_size, 
            8 * self.cell_size
        )
        pygame.draw.rect(surface, BLACK, board_rect, 2)
        
        # Draw grid lines
        for i in range(9):
            # Vertical lines
            pygame.draw.line(
                surface, 
                GRAY,
                (self.board_origin[0] + i * self.cell_size, self.board_origin[1]),
                (self.board_origin[0] + i * self.cell_size, self.board_origin[1] + 8 * self.cell_size)
            )
            # Horizontal lines
            pygame.draw.line(
                surface,
                GRAY,
                (self.board_origin[0], self.board_origin[1] + i * self.cell_size),
                (self.board_origin[0] + 8 * self.cell_size, self.board_origin[1] + i * self.cell_size)
            )
        
        # Draw filled cells
        for r in range(8):
            for c in range(8):
                if engine.board.grid[r][c]:
                    cell_rect = pygame.Rect(
                        self.board_origin[0] + c * self.cell_size,
                        self.board_origin[1] + r * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(surface, BLUE, cell_rect)
                    pygame.draw.rect(surface, BLACK, cell_rect, 1) 