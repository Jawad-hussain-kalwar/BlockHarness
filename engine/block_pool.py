# engine/block_pool.py
import random
from typing import Dict, List, Tuple, Any
from engine.block import Block


class BlockPool:
    """Weighted random generator for shapes."""

    def __init__(self, shapes: Dict[str, List[Tuple[int, int]]], weights: List[int]):
        """Initialize the block pool with shapes and weights.
        
        Args:
            shapes: Dictionary of shape definitions mapped by name
            weights: List of weights for each shape (should match order of shapes.keys())
        """
        self.shapes = shapes
        self.shape_names = list(shapes.keys())
        
        # Adjust weights list length if needed
        if len(weights) < len(self.shape_names):
            # Extend with zeros if too short
            self.weights = weights + [0] * (len(self.shape_names) - len(weights))
        elif len(weights) > len(self.shape_names):
            # Truncate if too long
            self.weights = weights[:len(self.shape_names)]
        else:
            self.weights = weights
            
        # Ensure at least one shape has a non-zero weight to avoid ValueError in random.choices
        if not any(self.weights) and self.shape_names:
            # If all weights are zero, set uniform weights
            self.weights = [1] * len(self.shape_names)

    def sample(self) -> Block:
        """Sample a random block based on shape weights.
        
        Returns:
            Block: A new block with randomly selected shape
        """
        if not self.shape_names:
            raise ValueError("No shapes available in the block pool")
            
        try:
            shape_name = random.choices(self.shape_names, weights=self.weights, k=1)[0]
        except (ValueError, KeyError) as e:
            # Fallback to uniform selection if weights cause an error
            print(f"Warning: Error in weighted selection ({e}), falling back to uniform selection")
            shape_name = random.choice(self.shape_names)
            
        shape = self.shapes[shape_name]
        return Block(shape)
        
    def get_block(self) -> Block:
        """Get a block based on the current weights.
        
        Returns:
            Block: A new block with randomly selected shape
        """
        return self.sample()

    def update_weights(self, new_weights: List[int]) -> None:
        """Update the weights used for block selection.
        
        Args:
            new_weights: New weights list
        """
        # Store original weights
        original_weights = self.weights.copy()
        
        # Try to apply new weights
        try:
            # Adjust weights list length if needed
            if len(new_weights) < len(self.shape_names):
                # Extend with zeros if too short
                self.weights = new_weights + [0] * (len(self.shape_names) - len(new_weights))
            elif len(new_weights) > len(self.shape_names):
                # Truncate if too long
                self.weights = new_weights[:len(self.shape_names)]
            else:
                self.weights = new_weights
                
            # Ensure at least one shape has a non-zero weight
            if not any(self.weights) and self.shape_names:
                # If all weights are zero, set uniform weights
                self.weights = [1] * len(self.shape_names)
                
            # Verify the weights work by testing them
            if self.shape_names:
                random.choices(self.shape_names, weights=self.weights, k=1)
        except Exception as e:
            # Restore original weights if there's an error
            print(f"Warning: Error updating weights ({e}), keeping original weights")
            self.weights = original_weights
