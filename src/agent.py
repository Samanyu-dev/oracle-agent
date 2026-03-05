import heapq
import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

from config import (
    MAX_LIVES, WALK_TIME_COST, JUMP_TIME_COST, TURN_COST,
    CELL_LAND, CELL_VOLCANO, CELL_WATER, CELL_BRICK, CELL_START, CELL_GOAL,
)

HAZARD_CELLS = {CELL_VOLCANO, CELL_WATER}
SAFE_CELLS   = {CELL_LAND, CELL_START, CELL_GOAL}

@dataclass
class StepRecord:
    """One step in the simulation log (shared Ex1 & Ex2)."""
    step        : int
    from_cell   : Tuple[int,int]
    to_cell     : Tuple[int,int]
    action      : str            # 'walk' or 'jump'
    took_damage : bool
    lives       : int
    turns       : int
    time_units  : int
    score       : float
    beliefs     : Optional[List[List[Dict]]] = None   # Ex2 only
    scan_events : Optional[List[Dict]]       = None   # Ex2 only


@dataclass
class ScanRecord:
    """One sensor scan event (Ex2 only)."""
    cell      : Tuple[int,int]
    thermal   : bool
    seismic   : bool
    beliefs   : Dict[str,float]
    scan_num  : int
    turn_at   : int
class OracleAgentEx1:
    """
    Deterministic agent with perfect sensors.
    Uses A* to find the path that minimises score = (turns+time)/lives.
    (Lower score = better: fewer wasted actions, more lives preserved.)
    """

    def __init__(self, grid: List[List[str]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.goal = (self.rows-1, self.cols-1)

    # ── Sensors
    def thermal_sensor(self, r:int, c:int) -> bool:
        return self.grid[r][c] == CELL_VOLCANO

    def seismic_sensor(self, r:int, c:int) -> bool:
        return self.grid[r][c] == CELL_WATER

    def _cell_type(self, r:int, c:int) -> str:
        return self.grid[r][c]

    def _is_hazard(self, r:int, c:int) -> bool:
        return self.grid[r][c] in HAZARD_CELLS

    def _in_bounds(self, r:int, c:int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    # ── Neighbor generation
    def _neighbors(self, r:int, c:int):
        """
        Yields (nr, nc, action, time_cost, turn_cost).
        Walk: 1 cell, costs WALK_TIME_COST + TURN_COST.
        Jump: 2 cells (skip middle), costs JUMP_TIME_COST + TURN_COST.
        Cannot walk or jump INTO a brick wall.
        Cannot jump OVER a brick wall (middle cell must not be brick).
        If an invalid move is attempted (brick destination on walk):
            → costs only TURN_COST (bounce), no position change.
        """
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            # Walk
            nr, nc = r+dr, c+dc
            if self._in_bounds(nr, nc):
                if self.grid[nr][nc] != CELL_BRICK:
                    yield (nr, nc, 'walk', WALK_TIME_COST, TURN_COST)
                # brick walk → bounce, but we just skip it in planning
                # (handled by not yielding a valid move there)

            # Jump
            mr, mc = r+dr,   c+dc    # middle cell
            jr, jc = r+2*dr, c+2*dc  # landing cell
            if self._in_bounds(mr, mc) and self._in_bounds(jr, jc):
                if (self.grid[mr][mc] != CELL_BRICK and
                        self.grid[jr][jc] != CELL_BRICK):
                    yield (jr, jc, 'jump', JUMP_TIME_COST, TURN_COST)

    # ── Heuristic 
    def _heuristic(self, r:int, c:int, lives:int) -> float:
        """
        Admissible heuristic: minimum time to reach goal / current lives.
        Uses Manhattan distance / 2 (jump covers 2 cells in 3TU,
        walk covers 1 cell in 2TU; min per cell ≈ 1.5TU).
        Penalises low lives heavily.
        """
        gr, gc = self.goal
        manhattan = abs(r-gr) + abs(c-gc)
        min_time  = math.ceil(manhattan / 2) * JUMP_TIME_COST
        life_pen  = (MAX_LIVES - lives) * 4
        if lives <= 0:
            return float('inf')
        return (min_time + life_pen + manhattan) / lives

    # ── A* Search
    def a_star(self):
        """
        A* where state = (row, col, lives_remaining).
        Priority = estimated_score = (turns+time) / lives.
        Returns (path, total_turns, total_time, final_lives)
        or (None, ...) if no solution.
        """
        start = (0, 0)

        # heap: (priority, turns, time, lives, pos, path)
        heap = [(0.0, 0, 0, MAX_LIVES, start, [start])]
        best = {}   # state → best cost seen

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

            for nr, nc, action, t_cost, turn_cost in self._neighbors(r, c):
                new_turns = turns + turn_cost
                new_time  = time_u + t_cost
                new_lives = lives

                if self.grid[nr][nc] in HAZARD_CELLS:
                    new_lives -= 1

                if new_lives <= 0:
                    continue   # don't explore death states

                new_score = (new_turns + new_time) / new_lives
                h = self._heuristic(nr, nc, new_lives)
                prio = new_score + h * 0.1

                heapq.heappush(heap, (
                    prio, new_turns, new_time,
                    new_lives, (nr, nc), path + [(nr, nc)]
                ))

        return None, 0, 0, 0

    # ── Run simulation
    def run(self) -> Tuple[Optional[List[StepRecord]], Optional[List]]:
        """
        Find optimal path with A*, then simulate step by step.
        Returns (simulation_log, path) or (None, None).
        """
        path, _, _, _ = self.a_star()
        if path is None:
            print("[Ex1] No valid path found!")
            return None, None

        log   = []
        lives = MAX_LIVES
        turns = 0
        time_u = 0

        for i in range(len(path)-1):
            fc = path[i]
            tc = path[i+1]
            fr, ff = fc
            tr, tc_ = tc

            dist   = abs(tr-fr) + abs(tc_-ff)
            action = 'walk' if dist == 1 else 'jump'
            t_cost = WALK_TIME_COST if action == 'walk' else JUMP_TIME_COST

            turns  += TURN_COST
            time_u += t_cost

            cell_type   = self.grid[tr][tc_]
            took_damage = cell_type in HAZARD_CELLS
            if took_damage:
                lives -= 1

            score = (turns + time_u) / lives if lives > 0 else float('inf')

            log.append(StepRecord(
                step        = i+1,
                from_cell   = fc,
                to_cell     = tc,
                action      = action,
                took_damage = took_damage,
                lives       = lives,
                turns       = turns,
                time_units  = time_u,
                score       = score,
            ))

            if lives <= 0:
                print(f"[Ex1] Agent died at step {i+1}!")
                break

        return log, path


