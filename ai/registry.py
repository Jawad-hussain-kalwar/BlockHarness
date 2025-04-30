import importlib
import inspect
import os
import sys
from typing import Dict, List, Type, Tuple

from ai.base_player import BaseAIPlayer


class AIPlayerRegistry:
    """Registry for AI player implementations.
    
    This class provides a way to discover and register all available AI player
    implementations in the ai directory.
    """
    
    def __init__(self):
        """Initialize the AI player registry."""
        self._player_classes: Dict[str, Type[BaseAIPlayer]] = {}
        self._initialized = False
    
    def _discover_player_classes(self) -> None:
        """Discover all AI player classes in the ai directory."""
        # Get the directory of the ai module
        ai_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get all Python files in the ai directory
        for filename in os.listdir(ai_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base_player.py', 'registry.py']:
                # Import the module
                module_name = f"ai.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find classes that inherit from BaseAIPlayer
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseAIPlayer) and 
                            obj != BaseAIPlayer):
                            # Register the player class
                            self._register_player_class(obj)
                except Exception as e:
                    print(f"Error loading AI player module {module_name}: {e}")
    
    def _register_player_class(self, player_class: Type[BaseAIPlayer]) -> None:
        """Register an AI player class.
        
        Args:
            player_class: The AI player class to register
        """
        # Create an instance to get the name
        player = player_class()
        name = player.name
        
        # Register the class by name
        self._player_classes[name] = player_class
    
    def get_player_class(self, name: str) -> Type[BaseAIPlayer]:
        """Get an AI player class by name.
        
        Args:
            name: The name of the AI player
            
        Returns:
            The AI player class
            
        Raises:
            KeyError: If no AI player with the given name exists
        """
        self._ensure_initialized()
        return self._player_classes[name]
    
    def create_player(self, name: str) -> BaseAIPlayer:
        """Create an instance of an AI player by name.
        
        Args:
            name: The name of the AI player
            
        Returns:
            An instance of the AI player
            
        Raises:
            KeyError: If no AI player with the given name exists
        """
        player_class = self.get_player_class(name)
        return player_class()
    
    def get_available_players(self) -> List[Tuple[str, str]]:
        """Get a list of available AI players with their names and descriptions.
        
        Returns:
            A list of tuples (name, description) for each available AI player
        """
        self._ensure_initialized()
        
        players = []
        for name, player_class in self._player_classes.items():
            player = player_class()
            players.append((name, player.name))
        
        # Sort by name
        players.sort(key=lambda p: p[0])
        
        return players
    
    def _ensure_initialized(self) -> None:
        """Ensure the registry is initialized."""
        if not self._initialized:
            self._discover_player_classes()
            self._initialized = True


# Singleton instance of the AI player registry
registry = AIPlayerRegistry() 