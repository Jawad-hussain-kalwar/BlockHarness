"""
Registry for AI player implementations using the generic Registry class.
This module provides a standard way to register and access AI player implementations.
"""
from typing import List, Tuple, Any, Type
from utils.registry import Registry
from ai.base_player import BaseAIPlayer


# Create a singleton instance using the generic Registry
class AIPlayerRegistry(Registry[BaseAIPlayer]):
    """AI Player registry that extends the generic Registry."""
    
    def __init__(self):
        """Initialize the AI player registry."""
        super().__init__(BaseAIPlayer)
        
        # Auto-discover is performed in _ensure_initialized() when needed
        
    def create_player(self, name: str) -> BaseAIPlayer:
        """Create an instance of an AI player by name (compatibility method).
        
        Args:
            name: The name of the AI player
            
        Returns:
            An instance of the AI player
            
        Raises:
            KeyError: If no AI player with the given name exists
        """
        return self.create(name)
    
    def get_available_players(self) -> List[Tuple[str, str]]:
        """Get a list of available AI players for UI display (compatibility method).
        
        Returns:
            List of (value, display_text) tuples for registered AI players
        """
        return self.get_available_components()
    
    # Override the register method to handle both classes and instances
    def register(self, component: Any) -> None:
        """Register an AI player class or instance.
        
        Args:
            component: AI player class or instance to register
        """
        if isinstance(component, type) and issubclass(component, BaseAIPlayer):
            # It's a class, instantiate it
            super().register(component)
        elif isinstance(component, BaseAIPlayer):
            # It's already an instance, get its class
            super().register(component.__class__)
        else:
            raise TypeError(f"Expected BaseAIPlayer class or instance, got {type(component)}")


# Create the singleton registry instance
registry = AIPlayerRegistry()

# Import players after registry creation to avoid circular imports
from ai.Greedy1 import Greedy1
from ai.Random import Random
from ai.EdgeHugging import EdgeHugging

# Register built-in AI player classes
registry.register(Greedy1)
registry.register(Random)
registry.register(EdgeHugging) 