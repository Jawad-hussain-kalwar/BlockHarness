"""
Registry for DDA algorithms with standardized initialization.
"""
from typing import List, Tuple, Dict, Optional, Any, Type

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
    
    def create_and_initialize_algorithm(self, name: str, config_params: Dict[str, Any]) -> BaseDDAAlgorithm:
        """Create and initialize a DDA algorithm with the provided configuration.
        
        This factory method ensures consistent initialization of DDA algorithms.
        
        Args:
            name: The name of the algorithm to create
            config_params: Configuration parameters for the algorithm
            
        Returns:
            An initialized instance of the specified algorithm
            
        Raises:
            KeyError: If the algorithm is not registered
        """
        # Create the algorithm instance
        algorithm = self.create(name)
        
        # Initialize it with the provided configuration
        algorithm.initialize(config_params)
        
        return algorithm
    
    def get_available_algorithms(self) -> List[Tuple[str, str]]:
        """Get a list of available DDA algorithms.
        
        Returns:
            A list of (value, display_text) tuples for use in a dropdown menu
        """
        return self.get_available_components()
    
    # Override the register method to handle both classes and instances
    def register(self, component: Any) -> None:
        """Register a DDA algorithm class or instance.
        
        Args:
            component: DDA algorithm class or instance to register
        """
        if isinstance(component, type) and issubclass(component, BaseDDAAlgorithm):
            # It's a class, register it directly
            super().register(component)
        elif isinstance(component, BaseDDAAlgorithm):
            # It's already an instance, get its class
            super().register(component.__class__)
        else:
            raise TypeError(f"Expected BaseDDAAlgorithm class or instance, got {type(component)}")


# Singleton instance
registry = DDAlgorithmRegistry() 