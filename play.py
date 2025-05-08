# play.py
from engine.game_controller import GameController

import argparse
import json
from config.defaults import CONFIG

def parse_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="BlockHarness - Pygame")
    parser.add_argument("--config", help="Path to config JSON file")
    args = parser.parse_args()
    
    # Load config
    config = CONFIG.copy()
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"[play.py][21] Error loading config: {e}")
    
    return args, config 

def main():
    # Parse command line arguments and get config
    args, config = parse_args()
        
    # Create the game controller
    controller = GameController(config)
    
    # Start the game loop
    controller.loop()

if __name__ == "__main__":
    main()