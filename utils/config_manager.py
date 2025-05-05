"""
ConfigManager centralizes configuration management using the observer pattern.
This eliminates duplicate config handling across different components.
"""
from typing import Dict, List, Callable, Any, Optional, Set


# Type definitions
ConfigObserver = Callable[[Dict[str, Any]], None]
ConfigFilter = Set[str]  # Set of config keys to observe


class ConfigManager:
    """Central configuration manager using the observer pattern.
    
    This class maintains a single configuration dictionary and notifies
    registered observers when changes occur.
    """
    
    def __init__(self, initial_config: Optional[Dict[str, Any]] = None):
        """Initialize the configuration manager.
        
        Args:
            initial_config: Optional initial configuration dictionary
        """
        self._config = initial_config or {}
        self._observers: List[tuple[ConfigObserver, Optional[ConfigFilter]]] = []
    
    def register_observer(self, observer: ConfigObserver, 
                         config_filter: Optional[ConfigFilter] = None) -> None:
        """Register an observer to be notified of configuration changes.
        
        Args:
            observer: Function to call when configuration changes
            config_filter: Optional set of configuration keys to observe
        """
        self._observers.append((observer, config_filter))
    
    def unregister_observer(self, observer: ConfigObserver) -> bool:
        """Unregister an observer.
        
        Args:
            observer: Observer function to unregister
            
        Returns:
            True if the observer was found and removed, False otherwise
        """
        for i, (obs, _) in enumerate(self._observers):
            if obs == observer:
                del self._observers[i]
                return True
        return False
    
    def update(self, new_config: Dict[str, Any]) -> None:
        """Update the configuration with new values.
        
        Args:
            new_config: New configuration values to apply
        """
        if not new_config:
            return
        
        # Track which keys are changing
        changed_keys = set()
        
        # Update the configuration
        for key, value in new_config.items():
            if key not in self._config or self._config[key] != value:
                changed_keys.add(key)
                self._config[key] = value
        
        # Notify observers
        self._notify_observers(changed_keys)
    
    def set(self, key: str, value: Any) -> None:
        """Set a single configuration value.
        
        Args:
            key: Configuration key
            value: New value
        """
        if key not in self._config or self._config[key] != value:
            self._config[key] = value
            self._notify_observers({key})
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key does not exist
            
        Returns:
            The configuration value, or the default if the key does not exist
        """
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary.
        
        Returns:
            A copy of the configuration dictionary
        """
        return self._config.copy()
    
    def _notify_observers(self, changed_keys: Set[str]) -> None:
        """Notify observers of configuration changes.
        
        Args:
            changed_keys: Set of configuration keys that have changed
        """
        if not changed_keys:
            return
            
        for observer, config_filter in self._observers:
            # Check if this observer cares about any of the changed keys
            should_notify = (
                config_filter is None or
                any(key in config_filter for key in changed_keys)
            )
            
            if should_notify:
                observer(self._config)


# Singleton instance
config_manager = ConfigManager() 