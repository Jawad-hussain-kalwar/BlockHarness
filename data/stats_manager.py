# data/stats_manager.py
import os
import csv
import datetime
from typing import Dict, List, Union

class StatsManager:
    """Manages game statistics and saves them to a CSV file."""
    
    def __init__(self, stats_file: str = "game_stats.csv"):
        """Initialize the stats manager.
        
        Args:
            stats_file: Name of the CSV file for stats (will be stored in the data directory)
        """
        self.data_dir = os.path.dirname(os.path.abspath(__file__))
        self.stats_file = os.path.join(self.data_dir, stats_file)
        
        # Create the CSV file if it doesn't exist
        if not os.path.exists(self.stats_file):
            self._create_stats_file()
    
    def _create_stats_file(self) -> None:
        """Create the stats CSV file with headers."""
        with open(self.stats_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['timestamp', 'score', 'lines', 'blocks_placed'])
    
    def save_stats(self, stats: Dict[str, Union[int, float]]) -> None:
        """Save game statistics to the CSV file.
        
        Args:
            stats: Dictionary containing game statistics (score, lines, blocks_placed)
        """
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare row data
        row = [
            timestamp,
            stats.get('score', 0),
            stats.get('lines', 0),
            stats.get('blocks_placed', 0)
        ]
        
        # Append to CSV file
        with open(self.stats_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)
    
    def get_stats(self) -> List[Dict[str, Union[str, int, float]]]:
        """Get all stats from the CSV file.
        
        Returns:
            List of dictionaries containing game statistics
        """
        stats = []
        
        if not os.path.exists(self.stats_file):
            return stats
            
        with open(self.stats_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert numeric values
                for key in ['score', 'lines', 'blocks_placed']:
                    if key in row:
                        row[key] = int(row[key])
                stats.append(row)
        
        return stats 