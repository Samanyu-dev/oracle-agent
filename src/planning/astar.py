"""
A* Search Planner with life-aware heuristics.
Supports both deterministic (perfect info) and belief-aware (partial info) modes.
"""

import heapq
import math
from typing import List, Tuple, Optional, Callable, Dict

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    GRID_ROWS, GRID_COLS,
    CELL_BRICK, CELL_VOLCANO, CELL_WATER,
    MAX_LIVES, WALK_TIME_COST, JUMP_TIME_COST, TURN_COST,
)


class AStarPlanner:
    """
    Life-aware A* planner.
    State = (row, col, lives_remaining)
    """

    def __init__(self, grid: List[List[str]],
                 belief_engine=None,
                 heuristic_weight: float = 0.1,
                 risk_threshold: float = 0.5):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.goal = (self.rows - 1, self.cols - 1)
        self.belief = belief_engine
        self.heuristic_weight = heuristic_weight
        self.risk_threshold = risk_threshold

    def _neighbors(self, r: int, c: int):
        """Yield valid neighbor moves."""
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            # Walk
            nr, nc = r + dr, c + dc
            if (0 <= nr < self.rows and 0 <= nc < self.cols and
                self.grid[nr][nc] != CELL_BRICK):
                if self.belief is None or self.belief.get_risk(nr, nc) <= self.risk_threshold:
                    yield (nr, nc, 'walk', WALK_TIME_COST)

            # Jump (2 cells, cannot jump over wall)
            mr, mc = r + dr, c + dc
            jr, jc = r + 2*dr, c + 2*dc
            if (0 <= mr < self.rows and 0 <= mc < self.cols and
                0 <= jr < self.rows and 0 <= jc < self.cols and
                self.grid[mr][mc] != CELL_BRICK and
                self.grid[jr][jc] != CELL_BRICK):
                if self.belief is None or self.belief.get_risk(jr, jc) <= self.risk_threshold:
                    yield (jr, jc, 'jump', JUMP_TIME_COST)

    def _heuristic(self, r: int, c: int, lives: int) -> float:
        """Admissible heuristic: minimum time to goal / lives."""
        gr, gc = self.goal
        manhattan = abs(r - gr) + abs(c - gc)
        min_time = math.ceil(manhattan / 2) * JUMP_TIME_COST
        life_pen = (MAX_LIVES - lives) * 4
        if lives <= 0:
            return float('inf')
        return (min_time + life_pen + manhattan) / lives

    def plan(self, start_lives: int = MAX_LIVES) -> Optional[Tuple[List[Tuple[int, int]], int, int, int]]:
        """
        Run A* search.
        Returns (path, turns, time_units, final_lives) or None.
        """
        start = (0, 0)
        heap = [(0.0, 0, 0, start_lives, start, [start])]
        best = {}

        while heap:
            priority, turns, time_u, lives, pos, path = heapq.heappop(heap)
            r, c = pos

            key = (r, c, lives)
            if key in best and best[key] <= (turns + time_u):
                continue
            best[key] = turns + time_u

            if pos == self.goal:
                return path, turns, time_u, lives

            if lives <= 0:
                continue

            for nr, nc, action, t_cost in self._neighbors(r, c):
                new_turns = turns + TURN_COST
                new_time = time_u + t_cost
                new_lives = lives

                # Hazard penalty
                if self.grid[nr][nc] in {CELL_VOLCANO, CELL_WATER}:
                    new_lives -= 1

                if new_lives <= 0:
                    continue

                new_score = (new_turns + new_time) / new_lives
                h = self._heuristic(nr, nc, new_lives)
                prio = new_score + h * self.heuristic_weight

                heapq.heappush(heap, (
                    prio, new_turns, new_time,
                    new_lives, (nr, nc), path + [(nr, nc)]
                ))

        return None

    def plan_with_expected_utility(self,
                                   utility_fn: Callable[[int, int, int, int, int], float]) -> Optional[Tuple]:
        """
        A* variant that uses expected utility instead of survival score.
        utility_fn(turns, time, lives, row, col) -> float (higher is better)
        """
        start = (0, 0)
        heap = [(-utility_fn(0, 0, MAX_LIVES, 0, 0), 0, 0, MAX_LIVES, start, [start])]
        best = {}

        while heap:
            neg_util, turns, time_u, lives, pos, path = heapq.heappop(heap)
            r, c = pos

            key = (r, c, lives)
            if key in best and best[key] <= turns + time_u:
                continue
            best[key] = turns + time_u

            if pos == self.goal:
                return path, turns, time_u, lives

            if lives <= 0:
                continue

            for nr, nc, action, t_cost in self._neighbors(r, c):
                new_turns = turns + TURN_COST
                new_time = time_u + t_cost
                new_lives = lives - (1 if self.grid[nr][nc] in {CELL_VOLCANO, CELL_WATER} else 0)

                if new_lives <= 0:
                    continue

                u = utility_fn(new_turns, new_time, new_lives, nr, nc)
                h = self._heuristic(nr, nc, new_lives)
                prio = -(u - h * self.heuristic_weight)

                heapq.heappush(heap, (prio, new_turns, new_time, new_lives, (nr, nc), path + [(nr, nc)]))

        return None
