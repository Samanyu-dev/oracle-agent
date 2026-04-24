"""
Monte Carlo Tree Search (MCTS) Planner for Oracle Agent.
Simulates rollouts to evaluate action sequences under uncertainty.
"""

import math
import random
import copy
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MC_ROLLOUTS, MC_HORIZON, MC_UCB_CONSTANT, MAX_LIVES
from env.grid_world import GridWorld
from belief.bayesian_update import BeliefEngine


@dataclass
class MCNode:
    """Node in the Monte Carlo search tree."""
    state: Tuple[int, int]          # (row, col)
    lives: int
    parent: Optional['MCNode'] = None
    action_taken: Optional[str] = None
    children: Dict[str, 'MCNode'] = field(default_factory=dict)
    visits: int = 0
    value: float = 0.0
    untried_actions: List[str] = field(default_factory=list)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def best_child(self, c: float = MC_UCB_CONSTANT) -> 'MCNode':
        """Select child with highest UCB1 score."""
        choices = []
        for child in self.children.values():
            if child.visits == 0:
                ucb = float('inf')
            else:
                ucb = (child.value / child.visits) + c * math.sqrt(math.log(self.visits) / child.visits)
            choices.append((ucb, child))
        return max(choices, key=lambda x: x[0])[1]


class MonteCarloPlanner:
    """
    Monte Carlo Tree Search planner for the Oracle agent.
    Uses cloned environments for fast rollouts.
    """

    def __init__(self, grid: List[List[str]], belief: Optional[BeliefEngine] = None,
                 n_rollouts: int = MC_ROLLOUTS, horizon: int = MC_HORIZON):
        self.grid = grid
        self.belief = belief
        self.n_rollouts = n_rollouts
        self.horizon = horizon
        self.rows = len(grid)
        self.cols = len(grid[0])

    def plan(self, env: GridWorld) -> Tuple[str, Dict]:
        """
        Run MCTS from current env state. Returns (best_action, stats).
        """
        actions = self._get_legal_actions(env)
        root = MCNode(
            state=env.agent_pos,
            lives=env.lives,
            untried_actions=actions[:]
        )

        for _ in range(self.n_rollouts):
            node = self._select(root)
            if not node.is_fully_expanded() and not self._is_terminal(node):
                node = self._expand(node)
            reward = self._simulate(node)
            self._backpropagate(node, reward)

        # Choose best action by visit count
        if not root.children:
            return random.choice(actions), {'visits': 0, 'value': 0}

        best_action = max(root.children.items(), key=lambda x: x[1].visits)[0]
        stats = {
            'visits': root.children[best_action].visits,
            'value': root.children[best_action].value,
            'action_values': {a: n.value / max(1, n.visits) for a, n in root.children.items()}
        }
        return best_action, stats

    def _select(self, node: MCNode) -> MCNode:
        """Traverse tree using UCB1 until leaf."""
        while node.is_fully_expanded() and not self._is_terminal(node) and node.children:
            node = node.best_child()
        return node

    def _expand(self, node: MCNode) -> MCNode:
        """Add one child for an untried action."""
        action = node.untried_actions.pop()
        # We don't know the exact outcome, so we approximate with env clone
        child = MCNode(
            state=node.state,  # Simplified: actual state resolved in simulation
            lives=node.lives,
            parent=node,
            action_taken=action,
            untried_actions=[]
        )
        node.children[action] = child
        return child

    def _simulate(self, node: MCNode) -> float:
        """Rollout from node with random policy."""
        # Clone environment
        env_copy = self._make_env_from_node(node)
        total_reward = 0.0
        gamma = 1.0

        for _ in range(self.horizon):
            if env_copy.lives <= 0 or env_copy.agent_pos == env_copy.goal:
                break
            actions = self._get_legal_actions(env_copy)
            if not actions:
                break
            action = self._rollout_policy(env_copy, actions)
            trans = env_copy.step(action)
            total_reward += gamma * trans.reward
            gamma *= 0.95
            if trans.done:
                break

        return total_reward

    def _backpropagate(self, node: MCNode, reward: float):
        """Propagate reward up the tree."""
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent

    def _is_terminal(self, node: MCNode) -> bool:
        return node.lives <= 0 or node.state == (self.rows - 1, self.cols - 1)

    def _get_legal_actions(self, env: GridWorld) -> List[str]:
        """Legal actions from current env state."""
        actions = []
        r, c = env.agent_pos
        for d in ['n', 's', 'e', 'w']:
            dr, dc = {'n': (-1,0), 's': (1,0), 'e': (0,1), 'w': (0,-1)}[d]
            nr, nc = r + dr, c + dc
            if env._in_bounds(nr, nc) and not env._is_wall(nr, nc):
                actions.append(f'walk_{d}')
            mr, mc = r + dr, c + dc
            jr, jc = r + 2*dr, c + 2*dc
            if (env._in_bounds(mr, mc) and env._in_bounds(jr, jc) and
                not env._is_wall(mr, mc) and not env._is_wall(jr, jc)):
                actions.append(f'jump_{d}')
        actions.append('scan')
        return actions

    def _rollout_policy(self, env: GridWorld, actions: List[str]) -> str:
        """Smart rollout: prefer moves toward goal, avoid scan."""
        # Bias: don't scan during rollout (too expensive)
        move_actions = [a for a in actions if a != 'scan']
        if not move_actions:
            return 'scan'

        # Weight by distance to goal
        r, c = env.agent_pos
        gr, gc = env.goal
        weights = []
        for a in move_actions:
            d = a.split('_')[1]
            dr, dc = {'n': (-1,0), 's': (1,0), 'e': (0,1), 'w': (0,-1)}[d]
            if 'jump' in a:
                dr, dc = dr * 2, dc * 2
            nr, nc = r + dr, c + dc
            dist = abs(nr - gr) + abs(nc - gc)
            weights.append(1.0 / (1 + dist))

        total = sum(weights)
        probs = [w / total for w in weights]
        return random.choices(move_actions, weights=probs, k=1)[0]

    def _make_env_from_node(self, node: MCNode) -> GridWorld:
        """Reconstruct environment from node state."""
        env = GridWorld.__new__(GridWorld)
        env.grid = [row[:] for row in self.grid]
        env.rows = self.rows
        env.cols = self.cols
        env.path = []
        env.anchor1 = env.anchor2 = None
        env.start = (0, 0)
        env.goal = (self.rows - 1, self.cols - 1)
        env.agent_pos = node.state
        env.lives = node.lives
        env.turns = 0
        env.time_units = 0
        env.scan_count = {}
        env.visited = {node.state}
        return env
