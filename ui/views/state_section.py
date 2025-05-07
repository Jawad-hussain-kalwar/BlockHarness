# ui/views/state_section.py
import pygame
from ui.colours import (
    SECTION_BG, SECTION_BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_WARNING, TEXT_DANGER
)
from ui.layout import (
    PADDING, DDA_WIDTH, SIM_WIDTH, GAME_WIDTH, STATE_WIDTH, SECTION_HEIGHT,
    SIDEBAR_WIDTH, SIDEBAR_PADDING, BORDER_RADIUS
)
from ui.debug import draw_debug_rect
from ui.font_manager import font_manager

class StateSection:
    """View for the Game State section that displays game state information."""
    
    def __init__(self, window_size, font, small_font):
        self.window_size = window_size
        self.font = font
        self.small_font = small_font
        
        # Create fonts with Ubuntu-Regular instead of default font
        self.title_font = font_manager.get_font('Ubuntu-Regular', 24)  # Doubled from 22 to 44
        self.value_font = font_manager.get_font('Ubuntu-Regular', 20)  # Doubled from 16 to 32
        
        # Initialize section rectangle with new layout constants
        x_origin = PADDING + DDA_WIDTH + PADDING + SIM_WIDTH + PADDING + GAME_WIDTH + PADDING
        y_origin = PADDING
        self.rect = pygame.Rect(x_origin, y_origin, STATE_WIDTH, SECTION_HEIGHT)
        
        # Scrolling state
        self.scroll_y = 0
        self.max_scroll_y = 0
        
        # Group metrics into categories
        self.metrics_groups = [
            {
                "title": "Game Analysis",
                "metrics": [
                    "best_fit_block",
                    "best_fit_position",
                    "clearable_lines",
                    "opportunity",
                    "num_game_over_blocks"
                ]
            },
            {
                "title": "Game State Metrics",
                "metrics": [
                    "imminent_threat",
                    "occupancy_ratio",
                    "fragmentation_count",
                    "largest_empty_region",
                    "danger_score",
                    "phase"
                ]
            },
            {
                "title": "Player State Metrics",
                "metrics": [
                    "move_count",
                    "lines_cleared",
                    "score",
                    "clear_rate",
                    "recent_clears",
                    "perf_band",
                    "player_level",
                    "emotional_state",
                    "placement_efficiency"
                ]
            },
            {
                "title": "Timing Metrics",
                "metrics": [
                    "time_per_move",
                    "avg_time_per_move"
                ]
            },
            {
                "title": "Mistake Metrics",
                "metrics": [
                    "mistake_flag",
                    "mistake_count",
                    "mistake_rate",
                    "mistake_sw"
                ]
            }
        ]
        
        # Labels for metrics (prettier display names)
        self.metric_labels = {
            "best_fit_block": "Best Fit Block",
            "best_fit_position": "Best Fit Position",
            "clearable_lines": "Clearable Lines",
            "opportunity": "Opportunity",
            "num_game_over_blocks": "Game Over Blocks",
            "imminent_threat": "Imminent Threat",
            "occupancy_ratio": "Occupancy Ratio",
            "fragmentation_count": "Fragmentation Count",
            "largest_empty_region": "Largest Empty Region",
            "danger_score": "Danger Score",
            "phase": "Game Phase",
            "move_count": "Moves",
            "lines_cleared": "Lines Cleared",
            "score": "Score",
            "clear_rate": "Clear Rate",
            "recent_clears": "Recent Line Clears",
            "perf_band": "Performance Band",
            "player_level": "Player Level",
            "emotional_state": "Emotional State",
            "placement_efficiency": "Placement Efficiency",
            "time_per_move": "Time Per Move (s)",
            "avg_time_per_move": "Avg Time Per Move (s)",
            "mistake_flag": "Mistake Flag",
            "mistake_count": "Mistake Count",
            "mistake_rate": "Mistake Rate",
            "mistake_sw": "Recent Mistakes (10 moves)"
        }
    
    def draw(self, surface, engine):
        """Draw the Game State section.
        
        Args:
            surface: Pygame surface to draw on
            engine: Game engine instance
        """
        # Draw section background
        pygame.draw.rect(surface, SECTION_BG, self.rect, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, SECTION_BORDER, self.rect, width=1, border_radius=BORDER_RADIUS)
        
        # Draw debug border if enabled
        draw_debug_rect(surface, self.rect, "state")
        
        # Draw section title
        title = self.title_font.render("Game State", True, TEXT_PRIMARY)
        title_x = self.rect.x + PADDING
        title_y = self.rect.y + PADDING
        surface.blit(title, (title_x, title_y))
        
        # Create a scrollable content area
        content_rect = pygame.Rect(
            self.rect.x + PADDING,
            self.rect.y + PADDING + title.get_height() + PADDING,
            self.rect.width - 2 * PADDING,
            self.rect.height - 2 * PADDING - title.get_height() - PADDING
        )
        
        # Get metrics data from engine
        metrics = engine.get_metrics()
        
        # Get viewable metrics configuration
        viewable_metrics = engine.config.get("viewable_metrics", {})
        
        # Draw metrics in groups with scrolling
        y_offset = content_rect.y - self.scroll_y
        
        # Draw each group
        for group in self.metrics_groups:
            # Track if any metrics in this group are visible
            group_has_visible_metrics = False
            
            # Check if any metrics in this group are viewable
            for metric_key in group["metrics"]:
                if metric_key in metrics and viewable_metrics.get(metric_key, True):
                    group_has_visible_metrics = True
                    break
            
            # Skip group if no visible metrics
            if not group_has_visible_metrics:
                continue
                
            # Draw group title
            group_title = self.font.render(group["title"], True, TEXT_PRIMARY)
            surface.blit(group_title, (content_rect.x, y_offset))
            y_offset += group_title.get_height() + 5
            
            # Draw metrics in this group
            for metric_key in group["metrics"]:
                # Only display metrics that are enabled in the config
                if metric_key in metrics and viewable_metrics.get(metric_key, True):
                    value = metrics[metric_key]
                    
                    # Format value based on type
                    if isinstance(value, bool):
                        value_str = "Yes" if value else "No"
                        # Use warning color for true imminent_threat or opportunity
                        value_color = TEXT_WARNING if value and (metric_key == "imminent_threat" or metric_key == "opportunity") else TEXT_SECONDARY
                    elif isinstance(value, (int, float)):
                        value_str = str(value)
                        # Use different colors based on danger thresholds
                        if metric_key == "danger_score":
                            danger_cut = engine.config["metrics_flow"]["danger_cut"]
                            value_color = TEXT_DANGER if value >= danger_cut else TEXT_SECONDARY
                        else:
                            value_color = TEXT_SECONDARY
                    elif isinstance(value, list):
                        # Format lists (like recent_clears) in a readable way
                        if metric_key == "recent_clears":
                            # Format as a sequence of numbers
                            value_str = " ".join(map(str, value))
                        else:
                            # Generic list formatting
                            value_str = str(value)
                        value_color = TEXT_SECONDARY
                    else:
                        value_str = str(value)
                        value_color = TEXT_SECONDARY
                    
                    # Draw metric label
                    label = self.value_font.render(f"{self.metric_labels.get(metric_key, metric_key)}:", True, TEXT_PRIMARY)
                    surface.blit(label, (content_rect.x + 10, y_offset))
                    
                    # Draw metric value
                    value_surf = self.value_font.render(value_str, True, value_color)
                    surface.blit(value_surf, (content_rect.x + content_rect.width - value_surf.get_width() - 10, y_offset))
                    
                    y_offset += value_surf.get_height() + 5
            
            # Add space between groups
            y_offset += 15
        
        # Calculate max scroll position
        self.max_scroll_y = max(0, y_offset - content_rect.height - content_rect.y)
        
        # Handle scrolling
        self._handle_scrolling(surface, content_rect)
    
    def _handle_scrolling(self, surface, content_rect):
        """Handle scrolling of metrics display."""
        # Only show scrollbar if content is scrollable
        if self.max_scroll_y > 0:
            # Draw scrollbar background
            scrollbar_bg_rect = pygame.Rect(
                self.rect.right - 15,
                content_rect.y,
                10,
                content_rect.height
            )
            pygame.draw.rect(surface, (50, 50, 50), scrollbar_bg_rect, border_radius=3)
            
            # Calculate scrollbar handle size and position
            visible_ratio = content_rect.height / (content_rect.height + self.max_scroll_y)
            handle_height = max(30, content_rect.height * visible_ratio)
            scroll_ratio = self.scroll_y / self.max_scroll_y if self.max_scroll_y > 0 else 0
            handle_pos = content_rect.y + scroll_ratio * (content_rect.height - handle_height)
            
            # Draw scrollbar handle
            scrollbar_handle_rect = pygame.Rect(
                self.rect.right - 15,
                handle_pos,
                10,
                handle_height
            )
            pygame.draw.rect(surface, (100, 100, 100), scrollbar_handle_rect, border_radius=3)
    
    def handle_event(self, event):
        """Handle events for the state section, like scrolling."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - 20)
                return True
            elif event.button == 5:  # Scroll down
                self.scroll_y = min(self.max_scroll_y, self.scroll_y + 20)
                return True
        return False 