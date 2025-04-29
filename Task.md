**Objective:**
Modify the UI and functionality to include new features while keeping the existing controllers and other components intact.

**UI Changes:**
1. **Split the Left Sidebar:**
   - Divide the left sidebar into two halves.
   - Use the top half for Dynamic Difficulty Adjustment (DDA).
   - Use the bottom half for simulation controls.

2. **Add AI Player Selection:**
   - Introduce ability to add multiple AI players, each with unique strategies for placing blocks.
   - Include a dynamic dropdown menu in the UI to select one of available AI player.
   - Allow the simulation to start with the selected AI player.

**Functionality Changes:**
1. **Dynamic AI Algorithms:**
   - Implement various algorithms for AI players, which may evolve over time.
   - Ensure the dropdown menu updates dynamically to reflect available AI algorithms.
   
---

# Implementation Plan for UI & Functionality Changes

## 1. Update the SidebarView Class

### 1.1 Split the Left Sidebar into Two Halves
- Modify the `SidebarView` class to split the sidebar vertically into two sections
- Create a clear separation line between the DDA section (top) and the simulation controls (bottom)

### 1.2 Implement a Dropdown Menu Class
- Create a new `DropdownMenu` class in the UI module, similar to the existing `InputField` class
- Implement methods for drawing, handling events, and retrieving selected values

### 1.3 Update AI Player Selection in Sidebar
- Add a dropdown menu for AI player selection in the simulation control section
- Connect the dropdown to the available AI algorithms

## 2. Modify the AI Module

### 2.1 Create a Base AI Player Interface
- Refactor the existing AIPlayer in Greedy1.py to follow a consistent interface
- Create a base class or interface that all AI players will implement

### 2.2 Implement Additional AI Algorithms
- Create new AI player classes implementing different strategies
- Place them in the AI directory with meaningful names
- Ensure all implementations adhere to the common interface

### 2.3 Create an AI Player Registry
- Implement a registry system to dynamically discover and load available AI players
- Make the registry accessible to the UI for populating the dropdown menu

## 3. Update the SimulationController

### 3.1 Modify the AI Controller Initialization
- Update the SimulationController to use the selected AI player
- Add a method to change the active AI player based on user selection

### 3.2 Update the Simulation Start Logic
- Modify the start_simulation method to use the selected AI player
- Update the simulation controls handling to process AI player selection

## 4. Update the Config Structure

### 4.1 Add AI Configuration Options
- Extend the configuration structure to include AI player selection
- Ensure backward compatibility with existing config files

### 4.2 Update Config Getters/Setters in SidebarView
- Modify the get_config_values and update_config_fields methods to handle AI player selection

## Detailed Tasks Breakdown

### Task 1: Create the DropdownMenu Class
1. Create a new file `ui/dropdown_menu.py`
2. Implement a class similar to InputField but with dropdown functionality
3. Implement methods for drawing, event handling, and value retrieval

### Task 2: Create an AI Player Interface
1. Create a new file `ai/base_player.py` with a base class or interface
2. Refactor the existing AIPlayer in Greedy1.py to implement this interface
3. Update imports in AIController to use the new structure

### Task 3: Implement Additional AI Players
1. Create at least one new AI player algorithm (e.g., `ai/Random.py`) 
2. Implement the common interface
3. Ensure it works with the existing AIController

### Task 4: Create AI Player Registry
1. Create a new file `ai/registry.py`
2. Implement logic to discover and register AI player classes
3. Add methods to get available AI players and instantiate them by name

### Task 5: Update SidebarView
1. Modify `sidebar_view.py` to split the sidebar into two sections
2. Add a dropdown menu for AI player selection
3. Update the layout to accommodate new elements
4. Update event handling to process dropdown events

### Task 6: Update SimulationController
1. Modify initialization to accept an AI player selection
2. Update simulation start logic to use the selected AI player
3. Add methods to change the active AI player

### Task 7: Update Config Handling
1. Update config structure to include AI player selection
2. Modify config getters/setters in SidebarView
3. Ensure backward compatibility

## Impact Assessment

- **Existing Controllers**: No changes to core controller functionality, only extending SimulationController
- **UI Components**: Adding new UI elements while maintaining the existing layout and flow
- **AI Module**: Refactoring existing code to support multiple AI implementations
- **Configuration**: Extending the configuration structure while maintaining backward compatibility

---

- [x] **Split the Left Sidebar**  
  - [x] Divide the sidebar vertically into two halves  
  - [x] Allocate top half to Dynamic Difficulty Adjustment (DDA)  
  - [x] Allocate bottom half to simulation controls  

- [x] **Add AI Player Selection**  
  - [x] Introduce support for multiple AI players, each with its own placement strategy  
  - [x] Add a dynamic dropdown menu in the simulation-controls section  
  - [x] Wire the "Start Simulation" action to use the selected AI player  

- [x] **Implement Dynamic AI Algorithms**  
  - [x] Design and implement several AI placement strategies  
  - [x] Ensure the dropdown list updates automatically when new algorithms are added  

- [x] **Update SidebarView Class**  
  - [x] Refactor `SidebarView` to render two stacked panels (DDA and controls)  
  - [x] Draw a clear separator between the panels  
  - [x] Integrate the dropdown menu component into the controls panel  

- [x] **Develop DropdownMenu Component**  
  - [x] Create `ui/dropdown_menu.py`  
  - [x] Implement rendering, mouse-event handling, and value-selection logic  
  - [x] Match styling and API of existing `InputField` component  

- [x] **Refactor AI Module**  
  - [x] Create a base interface in `ai/base_player.py`  
  - [x] Refactor `ai/Greedy1.py` (and others) to implement this interface  
  - [x] Implement at least one new AI player (e.g. `ai/Random.py`) following the interface  

- [x] **Build AI Player Registry**  
  - [x] Create `ai/registry.py` to discover and register AI player classes dynamically  
  - [x] Expose a method to list available AI players by name  
  - [x] Hook registry into the dropdown menu's data source  

- [x] **Enhance SimulationController**  
  - [x] Modify constructor to accept an AI-player instance  
  - [x] Update `start_simulation` to instantiate and use the selected AI player  
  - [x] Add a method to switch AI players at runtime  

- [x] **Extend Configuration Schema**  
  - [x] Add an "ai_player" field to your config structure  
  - [x] Update `SidebarView.get_config_values()` and `update_config_fields()` to include AI selection  
  - [x] Ensure old configs (without the new field) still load without errors  

---