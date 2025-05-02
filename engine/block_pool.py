# engine/block_pool.py
import random
from engine.block import Block


class BlockPool:
    """Weighted random generator for shapes."""

    def __init__(self, shapes, weights):
        self.shapes = shapes
        self.weights = weights

    def sample(self) -> Block:
        shape = random.choices(self.shapes, weights=self.weights, k=1)[0]
        return Block(shape)
        
    def get_block(self) -> Block:
        """Get a block based on the current weights.
        
        Returns:
            Block: A new block with randomly selected shape
        """
        return self.sample()
