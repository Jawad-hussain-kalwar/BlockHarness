# simulator.py
from statistics import mean
from typing import List, Tuple, Dict
import time

from controllers.ai_controller import AIController
from engine.shapes import SHAPES


CONFIG = {
    "shapes": SHAPES,
    "shape_weights": [2, 2, 2, 2, 1, 1, 1, 1],           # initial bias
    "difficulty_thresholds": [
        (1000, [1, 2, 2, 2, 2, 2, 2, 3]),                # harder
        (3000, [1, 1, 2, 3, 3, 3, 3, 4]),                # hardest
    ],
}


def run_single() -> Tuple[int, int, int]:
    """Run a single simulation and return the results.
    
    Returns:
        Tuple of (score, moves, lines)
    """
    # Create AI controller with the configuration
    controller = AIController(CONFIG)
    
    # Run the simulation until game over
    results = controller.run_simulation()
    
    return (
        results["score"],
        results["blocks_placed"],
        results["lines"]
    )


def run_multiple(runs: int = 20) -> Dict:
    """Run multiple simulations and return statistics.
    
    Args:
        runs: Number of simulations to run
        
    Returns:
        Dictionary with statistics
    """
    start_time = time.time()
    
    results = [run_single() for _ in range(runs)]
    scores, moves, lines = zip(*results)
    
    end_time = time.time()
    
    return {
        "scores": {
            "mean": mean(scores),
            "min": min(scores),
            "max": max(scores)
        },
        "moves": {
            "mean": mean(moves),
            "min": min(moves),
            "max": max(moves)
        },
        "lines": {
            "mean": mean(lines),
            "min": min(lines),
            "max": max(lines)
        },
        "time": end_time - start_time,
        "runs": runs
    }


if __name__ == "__main__":
    stats = run_multiple(20)
    print(f"Average score: {stats['scores']['mean']:.1f}")
    print(f"Average moves: {stats['moves']['mean']:.1f}")
    print(f"Average lines: {stats['lines']['mean']:.1f}")
    print(f"Time taken: {stats['time']:.2f} seconds")
