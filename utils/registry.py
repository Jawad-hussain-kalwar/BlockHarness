"""
Generic registry for plugin-like components such as AI players, DDA algorithms, etc.
Provides a common interface for component discovery, registration, and instantiation.
"""
import importlib
import inspect
import os
from typing import Dict, List, Type, Tuple, Any, Optional, TypeVar, Generic, Callable


# Define generic type for base classes
T = TypeVar('T')

class Registry(Generic[T]):
    """Generic registry for plugin components.
    
    This class provides a way to discover and register all available implementations
    of a base class within a specified directory.
    """
    
    def __init__(self, base_class: Type[T], auto_discover: bool = False):
        """Initialize the registry.
        
        Args:
            base_class: The base class that registered components must inherit from
            auto_discover: Whether to automatically discover components on initialization
        """
        self._items: Dict[str, Type[T]] = {}
        self._base_class = base_class
        self._initialized = False
        
        if auto_discover:
            self.discover_components()
    
    def discover_components(self, directory: Optional[str] = None, package: Optional[str] = None) -> None:
        """Discover all components in the specified directory that inherit from the base class.
        
        Args:
            directory: The directory to search in. If None, will use the directory of the base class.
            package: The package name to use for imports. If None, will use the name of the base class's module.
        """
        if directory is None:
            # Get the directory of the base class's module
            directory = os.path.dirname(inspect.getmodule(self._base_class).__file__)
        
        if package is None:
            # Get the package name of the base class
            package = self._base_class.__module__.split('.')[0]
        
        # Get the base filename to exclude
        base_filename = os.path.basename(inspect.getfile(self._base_class))
        registry_filename = os.path.basename(__file__)
        
        # Get all Python files in the directory
        for filename in os.listdir(directory):
            if (filename.endswith('.py') and 
                filename not in ['__init__.py', base_filename, registry_filename]):
                # Import the module
                module_name = f"{package}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find classes that inherit from the base class
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, self._base_class) and 
                            obj != self._base_class):
                            # Register the component class
                            self.register(obj)
                except Exception as e:
                    print(f"Error loading module {module_name}: {e}")
        
        self._initialized = True
    
    def register(self, component_class: Type[T]) -> None:
        """Register a component class.
        
        Args:
            component_class: The component class to register
        """
        # Try to get the name attribute from the class or an instance
        try:
            # First try the class itself for a name property or attribute
            if hasattr(component_class, 'name') and isinstance(component_class.name, property):
                # It's a property, so we need to instantiate
                component = component_class()
                name = component.name
            elif hasattr(component_class, 'name') and callable(getattr(component_class, 'name')):
                # It's a method, so we need to instantiate
                component = component_class()
                name = component.name()
            elif hasattr(component_class, 'name'):
                # It's a class attribute
                name = component_class.name
            else:
                # Use the class name as fallback
                name = component_class.__name__
        except Exception:
            # If we get any errors, fall back to class name
            name = component_class.__name__
        
        # Register the class by name
        self._items[name] = component_class
    
    def get_class(self, name: str) -> Type[T]:
        """Get a component class by name.
        
        Args:
            name: The name of the component
            
        Returns:
            The component class
            
        Raises:
            KeyError: If no component with the given name exists
        """
        self._ensure_initialized()
        return self._items[name]
    
    def create(self, name: str, *args, **kwargs) -> T:
        """Create an instance of a component by name.
        
        Args:
            name: The name of the component
            *args: Positional arguments to pass to the constructor
            **kwargs: Keyword arguments to pass to the constructor
            
        Returns:
            An instance of the component
            
        Raises:
            KeyError: If no component with the given name exists
        """
        component_class = self.get_class(name)
        return component_class(*args, **kwargs)
    
    def get_available_components(self, 
                                name_formatter: Optional[Callable[[Type[T]], str]] = None) -> List[Tuple[str, str]]:
        """Get a list of available components with their names and display names.
        
        Args:
            name_formatter: Optional function to format the display name of each component
            
        Returns:
            A list of tuples (name, display_name) for each available component
        """
        self._ensure_initialized()
        
        components = []
        for name, component_class in self._items.items():
            if name_formatter:
                display_name = name_formatter(component_class)
            else:
                try:
                    # Try to get display_name from the class
                    if hasattr(component_class, 'display_name'):
                        display_name = component_class.display_name
                    else:
                        # Otherwise use the name
                        display_name = name
                except Exception:
                    display_name = name
            
            components.append((name, display_name))
        
        # Sort by name
        components.sort(key=lambda c: c[0])
        
        return components
    
    def _ensure_initialized(self) -> None:
        """Ensure the registry is initialized."""
        if not self._initialized:
            self.discover_components()
            self._initialized = True 