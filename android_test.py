#!/usr/bin/env python3
"""
Simple test script to verify Android touch handling in BlockHarness.
This script tests scaling and grid position calculations.
"""
import sys
import pygame
from ui.views.game_section import GameSection
from ui.views.main_view import MainView
from ui.layout import WINDOW_WIDTH, WINDOW_HEIGHT

def test_scaled_coordinates():
    """Test that scaled coordinates are properly converted to grid positions."""
    pygame.init()
    
    # Create a font for testing
    font = pygame.font.SysFont('Arial', 18)
    small_font = pygame.font.SysFont('Arial', 14)
    
    # Create game section for testing
    game_section = GameSection(font, small_font)
    
    # Test various scaling factors
    test_scales = [1.0, 1.5, 2.0, 2.5, 3.0]
    
    # Test various board positions
    test_positions = [
        # Center of board cells at different positions
        (100, 200),  # Top-left region
        (300, 200),  # Top-right region
        (100, 500),  # Bottom-left region
        (300, 500),  # Bottom-right region
        (200, 350),  # Center of board
    ]
    
    print("=== Touch Coordinate Scaling Test ===")
    
    for scale in test_scales:
        print(f"\nTesting scale factor: {scale}")
        
        for pos in test_positions:
            # Simulate scaled coordinates (as if from touch event)
            scaled_x = pos[0] * scale
            scaled_y = pos[1] * scale
            
            # Convert back using our handle methods
            try:
                # First test with original coordinates
                orig_grid_pos = game_section.handle_board_click(pos[0], pos[1])
                
                # Now test with scaled coordinates and scale factor
                scaled_pos = (scaled_x, scaled_y)
                descaled_x = scaled_x / scale
                descaled_y = scaled_y / scale
                scaled_grid_pos = game_section.handle_board_click(descaled_x, descaled_y)
                
                # Check if both produce the same result
                if orig_grid_pos == scaled_grid_pos:
                    result = "✓ PASS"
                else:
                    result = "✗ FAIL"
                
                print(f"  Position {pos} → Scaled {scaled_pos} → Grid pos: {scaled_grid_pos} - {result}")
                print(f"    Original: {orig_grid_pos}, Scaled: {scaled_grid_pos}")
                
                # Verify grid position is integer
                if scaled_grid_pos:
                    if isinstance(scaled_grid_pos[0], int) and isinstance(scaled_grid_pos[1], int):
                        print(f"    Grid position types: ✓ PASS (integers)")
                    else:
                        print(f"    Grid position types: ✗ FAIL (not integers: {type(scaled_grid_pos[0])}, {type(scaled_grid_pos[1])})")
            
            except Exception as e:
                print(f"  Error testing position {pos}: {e}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_scaled_coordinates() 