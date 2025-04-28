# play.py
from config.cli import parse_args
from controllers.simulation_controller import SimulationController

def main():
    # Parse command line arguments and get config
    args, config = parse_args()
    
    # Create the game controller
    controller = SimulationController(config)
    
    # Start the game loop
    controller.loop()

if __name__ == "__main__":
    main() 