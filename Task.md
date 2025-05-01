# DDA Implementation Plan

This document outlines the step-by-step actions needed to implement the new DDA system features as specified.

## 1. Create a New Static DDA Class

### 1.1 Create StaticDDA Implementation
- [x] Create a new file in `dda/static_dda.py`
- [x] Implement `StaticDDA` class that extends `BaseDDAAlgorithm`
- [x] Set `display_name` class attribute to "Static"
- [x] Implement `initialize` method with fixed weights for all blocks
- [x] Implement `maybe_adjust` method that always returns None (no adjustments)
- [x] Register the new DDA algorithm in the registry at the end of the file

### 1.2 Update Initialization
- [x] Import the new StaticDDA in `dda/__init__.py` to ensure it's registered

## 2. Create DDA-Specific View Structure

### 2.1 Create Directory Structure
- [x] Create directory structure: `ui/views/dda_views/`
- [x] Create file `ui/views/dda_views/__init__.py` for importing convenience

### 2.2 Implement Threshold DDA View
- [x] Create file `ui/views/dda_views/th_dda_view.py`
- [x] Move all threshold DDA specific controls from `dda_section.py` to this file
  - [x] Initial weights input field
  - [x] Threshold score and weights input fields
  - [x] Related labels and positioning logic
- [x] Implement `ThresholdDDAView` class with the following methods:
  - [x] `__init__(self, parent_rect, font, small_font)`
  - [x] `update_config_fields(self, config)`
  - [x] `draw(self, surface)`
  - [x] `handle_event(self, event)`
  - [x] `get_config_values(self)`

### 2.3 Implement Static DDA View
- [x] Create file `ui/views/dda_views/static_dda_view.py`
- [x] Implement `StaticDDAView` class with the same methods as `ThresholdDDAView`
- [x] Include only necessary controls:
  - [x] Initial weights input field with fixed value of "1,1,1,1,1,1,1,1" (for all block types)
  - [x] A visual representation or sample image showing equal distribution
- [x] Add a label explaining that Static DDA does not adjust difficulty

## 3. Refactor DDA Section to Support Multiple DDA Views

### 3.1 Modify DDA Section
- [x] Update imports in `dda_section.py` to include new DDA view classes
- [x] Remove DDA-specific controls from DDASection class
- [x] Modify `__init__` to handle different DDA algorithm types:
  - [x] Keep only the DDA algorithm dropdown and apply button
  - [x] Add a container attribute to hold the current DDA view
- [x] Add a method to switch between DDA views based on selected algorithm:
  ```python
  def _update_active_dda_view(self, algorithm_name):
      """Update the active DDA view based on the selected algorithm."""
      if algorithm_name == "ThresholdDDA":
          self.active_dda_view = self.threshold_dda_view
      elif algorithm_name == "StaticDDA":
          self.active_dda_view = self.static_dda_view
      # Add future DDA types here
  ```

### 3.2 Update Event Handling
- [x] Modify `handle_event` in DDASection to delegate to active DDA view
- [x] Update `get_config_values` to get values from active DDA view
- [x] Modify dropdown handling to switch active view when selection changes

### 3.3 Update Drawing Logic
- [x] Update `draw` method to draw the appropriate DDA view based on selection

## 4. Integration and Testing

### 4.1 Controller Integration
- [x] Update any controller code that directly references DDA input fields
- [x] Ensure the simulation_controller properly initializes DDA views

### 4.2 Testing Plan
- [ ] Test switching between DDAs in the UI
- [ ] Test Static DDA in game and confirm it maintains constant weights
- [ ] Test Threshold DDA to ensure it still functions properly
- [ ] Verify that changes to one DDA view don't affect others

## 5. Prepare for Future Extensions

### 5.1 Documentation
- [x] Add comments explaining the extensibility pattern for new DDAs
- [x] Update relevant READMEs with information about the new DDA and structure

### 5.2 Extension Pattern
- [x] Create a template file `ui/views/dda_views/template_dda_view.py` for future DDA implementations
- [x] Document the pattern for adding new DDAs:
  1. Create new DDA class in `dda/`
  2. Register it in the registry
  3. Create a matching view in `ui/views/dda_views/`
  4. Update the DDA section to handle the new type
