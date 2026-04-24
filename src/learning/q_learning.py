"""
Q-Learning Engine for Oracle Agent.
Tabular Q-learning with epsilon-greedy exploration and adaptive state encoding.
"""

import random
import math
import json
import os
from typing import Dict, Tuple, List, Optional
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    RL_LEARNING_RATE, RL_DISCOUNT_FACTOR,
    RL_EPSILON_START, RL_EPSILON_END, RL_EPSILON_DECAY,
    GRID_ROWS, GRID_COLS, MAX_LIVES,
    TILE_ENCODING, CELL_LAND, CELL_VOLCANO, CELL_WATER, CELL_BRICK,
)


class QLearningEngine:
    """
    Tabular Q-Learning with belief-state augmentation.
    State = (row, col, lives, risk_level, nearest_wall_dist)
    """

    def __init__(self, rows: int = GRID_ROWS, cols: int = GRID_COLS,
                 alpha: float = RL_LEARNING_RATE,
                 gamma: float = RL_DISCOUNT_FACTOR,
                 epsilon: float = RL_EPSILON_START,
                 epsilon_end: float = RL_EPSILON_END,
                 epsilon_decay: float = RL_EPSILON_DECAY):
        self.rows = rows
        self.cols = cols
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        # Q-table: state -> action -> value
        self.q_table: Dict[Tuple, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.visit_counts: Dict[Tuple, int] = defaultdict(int)

    def encode_state(self, pos: Tuple[int, int], lives: int,
                     belief_map=None, grid=None) -> Tuple:
        """
        Encode state for tabular Q-learning.
        Includes position, lives, and coarse belief features.
        """
        r, c = pos
        features = [r, c, lives]

        if belief_map is not None and grid is not None:
            # Add coarse risk features for nearby cells
            risk_n = self._get_risk(belief_map, r - 1, c)
            risk_s = self._get_risk(belief_map, r + 1, c)
            risk_e = self._get_risk(belief_map, r, c + 1)
            risk_w = self._get_risk(belief_map, r, c - 1)
            features.extend([
                int(risk_n * 3), int(risk_s * 3),
                int(risk_e * 3), int(risk_w * 3)
            ])
        else:
            features.extend([0, 0, 0, 0])

        return tuple(features)

    def _get_risk(self, belief_map, r: int, c: int) -> float:
        if belief_map is None:
            return 0.0
        if 0 <= r < self.rows and 0 <= c < self.cols:
            bp = belief_map[r][c]
            return bp.get(CELL_VOLCANO, 0) + bp.get(CELL_WATER, 0)
        return 1.0  # Out of bounds = high risk

    def select_action(self, state: Tuple, actions: List[str],
                      temperature: float = 1.0) -> str:
        """
        Epsilon-greedy action selection with softmax temperature.
        """
        if not actions:
            raise ValueError("No actions available")

        self.visit_counts[state] += 1

        if random.random() < self.epsilon:
            return random.choice(actions)

        # Softmax over Q-values
        q_values = {a: self.q_table[state][a] for a in actions}
        max_q = max(q_values.values())

        # Boltzmann distribution
        exp_q = {a: math.exp((q - max_q) / temperature) for a, q in q_values.items()}
        total = sum(exp_q.values())
        probs = {a: exp_q[a] / total for a in actions}

        r = random.random()
        cumulative = 0.0
        for a in actions:
            cumulative += probs[a]
            if r <= cumulative:
                return a
        return actions[-1]

    def update(self, state: Tuple, action: str, reward: float,
               next_state: Tuple, next_actions: List[str], done: bool):
        """
        Q-learning update rule:
        Q(s,a) <- Q(s,a) + α * [r + γ * max Q(s',a') - Q(s,a)]
        """
        current_q = self.q_table[state][action]

        if done or not next_actions:
            target = reward
        else:
            next_qs = [self.q_table[next_state][a] for a in next_actions]
            target = reward + self.gamma * max(next_qs)

        self.q_table[state][action] = current_q + self.alpha * (target - current_q)

    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def get_value(self, state: Tuple) -> float:
        """Get maximum Q-value for a state."""
        if state not in self.q_table or not self.q_table[state]:
            return 0.0
        return max(self.q_table[state].values())

    def save(self, path: str):
        """Save Q-table to disk."""
        data = {
            'q_table': {str(k): v for k, v in self.q_table.items()},
            'epsilon': self.epsilon,
            'visit_counts': {str(k): v for k, v in self.visit_counts.items()},
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load(self, path: str):
        """Load Q-table from disk."""
        if not os.path.exists(path):
            return
        with open(path, 'r') as f:
            data = json.load(f)
        self.q_table = defaultdict(lambda: defaultdict(float))
        for k, v in data['q_table'].items():
            state = tuple(int(x) for x in k.strip('()').split(','))
            self.q_table[state] = defaultdict(float, v)
        self.epsilon = data.get('epsilon', self.epsilon)
        for k, v in data.get('visit_counts', {}).items():
            state = tuple(int(x) for x in k.strip('()').split(','))
            self.visit_counts[state] = v
