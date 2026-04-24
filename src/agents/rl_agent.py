"""
Reinforcement Learning Agent for Oracle.
Integrates Q-Learning with Bayesian belief states for sample-efficient learning.
"""

import random
from typing import List, Tuple, Optional, Dict
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.grid_world import GridWorld
from belief.bayesian_update import BeliefEngine
from learning.q_learning import QLearningEngine
from planning.astar import AStarPlanner
from config import (
    MAX_LIVES, RL_EPISODES, RL_LEARNING_RATE, RL_DISCOUNT_FACTOR,
    UTILITY_GOAL, UTILITY_LIFE, UTILITY_TIME_PENALTY, UTILITY_HAZARD,
)


class RLAgent:
    """
    The Learning Oracle.
    Learns optimal policies through Q-learning while leveraging belief states.
    """

    def __init__(self, grid: List[List[str]], pretrained_q: Optional[QLearningEngine] = None):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.q_engine = pretrained_q or QLearningEngine(self.rows, self.cols)
        self.belief = BeliefEngine(self.rows, self.cols)
        self.planner = AStarPlanner(grid, belief_engine=self.belief)

        self.current_path: Optional[List[Tuple[int, int]]] = None
        self.plan_idx = 0
        self.episode_rewards: List[float] = []
        self.episode_lengths: List[int] = []
        self.stats = {
            'agent_type': 'RL-Q-Learning',
            'scans': 0,
            'steps': 0,
            'training_episodes': 0,
        }

    def reset(self):
        self.belief = BeliefEngine(self.rows, self.cols)
        self.planner = AStarPlanner(self.grid, belief_engine=self.belief)
        self.current_path = None
        self.plan_idx = 0
        self.stats = {
            'agent_type': 'RL-Q-Learning',
            'scans': 0,
            'steps': 0,
            'training_episodes': self.q_engine.epsilon,
        }

    def act(self, env: GridWorld, training: bool = False) -> str:
        """
        Select action using Q-learning policy.
        During training: epsilon-greedy with Q-updates.
        During evaluation: greedy Q-policy.
        """
        pos = env.agent_pos
        r, c = pos

        if pos == env.goal:
            return 'scan'

        # Update belief with sensor reading
        if env.scan_count.get(pos, 0) < 4:
            thermal, seismic = env.get_sensor_reading(pos)
            self.belief.update(r, c, thermal, seismic)

        # Get legal actions
        actions = self._get_legal_actions(env)
        if not actions:
            return 'scan'

        # Encode state with belief features
        state = self.q_engine.encode_state(
            pos, env.lives,
            belief_map=self.belief.to_array(),
            grid=self.grid
        )

        if training:
            action = self.q_engine.select_action(state, actions)
        else:
            # Greedy selection
            action = self.q_engine.select_action(state, actions)
            # Force epsilon=0 for pure exploitation
            if random.random() > 0.05:  # Small residual exploration
                q_values = {a: self.q_engine.q_table[state][a] for a in actions}
                action = max(q_values, key=q_values.get)

        self.stats['steps'] += 1
        if action == 'scan':
            self.stats['scans'] += 1
        return action

    def learn(self, env: GridWorld, state: Tuple, action: str, reward: float,
              next_pos: Tuple[int, int], next_lives: int, done: bool):
        """Perform Q-learning update after taking an action."""
        next_state = self.q_engine.encode_state(
            next_pos, next_lives,
            belief_map=self.belief.to_array(),
            grid=self.grid
        )
        next_actions = self._get_legal_actions_from_pos(next_pos, next_lives, env)
        self.q_engine.update(state, action, reward, next_state, next_actions, done)

    def train_episode(self, env: GridWorld, max_steps: int = 200) -> Tuple[float, bool, int]:
        """
        Run one training episode. Returns (total_reward, success, steps).
        """
        env.reset()
        self.reset()
        total_reward = 0.0
        steps = 0
        state = self.q_engine.encode_state(
            env.agent_pos, env.lives,
            belief_map=self.belief.to_array(),
            grid=self.grid
        )

        for _ in range(max_steps):
            actions = self._get_legal_actions(env)
            if not actions:
                break

            action = self.q_engine.select_action(state, actions)
            trans = env.step(action)

            # Learn from transition
            next_state = self.q_engine.encode_state(
                trans.next_state, env.lives,
                belief_map=self.belief.to_array(),
                grid=self.grid
            )
            next_actions = self._get_legal_actions(env)
            self.q_engine.update(state, action, trans.reward,
                                 next_state, next_actions, trans.done)

            total_reward += trans.reward
            state = next_state
            steps += 1

            if trans.done:
                break

        self.q_engine.decay_epsilon()
        self.episode_rewards.append(total_reward)
        self.episode_lengths.append(steps)
        success = env.agent_pos == env.goal and env.lives > 0
        return total_reward, success, steps

    def train(self, env_factory, n_episodes: int = RL_EPISODES):
        """
        Train over multiple episodes with fresh grids.
        env_factory: callable that returns a new GridWorld
        """
        print(f"[RL] Training for {n_episodes} episodes...")
        successes = 0
        for ep in range(n_episodes):
            env = env_factory()
            reward, success, steps = self.train_episode(env)
            if success:
                successes += 1
            if (ep + 1) % 200 == 0:
                sr = successes / 200
                avg_r = sum(self.episode_rewards[-200:]) / 200
                print(f"[RL] Episode {ep+1}/{n_episodes} | "
                      f"Success Rate: {sr:.2%} | Avg Reward: {avg_r:.2f} | "
                      f"Epsilon: {self.q_engine.epsilon:.3f}")
                successes = 0
        self.stats['training_episodes'] = n_episodes
        print("[RL] Training complete.")

    def save(self, path: str = 'models/q_table.json'):
        """Save learned policy."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.q_engine.save(path)

    def load(self, path: str = 'models/q_table.json'):
        """Load learned policy."""
        self.q_engine.load(path)

    def _get_legal_actions(self, env: GridWorld) -> List[str]:
        """Legal actions from current env state."""
        return self._get_legal_actions_from_pos(env.agent_pos, env.lives, env)

    def _get_legal_actions_from_pos(self, pos: Tuple[int, int], lives: int,
                                     env: GridWorld) -> List[str]:
        actions = []
        r, c = pos
        for d in ['n', 's', 'e', 'w']:
            dr, dc = {'n': (-1,0), 's': (1,0), 'e': (0,1), 'w': (0,-1)}[d]
            nr, nc = r + dr, c + dc
            if env._in_bounds(nr, nc) and not env._is_wall(nr, nc):
                # Skip if belief says very risky and we have alternatives
                if self.belief.get_risk(nr, nc) < 0.9 or lives > 1:
                    actions.append(f'walk_{d}')
            mr, mc = r + dr, c + dc
            jr, jc = r + 2*dr, c + 2*dc
            if (env._in_bounds(mr, mc) and env._in_bounds(jr, jc) and
                not env._is_wall(mr, mc) and not env._is_wall(jr, jc)):
                if self.belief.get_risk(jr, jc) < 0.9 or lives > 1:
                    actions.append(f'jump_{d}')
        # Only scan if uncertainty is high
        if self.belief.entropy(r, c) > 1.0 and env.scan_count.get(pos, 0) < 4:
            actions.append('scan')
        return actions if actions else ['scan']

    def get_stats(self) -> Dict:
        return self.stats.copy()
