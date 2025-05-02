# Metrics-Based Dynamic Difficulty Adjustment Algorithm

## Overview

The Metrics-Based DDA will analyze player performance metrics and game state to dynamically adjust difficulty by selecting appropriate shapes for the next tray. This DDA aims to maintain an appropriate challenge level throughout the game, preventing both frustration and boredom by responding to player performance in real-time.

## Implementation Plan

### 1. File Structure

Create two new files:
- `dda/metrics_dda.py` - Core implementation of the MetricsDDA algorithm
- `ui/views/dda_views/metrics_dda_view.py` - UI configuration interface for the algorithm

### 2. Core DDA Implementation

The `MetricsDDA` class will extend `BaseDDAAlgorithm` and will:

1. **Track Game State**:
   - Monitor board state metrics like occupancy ratio and fragmentation
   - Track player performance metrics like clear rate and emotional state
   - Maintain a dynamic difficulty level (1-10 scale)

2. **Support Three Operating Modes**:
   - **Emergency Mode**: When `imminent_threat` is true, provide only rescue shapes
   - **Rescue Mode**: When `danger_score >= danger_cut`, provide a mix of rescue shapes and simple shapes
   - **Normal Mode**: Provide a balanced mix of shapes based on difficulty level

3. **Define Core Functions**:
   - `initialize(config_params)`: Set up initial parameters from config
   - `maybe_adjust(engine_state)`: Analyze metrics and adjust shape weights if needed
   - Helper methods for mode detection, shape selection, and difficulty adaptation

### 3. Algorithm Details

#### State Analysis
- Extract board state and metrics from the engine state in `maybe_adjust` method
- Use engine's `get_metrics()` function to access all metrics
- Use `imminent_threat`, `danger_score`, and `phase` metrics for mode decisions
- Track clear rate across moves to adjust difficulty

#### Difficulty Management
- Maintain a `difficulty_level` (1-10) based on player performance
- Increment/decrement based on clear rate vs. target bands (`low_clear` and `high_clear`)
- Apply special handling for emotional states (lower when frustrated, raise when bored)
- Store current `difficulty_level` as internal state in the DDA instance

#### Shape Selection Logic
- **Emergency Mode** (when `imminent_threat` is true):
  - Return weights with high values for indices 0-1 (1×1 and 1×2 shapes)
  - Set weights for all other indices to 0

- **Rescue Mode** (when `danger_score >= danger_cut`):
  - Use rescue weights with high values for small shapes (≤ 3 blocks)
  - Apply lower weights for larger shapes

- **Normal Mode**:
  - Derive size cap from current difficulty level using `size_caps` configuration
  - Further reduce size cap to 3 in early game phase
  - Return weights that favor shapes within the size cap

#### Mid-Tray Rescue
- Monitor danger score on each call to `maybe_adjust`
- If danger score suddenly exceeds threshold, update weights immediately
- Return new weights to change the remaining shapes in the current tray

### 4. Configuration Parameters

The MetricsDDA will need the following parameters in the config:

```python
"dda_params": {
    "metrics_dda": {
        "initial_difficulty": 3,                    # Starting difficulty (1-10)
        "low_clear": 0.30,                          # From existing metrics_flow
        "high_clear": 0.70,                         # From existing metrics_flow
        "danger_cut": 0.80,                         # From existing metrics_flow
        "rescue_shape_weights": [10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Weights for rescue mode
        "size_caps": [3, 3, 3, 4, 4, 4, 5, 5, 5, 5]  # Max shape size per difficulty level
    }
}
```

### 5. Integration Steps

1. Register the MetricsDDA in `dda/registry.py`:
   ```python
   registry.register("MetricsDDA", MetricsDDA)
   ```

2. Add import to `dda/__init__.py`:
   ```python
   from dda.metrics_dda import MetricsDDA
   ```

3. Add the view to `ui/views/dda_views/__init__.py`:
   ```python
   from ui.views.dda_views.metrics_dda_view import MetricsDDAView
   ```

