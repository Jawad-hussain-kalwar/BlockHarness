# play.py
from config.cli import parse_args
from controllers.simulation_controller import SimulationController

def main():
    # Parse command line arguments and get config
    args, config = parse_args()
    
    # Example of how to customize which metrics are displayed
    # Uncomment the following section to see a customized view
    """
    # Hide some Game State metrics
    config["viewable_metrics"]["fragmentation_count"] = False 
    config["viewable_metrics"]["largest_empty_region"] = False
    
    # Hide some Player State metrics
    config["viewable_metrics"]["emotional_state"] = False
    config["viewable_metrics"]["placement_efficiency"] = False
    config["viewable_metrics"]["recent_clears"] = False
    
    # Hide all Mistake metrics for a cleaner view
    config["viewable_metrics"]["mistake_flag"] = False
    config["viewable_metrics"]["mistake_count"] = False
    config["viewable_metrics"]["mistake_rate"] = False
    config["viewable_metrics"]["mistake_sw"] = False
    """
    
    # Create the simulation controller (which extends game controller)
    controller = SimulationController(config)
    
    # Start the game loop
    controller.loop()

if __name__ == "__main__":
    main() 