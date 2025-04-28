# simulator.py
from statistics import mean

from engine.game_engine import GameEngine
from engine.ai_player import AIPlayer
from shapes import SHAPES


CONFIG = {
    "shapes": SHAPES,
    "shape_weights": [2, 2, 2, 2, 1, 1, 1, 1],           # initial bias
    "difficulty_thresholds": [
        (1000, [1, 2, 2, 2, 2, 2, 2, 3]),                # harder
        (3000, [1, 1, 2, 3, 3, 3, 3, 4]),                # hardest
    ],
}


def run_single():
    engine = GameEngine(CONFIG)
    ai = AIPlayer()

    engine.spawn()
    moves = 0
    while not engine.no_move_left():
        move = ai.choose(engine)
        if move is None:
            break
        engine.place(*move)
        moves += 1
        engine.spawn()

    return engine.score, moves, engine.lines


if __name__ == "__main__":
    results = [run_single() for _ in range(20)]
    scores, moves, lines = zip(*results)
    print(f"Average score: {mean(scores):.1f}")
    print(f"Average moves: {mean(moves):.1f}")
    print(f"Average lines: {mean(lines):.1f}")