4. Update the DDA section in `ui/views/dda_section.py` to include the new view:
   ```python
   # Add to __init__
   self.metrics_dda_view = MetricsDDAView(self.dda_view_rect, font, small_font)
   
   # Add to _update_active_dda_view
   elif algorithm_name == "MetricsDDA":
       self.active_dda_view = self.metrics_dda_view
   ```

### 7. Implementation Details

#### metrics_dda.py Core Structure

```python
from typing import Dict, List, Optional
from dda.base_dda import BaseDDAAlgorithm
from dda.registry import registry

class MetricsDDA(BaseDDAAlgorithm):
    """DDA algorithm that adjusts difficulty based on player performance metrics."""
    
    display_name = "Metrics Adaptive"
    
    def __init__(self):
        """Initialize the metrics-based DDA algorithm."""
        self.difficulty_level = 3  # Default initial difficulty (1-10)
        self.low_clear = 0.30
        self.high_clear = 0.70
        self.danger_cut = 0.80
        self.rescue_shape_weights = []
        self.size_caps = []
        self.current_mode = "normal"  # "normal", "rescue", or "emergency"
        
    def initialize(self, config_params: Dict) -> None:
        """Initialize algorithm with configuration parameters."""
        params = config_params.get("metrics_dda", {})
        self.difficulty_level = params.get("initial_difficulty", 3)
        
        # Get flow parameters from global metrics config if not specified
        metrics_flow = config_params.get("metrics_flow", {})
        self.low_clear = params.get("low_clear", metrics_flow.get("low_clear", 0.30))
        self.high_clear = params.get("high_clear", metrics_flow.get("high_clear", 0.70))
        self.danger_cut = params.get("danger_cut", metrics_flow.get("danger_cut", 0.80))
        
        # Other parameters
        self.rescue_shape_weights = params.get("rescue_shape_weights", [10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.size_caps = params.get("size_caps", [3, 3, 3, 4, 4, 4, 5, 5, 5, 5])
        
    def maybe_adjust(self, engine_state) -> Optional[List[int]]:
        """Check game state and return new weights if adjustment needed."""
        # Get all metrics from the engine
        metrics = engine_state.get_metrics()
        
        # Check for emergency mode (imminent threat)
        imminent_threat = metrics.get("imminent_threat", False)
        if imminent_threat:
            self.current_mode = "emergency"
            return self._get_emergency_weights()
            
        # Check for rescue mode (high danger score)
        danger_score = metrics.get("danger_score", 0.0)
        if danger_score >= self.danger_cut:
            if self.current_mode != "rescue":
                self.current_mode = "rescue"
                return self._get_rescue_weights()
        else:
            # Normal mode - check if we need to adjust difficulty
            self.current_mode = "normal"
            
            # Get player performance metrics
            clear_rate = metrics.get("clear_rate", 0.5)
            emotional_state = metrics.get("emotional_state", "Calm")
            
            # Adjust difficulty level based on clear rate
            old_difficulty = self.difficulty_level
            if clear_rate < self.low_clear:
                self.difficulty_level = max(1, self.difficulty_level - 1)
            elif clear_rate > self.high_clear:
                self.difficulty_level = min(10, self.difficulty_level + 1)
                
            # Special adjustments based on emotional state
            if emotional_state == "Frustrated" and danger_score > 0.6:
                self.difficulty_level = max(1, self.difficulty_level - 2)
            elif emotional_state == "Bored" and self.difficulty_level < 10:
                self.difficulty_level = min(10, self.difficulty_level + 1)
                
            # Return new weights if difficulty changed
            if old_difficulty != self.difficulty_level:
                return self._get_normal_weights(metrics.get("phase", "mid"))
                
        # No adjustment needed
        return None
        
    def _get_emergency_weights(self) -> List[int]:
        """Get weights for emergency mode - only smallest shapes."""
        weights = [0] * 11  # Assuming 11 shape types
        weights[0] = 10  # High weight for 1x1 shape
        weights[1] = 5   # Medium weight for 1x2 shape
        return weights
        
    def _get_rescue_weights(self) -> List[int]:
        """Get weights for rescue mode - favor small shapes."""
        return self.rescue_shape_weights
        
    def _get_normal_weights(self, phase: str) -> List[int]:
        """Get weights for normal mode based on difficulty and phase."""
        weights = [1] * 11  # Default equal weights
        
        # Get size cap based on difficulty level
        idx = min(int(self.difficulty_level) - 1, len(self.size_caps) - 1)
        size_cap = self.size_caps[idx]
        
        # Reduce size cap in early phase
        if phase == "early":
            size_cap = min(size_cap, 3)
            
        # Apply weights based on size cap
        for i in range(len(weights)):
            if i < size_cap:
                weights[i] = size_cap - i + 1  # Higher weights for smaller shapes
            else:
                weights[i] = 0  # Zero weight for shapes above size cap
                
        return weights

# Register the metrics DDA algorithm
registry.register("MetricsDDA", MetricsDDA)
```

