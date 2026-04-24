"""
Deterministic Agent (Exercise 1 equivalent).
Perfect information + A* search.
"""

from typing import List, Tuple, Optional, Dict
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.grid_world import GridWorld
from planning.astar import AStarPlanner
from config import MAX_LIVES


class DeterministicAgent:
    """
    The All-Seeing Oracle. Perfect sensors, optimal planning.
    """

    def __init__(self, grid: List[List[str]]):
        self.grid = grid
        self.planner = AStarPlanner(grid)
        self.path: Optional[List[Tuple[int, int]]] = None
        self.plan_idx = 0
        self.stats = {
            'agent_type': 'Deterministic',
            'path_found': False,
            'steps': 0,
            'scans': 0,
        }

    def reset(self):
        self.plan_idx = 0
        self.stats = {
            'agent_type': 'Deterministic',
            'path_found': False,
            'steps': 0,
            'scans': 0,
        }

    def act(self, env: GridWorld) -> str:
        """Choose action for current timestep."""
        if self.path is None:
            result = self.planner.plan(start_lives=MAX_LIVES)
            if result:
                self.path, turns, time_u, lives = result
                self.stats['path_found'] = True
            else:
                # Fallback: random move
                actions = [a for a in env.ACTIONS if a != 'scan']
                return random.choice(actions) if actions else 'scan'

        if self.plan_idx >= len(self.path) - 1:
            return 'scan'  # Should be at goal

        current = self.path[self.plan_idx]
        nxt = self.path[self.plan_idx + 1]
        self.plan_idx += 1
        self.stats['steps'] += 1

        # Determine action type
        dr = nxt[0] - current[0]
        dc = nxt[1] - current[1]
        dist = abs(dr) + abs(dc)

        if dist == 1:
            action_base = 'walk'
        elif dist == 2:
            action_base = 'jump'
        else:
            raise ValueError(f"Invalid step: {current} -> {nxt}")

        direction = {(-1,0): 'n', (1,0): 's', (0,1): 'e', (0,-1): 'w',
                     (-2,0): 'n', (2,0): 's', (0,2): 'e', (0,-2): 'w'}[(dr, dc)]
        return f"{action_base}_{direction}"

    def get_stats(self) -> Dict:
        return self.stats.copy()
