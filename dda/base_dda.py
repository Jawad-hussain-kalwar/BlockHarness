from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseDDAAlgorithm(ABC):
    """Base class for all DDA algorithms."""
    
    # Class attribute for dropdown display
    display_name = "Abstract DDA Algorithm"
    
    @abstractmethod
    def initialize(self, config_params: Dict) -> None:
        """Initialize algorithm with configuration parameters."""
        pass
        
    @abstractmethod
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed.
        
        Args:
            engine_state: The current game engine state
            
        Returns:
            Optional[List[int]]: New shape weights if adjustment needed, None otherwise
        """
        pass
        
    @property
    def name(self) -> str:
        """Return algorithm name."""
        return self.__class__.__name__ 