#### metrics_dda_view.py Implementation

```python
import pygame
from typing import Dict, List, Optional
from ui.colours import (
    TEXT_PRIMARY, TEXT_SECONDARY,
    SECTION_BG, SECTION_BORDER,
    INPUT_BG, INPUT_BORDER
)
from ui.layout import (
    PADDING, FIELD_HEIGHT, FIELD_SPACING,
    LABEL_SPACING, BORDER_RADIUS
)
from ui.input_field import InputField
from ui.views.dda_views.template_dda_view import TemplateDDAView


class MetricsDDAView(TemplateDDAView):
    """Configuration view for the Metrics-based DDA algorithm."""
    
    def __init__(self, parent_rect, font, small_font):
        """Initialize the metrics DDA view with UI elements.
        
        Args:
            parent_rect: Rect of the parent section
            font: Font for main labels
            small_font: Font for smaller labels
        """
        super().__init__(parent_rect, font, small_font)
        
        # Calculate positioning based on parent rectangle
        left_x = self.rect.x + PADDING
        top_y = self.rect.y + PADDING
        field_width = self.rect.width - 2 * PADDING
        
        # Initialize positions and UI elements
        y = top_y
        
        # Description
        self.description_label = (left_x, y)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Initial difficulty level
        self.init_difficulty_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        init_difficulty_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.init_difficulty_field = InputField(init_difficulty_rect, "3", 2)
        self.input_fields.append(self.init_difficulty_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Low clear rate threshold
        self.low_clear_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        low_clear_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.low_clear_field = InputField(low_clear_rect, "0.30", 4)
        self.input_fields.append(self.low_clear_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # High clear rate threshold
        self.high_clear_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        high_clear_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.high_clear_field = InputField(high_clear_rect, "0.70", 4)
        self.input_fields.append(self.high_clear_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Danger score threshold
        self.danger_cut_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        danger_cut_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.danger_cut_field = InputField(danger_cut_rect, "0.80", 4)
        self.input_fields.append(self.danger_cut_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Rescue shape weights - first two values (other values are 0)
        self.rescue_weights_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        rescue_weights_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.rescue_weights_field = InputField(rescue_weights_rect, "10,8", 10)
        self.input_fields.append(self.rescue_weights_field)
        y += FIELD_HEIGHT + FIELD_SPACING
        
        # Size caps - concise representation
        self.size_caps_label = (left_x, y)
        y += FIELD_HEIGHT - FIELD_SPACING
        size_caps_rect = pygame.Rect(left_x, y, field_width, FIELD_HEIGHT)
        self.size_caps_field = InputField(size_caps_rect, "3,3,3,4,4,4,5,5,5,5", 25)
        self.input_fields.append(self.size_caps_field)
    
    def update_config_fields(self, config: Dict) -> None:
        """Update input fields from config.
        
        Args:
            config: Configuration dictionary
        """
        # Get metrics DDA params from config
        dda_params = config.get("dda_params", {})
        metrics_params = dda_params.get("metrics_dda", {})
        
        # If no specific metrics_dda params, check metrics_flow for defaults
        metrics_flow = config.get("metrics_flow", {})
        
        # Update input fields with values from config or defaults
        self.init_difficulty_field.value = str(metrics_params.get("initial_difficulty", 3))
        self.low_clear_field.value = str(metrics_params.get("low_clear", metrics_flow.get("low_clear", 0.30)))
        self.high_clear_field.value = str(metrics_params.get("high_clear", metrics_flow.get("high_clear", 0.70)))
        self.danger_cut_field.value = str(metrics_params.get("danger_cut", metrics_flow.get("danger_cut", 0.80)))
        
        # Update rescue weights (first two values, rest are 0)
        rescue_weights = metrics_params.get("rescue_shape_weights", [10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.rescue_weights_field.value = f"{rescue_weights[0]},{rescue_weights[1]}"
        
        # Update size caps
        size_caps = metrics_params.get("size_caps", [3, 3, 3, 4, 4, 4, 5, 5, 5, 5])
        self.size_caps_field.value = ",".join(str(cap) for cap in size_caps)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the metrics DDA view elements.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw description
        description_text = self.font.render("Metrics-Based Adaptive DDA", True, TEXT_PRIMARY)
        surface.blit(description_text, self.description_label)
        
        # Draw labels
        difficulty_label = self.font.render("Initial Difficulty (1-10):", True, TEXT_PRIMARY)
        surface.blit(difficulty_label, self.init_difficulty_label)
        
        low_clear_label = self.font.render("Low Clear Rate Threshold:", True, TEXT_PRIMARY)
        surface.blit(low_clear_label, self.low_clear_label)
        
        high_clear_label = self.font.render("High Clear Rate Threshold:", True, TEXT_PRIMARY)
        surface.blit(high_clear_label, self.high_clear_label)
        
        danger_cut_label = self.font.render("Danger Score Threshold:", True, TEXT_PRIMARY)
        surface.blit(danger_cut_label, self.danger_cut_label)
        
        rescue_weights_label = self.font.render("Rescue Shape Weights (1x1,1x2):", True, TEXT_PRIMARY)
        surface.blit(rescue_weights_label, self.rescue_weights_label)
        
        size_caps_label = self.font.render("Size Caps Per Difficulty Level:", True, TEXT_PRIMARY)
        surface.blit(size_caps_label, self.size_caps_label)
        
        # Draw input fields
        for field in self.input_fields:
            field.draw(surface)
    
    def get_config_values(self) -> Optional[Dict]:
        """Get the current configuration values from the metrics DDA view.
        
        Returns:
            Dict: Configuration parameters, or None if validation fails
        """
        try:
            # Parse initial difficulty
            initial_difficulty = int(self.init_difficulty_field.value)
            if not (1 <= initial_difficulty <= 10):
                print("Initial difficulty must be between 1 and 10")
                return None
            
            # Parse threshold values
            low_clear = float(self.low_clear_field.value)
            high_clear = float(self.high_clear_field.value)
            danger_cut = float(self.danger_cut_field.value)
            
            # Validate thresholds
            if not (0 < low_clear < high_clear < 1):
                print("Thresholds must satisfy: 0 < low_clear < high_clear < 1")
                return None
            
            if not (0 < danger_cut < 1):
                print("Danger threshold must be between 0 and 1")
                return None
            
            # Parse rescue weights (format: "w1,w2")
            rescue_weight_parts = self.rescue_weights_field.value.split(",")
            if len(rescue_weight_parts) != 2:
                print("Rescue weights must be two comma-separated values")
                return None
                
            w1 = int(rescue_weight_parts[0])
            w2 = int(rescue_weight_parts[1])
            rescue_shape_weights = [w1, w2] + [0] * 9  # Zero weights for remaining shapes
            
            # Parse size caps (format: "c1,c2,c3,c4,c5,c6,c7,c8,c9,c10")
            size_cap_parts = self.size_caps_field.value.split(",")
            if len(size_cap_parts) != 10:
                print("Size caps must have 10 comma-separated values")
                return None
                
            size_caps = [int(cap) for cap in size_cap_parts]
            if not all(1 <= cap <= 10 for cap in size_caps):
                print("Size caps must be between 1 and 10")
                return None
            
            # Return combined configuration
            return {
                "dda_params": {
                    "metrics_dda": {
                        "initial_difficulty": initial_difficulty,
                        "low_clear": low_clear,
                        "high_clear": high_clear,
                        "danger_cut": danger_cut,
                        "rescue_shape_weights": rescue_shape_weights,
                        "size_caps": size_caps
                    }
                }
            }
            
        except (ValueError, IndexError) as e:
            print(f"Invalid configuration values: {e}")
            return None
```

