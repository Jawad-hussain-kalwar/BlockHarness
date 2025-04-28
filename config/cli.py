# config/cli.py
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
            print(f"Error loading config: {e}")
    
    return args, config 