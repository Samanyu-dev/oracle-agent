"""
Bayesian Agent (Exercise 2 equivalent + enhancements).
Noisy sensors + belief updates + expected utility + information-theoretic scanning.
"""

import random
from typing import List, Tuple, Optional, Dict
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.grid_world import GridWorld
from belief.bayesian_update import BeliefEngine
from planning.astar import AStarPlanner
from planning.monte_carlo import MonteCarloPlanner
from config import (
    MAX_LIVES, MAX_SCANS_PER_CELL, RISK_THRESHOLD,
    UTILITY_GOAL, UTILITY_LIFE, UTILITY_TIME_PENALTY, UTILITY_HAZARD, UTILITY_SCAN_COST, UTILITY_INFO_GAIN,
)


class BayesianAgent:
    """
    The Blind Prophet. Operates under uncertainty with Bayesian inference,
    expected utility maximization, and smart scanning.
    """

    def __init__(self, grid: List[List[str]], use_mcts: bool = False):
        self.grid = grid
        self.belief = BeliefEngine(len(grid), len(grid[0]))
        self.planner = AStarPlanner(grid, belief_engine=self.belief)
        self.use_mcts = use_mcts
        if use_mcts:
            self.mcts = MonteCarloPlanner(grid, belief=self.belief)
        self.current_path: Optional[List[Tuple[int, int]]] = None
        self.plan_idx = 0
        self.scan_log: List[Dict] = []
        self.memory: Dict[Tuple[int, int], Dict[str, float]] = {}
        self.stats = {
            'agent_type': 'Bayesian' + ('+MCTS' if use_mcts else ''),
            'scans': 0,
            'steps': 0,
            'replans': 0,
        }

    def reset(self):
        self.belief = BeliefEngine(len(self.grid), len(self.grid[0]))
        if self.memory:
            self.belief.merge_memory(self.memory)
        self.planner = AStarPlanner(self.grid, belief_engine=self.belief)
        if self.use_mcts:
            self.mcts = MonteCarloPlanner(self.grid, belief=self.belief)
        self.current_path = None
        self.plan_idx = 0
        self.scan_log = []
        self.stats = {
            'agent_type': 'Bayesian' + ('+MCTS' if self.use_mcts else ''),
            'scans': 0,
            'steps': 0,
            'replans': 0,
        }

    def act(self, env: GridWorld) -> str:
        """Decide next action using belief + expected utility + info gain."""
        pos = env.agent_pos
        r, c = pos

        # If at goal, scan (idle)
        if pos == env.goal:
            return 'scan'

        # ── Smart Scan Decision ───────────────────────────────
        should_scan = self._should_scan(env, r, c)
        if should_scan:
            thermal, seismic = env.get_sensor_reading(pos)
            self.belief.update(r, c, thermal, seismic)
            self.scan_log.append({
                'pos': pos, 'thermal': thermal, 'seismic': seismic,
                'belief': self.belief.get_belief(r, c)
            })
            self.stats['scans'] += 1
            return 'scan'

        # ── Plan (replan if needed) ───────────────────────────
        if self.current_path is None or self.plan_idx >= len(self.current_path) - 1:
            self._replan()

        if self.current_path and self.plan_idx < len(self.current_path) - 1:
            current = self.current_path[self.plan_idx]
            nxt = self.current_path[self.plan_idx + 1]
            self.plan_idx += 1
            self.stats['steps'] += 1
            action = self._pos_to_action(current, nxt)

            # If MCTS is enabled, validate action
            if self.use_mcts and random.random() < 0.3:
                mcts_action, mcts_stats = self.mcts.plan(env)
                if mcts_action != 'scan':
                    action = mcts_action
            return action

        # Fallback: MCTS direct action
        if self.use_mcts:
            action, _ = self.mcts.plan(env)
            self.stats['steps'] += 1
            return action

        # Ultimate fallback: random legal move
        actions = [a for a in env.ACTIONS if a != 'scan']
        return random.choice(actions) if actions else 'scan'

    def _should_scan(self, env: GridWorld, r: int, c: int) -> bool:
        """
        Information-theoretic scan decision.
        Scan if:
        1. Cell hasn't been scanned AND entropy is high
        2. Expected information gain > threshold
        3. We're about to step into a risky cell
        """
        scans_done = self.belief.scan_counts.get((r, c), 0)
        if scans_done >= MAX_SCANS_PER_CELL:
            return False

        risk = self.belief.get_risk(r, c)
        entropy = self.belief.entropy(r, c)
        eig = self.belief.expected_information_gain(r, c)

        # High uncertainty on current cell
        if scans_done == 0 and entropy > 1.5:
            return True

        # About to move into unknown frontier
        if self.current_path and self.plan_idx < len(self.current_path) - 1:
            nxt = self.current_path[self.plan_idx + 1]
            nr, nc = nxt
            if self.belief.scan_counts.get(nxt, 0) < MAX_SCANS_PER_CELL:
                nxt_risk = self.belief.get_risk(nr, nc)
                if nxt_risk > 0.3 and self.belief.entropy(nr, nc) > 1.0:
                    # Scan the next cell before stepping
                    return False  # Will scan next cell, not current

        # Scan frontier cells before committing
        if eig > 0.5 and scans_done < 2:
            return True

        return False

    def _replan(self):
        """Recompute path with current beliefs."""
        result = self.planner.plan(start_lives=MAX_LIVES)
        if result:
            self.current_path, _, _, _ = result
            self.plan_idx = 0
            self.stats['replans'] += 1
        else:
            self.current_path = None

    def _pos_to_action(self, current: Tuple[int, int], nxt: Tuple[int, int]) -> str:
        dr = nxt[0] - current[0]
        dc = nxt[1] - current[1]
        dist = abs(dr) + abs(dc)
        base = 'jump' if dist == 2 else 'walk'
        direction = {(-1,0): 'n', (1,0): 's', (0,1): 'e', (0,-1): 'w',
                     (-2,0): 'n', (2,0): 's', (0,2): 'e', (0,-2): 'w'}[(dr, dc)]
        return f"{base}_{direction}"

    def update_memory(self, decay: float = 0.95):
        """Update cross-episode memory with learned hazard patterns."""
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                key = (r, c)
                if key not in self.memory:
                    self.memory[key] = self.belief.get_belief(r, c)
                else:
                    old = self.memory[key]
                    new = self.belief.get_belief(r, c)
                    for cell_type in old:
                        old[cell_type] = decay * old[cell_type] + (1 - decay) * new[cell_type]

    def get_stats(self) -> Dict:
        return self.stats.copy()