### 8. Testing Considerations

- Test algorithm response to different player skill levels
- Verify appropriate difficulty ramping with the following scenarios:
  - Player consistently clearing lines (should increase difficulty)
  - Player struggling to clear lines (should decrease difficulty)
  - Player showing signs of frustration (should decrease difficulty more)
  - Player showing signs of boredom (should increase difficulty)
- Test rescue mechanism activation when board gets crowded
- Test emergency mode activation when no valid placements exist
- Measure how difficulty level changes throughout a typical game session

---

## Implementation Checklist

- [ ] Create `metrics_dda.py` with core algorithm implementation
- [ ] Create `metrics_dda_view.py` with UI configuration interface
- [ ] Add registration to DDA registry in both files
- [ ] Update imports in relevant `__init__.py` files
- [ ] Update DDA section to handle the new DDA option
- [ ] Add default configuration parameters to `config/defaults.py`
  ```python
  "dda_params": {
      # ... existing params ...
      "metrics_dda": {
          "initial_difficulty": 3,
          "low_clear": 0.30,
          "high_clear": 0.70,
          "danger_cut": 0.80,
          "rescue_shape_weights": [10, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          "size_caps": [3, 3, 3, 4, 4, 4, 5, 5, 5, 5]
      }
  }
  ```

## Summary and Comparison

