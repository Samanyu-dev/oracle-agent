"""
Grid World Environment for Oracle Agent.
Handles state transitions, rewards, and episode lifecycle.
"""

import random
import numpy as np
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    GRID_ROWS, GRID_COLS,
    CELL_LAND, CELL_VOLCANO, CELL_WATER, CELL_BRICK, CELL_START, CELL_GOAL,
    MAX_LIVES, WALK_TIME_COST, JUMP_TIME_COST, TURN_COST,
    HAZARD_RATIO, LAND_RATIO, PATH_VOLCANOES, PATH_WATERS,
    UTILITY_GOAL, UTILITY_LIFE, UTILITY_TIME_PENALTY, UTILITY_HAZARD, UTILITY_SCAN_COST,
)


@dataclass
class Transition:
    """Result of taking an action in the environment."""
    next_state: Tuple[int, int]
    reward: float
    done: bool
    info: Dict


class GridWorld:
    """
    Fully observable or partially observable grid world.
    """

    ACTIONS = ['walk_n', 'walk_s', 'walk_e', 'walk_w',
               'jump_n', 'jump_s', 'jump_e', 'jump_w', 'scan']

    def __init__(self, grid: Optional[List[List[str]]] = None, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        if grid is None:
            from grid_gen import generate_grid
            self.grid, self.path, self.anchor1, self.anchor2 = generate_grid(GRID_ROWS, GRID_COLS)
        else:
            self.grid = grid
            self.path = []
            self.anchor1 = self.anchor2 = None

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)
        self.agent_pos = self.start
        self.lives = MAX_LIVES
        self.turns = 0
        self.time_units = 0
        self.scan_count = {}
        self.visited = set([self.start])

    # ── Core Physics ──────────────────────────────────────────

    def reset(self, new_grid: Optional[List[List[str]]] = None):
        """Reset the environment for a new episode."""
        if new_grid is not None:
            self.grid = new_grid
            self.rows = len(new_grid)
            self.cols = len(new_grid[0])
            self.goal = (self.rows - 1, self.cols - 1)
        self.agent_pos = self.start
        self.lives = MAX_LIVES
        self.turns = 0
        self.time_units = 0
        self.scan_count = {}
        self.visited = set([self.start])
        return self._get_state()

    def _get_state(self) -> Tuple[int, int]:
        return self.agent_pos

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def _cell_type(self, r: int, c: int) -> str:
        return self.grid[r][c]

    def _is_hazard(self, r: int, c: int) -> bool:
        return self.grid[r][c] in {CELL_VOLCANO, CELL_WATER}

    def _is_wall(self, r: int, c: int) -> bool:
        return self.grid[r][c] == CELL_BRICK

    # ── Action Execution ─────────────────────────────────────

    def step(self, action: str) -> Transition:
        """
        Execute an action. Returns (next_state, reward, done, info).
        """
        self.turns += TURN_COST
        info = {'action': action, 'took_damage': False, 'scanned': False}

        if action == 'scan':
            return self._execute_scan(info)

        # Parse direction
        if action.startswith('walk_'):
            dr, dc = self._dir_vec(action.split('_')[1])
            step_cost = WALK_TIME_COST
            nr, nc = self.agent_pos[0] + dr, self.agent_pos[1] + dc

            if not self._in_bounds(nr, nc) or self._is_wall(nr, nc):
                # Bounce: no move, still costs time
                self.time_units += step_cost
                reward = UTILITY_TIME_PENALTY * step_cost
                return Transition(self.agent_pos, reward, self.lives <= 0, info)

        elif action.startswith('jump_'):
            dr, dc = self._dir_vec(action.split('_')[1])
            step_cost = JUMP_TIME_COST
            mr, mc = self.agent_pos[0] + dr, self.agent_pos[1] + dc
            nr, nc = self.agent_pos[0] + 2*dr, self.agent_pos[1] + 2*dc

            if (not self._in_bounds(mr, mc) or not self._in_bounds(nr, nc) or
                self._is_wall(mr, mc) or self._is_wall(nr, nc)):
                # Illegal jump: bounce
                self.time_units += step_cost
                reward = UTILITY_TIME_PENALTY * step_cost
                return Transition(self.agent_pos, reward, self.lives <= 0, info)
        else:
            raise ValueError(f"Unknown action: {action}")

        # Execute move
        self.time_units += step_cost
        self.agent_pos = (nr, nc)
        self.visited.add(self.agent_pos)

        # Hazard check
        reward = UTILITY_TIME_PENALTY * step_cost
        if self._is_hazard(nr, nc):
            self.lives -= 1
            info['took_damage'] = True
            reward += UTILITY_HAZARD

        # Goal check
        done = False
        if self.agent_pos == self.goal:
            reward += UTILITY_GOAL + UTILITY_LIFE * self.lives
            done = True
        elif self.lives <= 0:
            done = True

        return Transition(self.agent_pos, reward, done, info)

    def _execute_scan(self, info: Dict) -> Transition:
        """Scan current cell — purely informational, costs time."""
        self.time_units += 1
        info['scanned'] = True
        cell = self.agent_pos
        self.scan_count[cell] = self.scan_count.get(cell, 0) + 1
        reward = UTILITY_SCAN_COST
        return Transition(self.agent_pos, reward, self.lives <= 0, info)

    def _dir_vec(self, direction: str) -> Tuple[int, int]:
        return {'n': (-1, 0), 's': (1, 0), 'e': (0, 1), 'w': (0, -1)}[direction]

    # ── Partial Observability ─────────────────────────────────

    def get_sensor_reading(self, pos: Optional[Tuple[int, int]] = None) -> Tuple[bool, bool]:
        """
        Returns noisy (thermal, seismic) reading for a cell.
        """
        if pos is None:
            pos = self.agent_pos
        r, c = pos
        cell_type = self.grid[r][c]

        thermal_true = (cell_type == CELL_VOLCANO)
        seismic_true = (cell_type == CELL_WATER)

        from config import P_THERMAL_GIVEN, P_SEISMIC_GIVEN

        if thermal_true:
            thermal = random.random() < P_THERMAL_GIVEN['lava']
        else:
            thermal = random.random() < P_THERMAL_GIVEN.get(cell_type.lower(), 0.1)

        if seismic_true:
            seismic = random.random() < P_SEISMIC_GIVEN['water']
        else:
            seismic = random.random() < P_SEISMIC_GIVEN.get(cell_type.lower(), 0.05)

        return thermal, seismic

    # ── Utility ───────────────────────────────────────────────

    def get_score(self) -> float:
        if self.lives <= 0:
            return float('inf')
        return (self.turns + self.time_units) / self.lives

    def clone(self) -> 'GridWorld':
        """Deep copy for Monte Carlo rollouts."""
        env = GridWorld.__new__(GridWorld)
        env.grid = [row[:] for row in self.grid]
        env.rows = self.rows
        env.cols = self.cols
        env.path = self.path[:]
        env.anchor1 = self.anchor1
        env.anchor2 = self.anchor2
        env.start = self.start
        env.goal = self.goal
        env.agent_pos = self.agent_pos
        env.lives = self.lives
        env.turns = self.turns
        env.time_units = self.time_units
        env.scan_count = dict(self.scan_count)
        env.visited = set(self.visited)
        return env
