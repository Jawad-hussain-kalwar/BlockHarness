from typing import List, Tuple

from utils.registry import Registry
from dda.base_dda import BaseDDAAlgorithm


class DDAlgorithmRegistry(Registry[BaseDDAAlgorithm]):
    """Registry for DDA algorithms."""
    
    def __init__(self):
        """Initialize the DDA algorithm registry."""
        super().__init__(BaseDDAAlgorithm)
    
    def create_algorithm(self, name: str) -> BaseDDAAlgorithm:
        """Create an instance of a DDA algorithm.
        
        Args:
            name: The name of the algorithm to create
            
        Returns:
            An instance of the specified algorithm
            
        Raises:
            KeyError: If the algorithm is not registered
        """
        return self.create(name)
    
    def get_available_algorithms(self) -> List[Tuple[str, str]]:
        """Get a list of available DDA algorithms.
        
        Returns:
            A list of (value, display_text) tuples for use in a dropdown menu
        """
        return self.get_available_components()


# Singleton instance
registry = DDAlgorithmRegistry() 