### Key Advantages of the Metrics-Based DDA

1. **Holistic Player Experience Analysis**:
   Unlike the existing StaticDDA and ThresholdDDA, the Metrics-Based DDA considers multiple aspects of the player experience:
   - Performance metrics (clear rate)
   - Board state (danger, fragmentation)
   - Emotional state (frustrated, bored, calm)
   - Game phase (early, mid, late)

2. **Dynamic Difficulty Adjustment**:
   - Continuously adapts difficulty based on real-time performance
   - Maintains an appropriate challenge level throughout the game
   - Unlike ThresholdDDA which only changes at predefined score thresholds

3. **Rescue Mechanisms**:
   - Provides emergency rescue when the board becomes difficult
   - Can shift mid-tray to prevent frustration spikes
   - Proactively responds to potential failure states

4. **Player Emotion Awareness**:
   - Takes into account the player's emotional state
   - Decreases difficulty when player shows signs of frustration
   - Increases difficulty when player appears bored

### Integration with Existing Systems

This implementation leverages existing metrics systems already present in the game:
- Uses the MetricsManager for collecting and calculating performance data
- Works within the existing DDA framework (BaseDDAAlgorithm)
- Follows established UI patterns for configuration
- Compatible with both manual play and AI simulation modes

### Extensibility

The design allows for future enhancements:
- Additional difficulty adjustment factors can be added
- Emotional state detection could be improved with more complex algorithms
- The size caps and weights could be dynamically tuned based on collected player data
