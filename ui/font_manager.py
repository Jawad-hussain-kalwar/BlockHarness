# ui/font_manager.py
import os
import pygame

class FontManager:
    """Font manager to handle loading and caching fonts from the fonts directory."""
    
    def __init__(self):
        self.fonts = {}  # Cache for loaded fonts
        self.font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        
    def get_font(self, font_name, size):
        """Get a font by name and size.
        
        Args:
            font_name: Name of the font file without extension (e.g., 'Kanit-Regular')
            size: Font size in points
            
        Returns:
            pygame.font.Font object
        """
        # Create a cache key
        cache_key = f"{font_name}_{size}"
        
        # Check if font is already loaded
        if cache_key in self.fonts:
            return self.fonts[cache_key]
        
        # Load the font
        try:
            font_path = os.path.join(self.font_dir, f"{font_name}.ttf")
            font = pygame.font.Font(font_path, size)
            self.fonts[cache_key] = font
            return font
        except FileNotFoundError:
            print(f"Font file {font_name}.ttf not found, using system default")
            # Fall back to default font
            return pygame.font.SysFont('Arial', size)

# Global font manager instance
font_manager = FontManager() 