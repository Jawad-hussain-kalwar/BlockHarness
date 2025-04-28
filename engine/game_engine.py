# engine/game_engine.py
from typing import Dict, List, Tuple

from engine.board import Board
from engine.block_pool import BlockPool


class GameEngine:
    """Core game loop & scoring logic."""

    def __init__(self, config: Dict):
        self.cfg = config
        self.board = Board()
        self.score = 0
        self.lines = 0
        self.blocks_placed = 0

        self.pool = BlockPool(
            self.cfg["shapes"],
            self.cfg["shape_weights"]
        )
        self.current_block = None

    # ───────────────────────── game steps ──────────────────────────

    def spawn(self):
        self.current_block = self.pool.sample()

    def valid_moves(self):
        """Yield every (r,c) where the current block fits."""
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if self.board.can_place(self.current_block, r, c):
                    yield (r, c)

    def place(self, r: int, c: int):
        self.board.place_block(self.current_block, r, c)
        self.blocks_placed += 1
        lines = self.board.clear_full_lines()
        self.lines += lines

        # scoring
        if lines:
            self.score += 100 * lines + 50 * max(0, lines - 1)  # combo bonus
        else:
            self.score += 1

        self._maybe_update_difficulty()

    # ─────────────────────── difficulty ramp ───────────────────────

    def _maybe_update_difficulty(self):
        for thr, new_weights in self.cfg.get("difficulty_thresholds", []):
            if self.score >= thr:
                self.pool.weights = new_weights

    # ────────────────────────── termination ────────────────────────

    def no_move_left(self) -> bool:
        return not any(self.valid_moves())
