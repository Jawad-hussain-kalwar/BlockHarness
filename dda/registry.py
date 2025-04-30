from typing import Dict, List, Tuple, Type
from dda.base_dda import BaseDDAAlgorithm


class DDAlgorithmRegistry:
    """Registry for DDA algorithms."""
    
    _algorithms: Dict[str, Type[BaseDDAAlgorithm]] = {}
    
    @classmethod
    def register(cls, name: str, algorithm_cls: Type[BaseDDAAlgorithm]) -> None:
        """Register a DDA algorithm.
        
        Args:
            name: The name of the algorithm
            algorithm_cls: The algorithm class
        """
        cls._algorithms[name] = algorithm_cls
    
    @classmethod
    def create_algorithm(cls, name: str) -> BaseDDAAlgorithm:
        """Create an instance of a DDA algorithm.
        
        Args:
            name: The name of the algorithm to create
            
        Returns:
            An instance of the specified algorithm
            
        Raises:
            KeyError: If the algorithm is not registered
        """
        if name not in cls._algorithms:
            raise KeyError(f"DDA algorithm '{name}' not found")
        return cls._algorithms[name]()
    
    @classmethod
    def get_available_algorithms(cls) -> List[Tuple[str, str]]:
        """Get a list of available DDA algorithms.
        
        Returns:
            A list of (value, display_text) tuples for use in a dropdown menu
        """
        return [(name, cls._algorithms[name].display_name) 
                for name in sorted(cls._algorithms.keys())]


# Singleton instance
registry = DDAlgorithmRegistry() 