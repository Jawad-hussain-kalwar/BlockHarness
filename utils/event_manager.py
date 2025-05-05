"""
EventManager handles Pygame events in a centralized manner using a publish-subscribe pattern.
This avoids duplicated event handling code across different controllers.
"""
import pygame
from typing import Dict, List, Callable, Any, Optional, Set, Union, Tuple


# Define types for event handlers
EventHandlerFunction = Callable[[pygame.event.Event], Union[bool, Dict[str, Any]]]
EventFilter = Set[int]  # Set of pygame event types


class EventManager:
    """Centralized Pygame event handler using a publish-subscribe pattern.
    
    This class allows components to register handlers for specific event types,
    eliminating the need for duplicate event handling across controllers.
    """
    
    def __init__(self):
        """Initialize the event manager."""
        # Map event types to lists of handler functions
        self._handlers: Dict[int, List[EventHandlerFunction]] = {}
        
        # Special handlers for common events
        self._quit_handlers: List[EventHandlerFunction] = []
        self._resize_handlers: List[EventHandlerFunction] = []
        
        # Handlers that receive all events
        self._global_handlers: List[Tuple[EventHandlerFunction, Optional[EventFilter]]] = []
    
    def register_handler(self, event_type: int, handler: EventHandlerFunction) -> None:
        """Register a handler for a specific event type.
        
        Args:
            event_type: Pygame event type to handle
            handler: Function to call when the event occurs
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def register_quit_handler(self, handler: EventHandlerFunction) -> None:
        """Register a handler for QUIT events.
        
        Args:
            handler: Function to call when a QUIT event occurs
        """
        self._quit_handlers.append(handler)
    
    def register_resize_handler(self, handler: EventHandlerFunction) -> None:
        """Register a handler for VIDEORESIZE events.
        
        Args:
            handler: Function to call when a VIDEORESIZE event occurs
        """
        self._resize_handlers.append(handler)
    
    def register_global_handler(self, handler: EventHandlerFunction, 
                               event_filter: Optional[EventFilter] = None) -> None:
        """Register a handler that receives all events.
        
        Args:
            handler: Function to call for all events
            event_filter: Optional set of event types to filter for
        """
        self._global_handlers.append((handler, event_filter))
    
    def unregister_handler(self, event_type: int, handler: EventHandlerFunction) -> bool:
        """Unregister a handler for a specific event type.
        
        Args:
            event_type: Pygame event type
            handler: Handler function to unregister
            
        Returns:
            True if the handler was found and removed, False otherwise
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            return True
        return False
    
    def unregister_global_handler(self, handler: EventHandlerFunction) -> bool:
        """Unregister a global handler.
        
        Args:
            handler: Handler function to unregister
            
        Returns:
            True if the handler was found and removed, False otherwise
        """
        for i, (h, _) in enumerate(self._global_handlers):
            if h == handler:
                del self._global_handlers[i]
                return True
        return False
    
    def process_events(self) -> bool:
        """Process all pending pygame events.
        
        Returns:
            False if the application should quit, True otherwise
        """
        for event in pygame.event.get():
            # Handle quit events first
            if event.type == pygame.QUIT:
                for handler in self._quit_handlers:
                    result = handler(event)
                    if isinstance(result, bool) and not result:
                        return False
                # Default quit behavior if no handlers returned False
                if not self._quit_handlers:
                    return False
            
            # Handle resize events
            elif event.type == pygame.VIDEORESIZE:
                for handler in self._resize_handlers:
                    handler(event)
            
            # Process global handlers that match the filter
            for handler, event_filter in self._global_handlers:
                if event_filter is None or event.type in event_filter:
                    result = handler(event)
                    if isinstance(result, bool) and not result:
                        return False
            
            # Process specific event handlers
            if event.type in self._handlers:
                for handler in self._handlers[event.type]:
                    result = handler(event)
                    if isinstance(result, bool) and not result:
                        return False
        
        return True 