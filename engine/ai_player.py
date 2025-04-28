# engine/ai_player.py
from copy import deepcopy


class AIPlayer:
    """Greedy heuristic: choose move that clears most lines now."""

    def choose(self, engine) -> tuple | None:
        best = None
        best_score = -1

        for r, c in engine.valid_moves():
            tmp = deepcopy(engine.board)
            tmp.place_block(engine.current_block, r, c)
            cleared = tmp.clear_full_lines()
            score = 100 * cleared + 50 * max(0, cleared - 1)

            if score > best_score:
                best_score = score
                best = (r, c)

        return best
