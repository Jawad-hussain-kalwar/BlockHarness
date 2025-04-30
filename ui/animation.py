# ui/animation.py
from typing import List, Tuple, Dict, Set, Optional
import time

class Animation:
    """Base class for animations"""
    def __init__(self, duration_ms: int = 500):
        self.duration_ms = max(0, duration_ms)  # Ensure non-negative duration
        self.start_time = None
        self.is_complete = False
    
    def start(self):
        """Start the animation"""
        # Mark animation as immediately complete if duration is 0
        if self.duration_ms == 0:
            self.is_complete = True
            return
            
        self.start_time = time.time()
        self.is_complete = False
        
    def update(self) -> bool:
        """Update animation state
        
        Returns:
            bool: True if animation is complete, False otherwise
        """
        # If duration is 0, animation is always complete
        if self.duration_ms == 0:
            self.is_complete = True
            return True
            
        if self.start_time is None:
            return False
            
        elapsed = (time.time() - self.start_time) * 1000
        if elapsed >= self.duration_ms:
            self.is_complete = True
            return True
        return False
    
    def get_progress(self) -> float:
        """Get animation progress as a value from 0.0 to 1.0"""
        # If duration is 0, animation is fully complete
        if self.duration_ms == 0:
            return 1.0
            
        if self.start_time is None:
            return 0.0
            
        elapsed = (time.time() - self.start_time) * 1000
        return min(1.0, elapsed / self.duration_ms)


class FadeoutAnimation(Animation):
    """Animation for fading out cleared lines"""
    def __init__(self, cells: Set[Tuple[int, int]], duration_ms: int = 500):
        super().__init__(duration_ms)
        self.cells = cells  # Set of (row, col) coordinates to animate
    
    def get_opacity(self) -> float:
        """Get current opacity value (1.0 to 0.0)"""
        # Immediately return 0 for zero-duration animations (simulation mode)
        if self.duration_ms == 0:
            return 0.0
            
        # Reverse the progress for fadeout (1.0 -> 0.0)
        return 1.0 - self.get_progress()


class AnimationManager:
    """Manages multiple animations"""
    def __init__(self):
        self.animations: List[Animation] = []
    
    def add_animation(self, animation: Animation) -> None:
        """Add and start a new animation"""
        # Skip zero-duration animations completely
        if animation.duration_ms == 0:
            # Zero-duration animations are already marked complete in their start() method
            return
            
        animation.start()
        self.animations.append(animation)
    
    def update(self) -> None:
        """Update all animations and remove completed ones"""
        self.animations = [anim for anim in self.animations if not anim.update()]
    
    def is_animating(self) -> bool:
        """Check if any animations are active"""
        return len(self.animations) > 0
    
    def get_cell_opacity(self, row: int, col: int) -> Optional[float]:
        """Get opacity for a specific cell if it's being animated
        
        Returns:
            float: Opacity value or None if cell is not animating
        """
        for anim in self.animations:
            if isinstance(anim, FadeoutAnimation) and (row, col) in anim.cells:
                return anim.get_opacity()
        return None 