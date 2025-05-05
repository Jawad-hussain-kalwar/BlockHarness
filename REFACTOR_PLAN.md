# BlockHarness Refactoring Plan

## Objective
Create a cleaner, more maintainable codebase by eliminating code duplication and enforcing the DRY (Don't Repeat Yourself) principle.

## Identified Issues and Solutions

### 1. Controller Hierarchy Redundancy

**Problem:**
- SimulationController duplicates event handling code from GameController
- Both controllers implement similar rendering and loop methods with slight variations

**Solution:**
- Refactor event handling into protected template methods with specific hooks
- Create a more structured event system with delegation/hooks
- Example improvements:
  ```python
  # Current pattern (in both controllers):
  def handle_events(self):
      for event in pygame.event.get():
          # Similar code with slight variations...
  
  # Refactored pattern:
  def handle_events(self):
      for event in pygame.event.get():
          if self._handle_common_events(event):
              continue
          if self._handle_controller_specific_events(event):
              continue
  ```

### 2. Game State Management

**Problem:**
- Game state reset logic is duplicated across BaseController, GameController, and SimulationController
- State transitions follow similar patterns but with controller-specific variations

**Solution:**
- Create a dedicated GameState class to centralize state management
- Implement State pattern for different game phases (setup, playing, game over, etc.)
- Move engine reset logic into a single location
- Standardize how state is saved and restored

### 3. UI Event Handling

**Problem:**
- Event handling follows similar patterns in GameController and SimulationController
- Resize handling logic is duplicated

**Solution:**
- Create an EventManager class to standardize event processing
- Implement a publish-subscribe system for controller-specific event handlers
- Use delegation for specialized behaviors while keeping core logic in one place

### 4. Animation Logic Duplication

**Problem:**
- Animation handling appears in both GameEngine and controllers
- Update logic is called from multiple places

**Solution:**
- Create a centralized AnimationSystem that all components can access
- Standardize how animations are registered and processed
- Use callbacks for animation completion events

### 5. Configuration Management

**Problem:**
- Configuration is passed around and processed in multiple components
- Update logic is repeated

**Solution:**
- Create a ConfigManager singleton with observer pattern
- Components can subscribe to config changes they care about
- Ensure configuration is only processed in one place

### 6. Registry Pattern Implementation

**Problem:**
- AI and DDA registries implement very similar functionality
- Logic for discovery, registration, and instantiation is duplicated

**Solution:**
- Create a generic Registry base class that both can inherit from
- Standardize the registry interface and reduce duplication
- Example implementation:
  ```python
  class Registry:
      """Generic registry for plugin components."""
      def __init__(self, base_class):
          self._items = {}
          self._base_class = base_class
      
      def register(self, name, cls):
          # Shared registration logic
          
      def create(self, name, *args, **kwargs):
          # Shared instantiation logic
  ```

### 7. Metrics Calculation

**Problem:**
- Some metric calculations may be duplicated across components
- State monitoring logic is spread across classes

**Solution:**
- Ensure MetricsManager is the single source of truth for all metrics
- Implement caching for expensive calculations
- Use observer pattern to notify interested components of metric changes

## Implementation Plan

1. **Phase 1: Create Core Infrastructure**
   - Implement Registry base class
   - Create EventManager system
   - Develop ConfigManager with observer pattern
   - Design GameState class hierarchy

2. **Phase 2: Refactor Controllers**
   - Update BaseController to use new infrastructure
   - Modify GameController to delegate to new systems
   - Refactor SimulationController to eliminate duplication

3. **Phase 3: Standardize State Management**
   - Implement state transitions in GameState
   - Move engine reset logic to appropriate location
   - Update all controllers to use centralized state

4. **Phase 4: Optimize UI and Rendering**
   - Consolidate animation system
   - Streamline event handling
   - Remove duplicate render code

5. **Phase 5: Testing and Validation**
   - Ensure all game functionality works as before
   - Verify that performance is maintained or improved
   - Document the new architecture

## Expected Benefits

- **Reduced Code Size:** Elimination of duplicate code
- **Improved Maintainability:** Clearer separation of concerns
- **Better Extensibility:** Easier to add new features
- **Enhanced Readability:** Consistent patterns throughout codebase
- **Reduced Bug Surface:** Less code generally means fewer bugs

## Metrics for Success

- Reduction in total lines of code
- Decrease in duplicated code (measured by static analysis)
- Improved code cohesion and coupling metrics
- Maintained or improved performance 