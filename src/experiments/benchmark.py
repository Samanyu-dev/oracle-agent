"""
Benchmarking Suite for Oracle Agent.
Compares Deterministic, Bayesian, and RL agents across multiple metrics.
"""

import random
from typing import List, Dict, Callable, Optional
import numpy as np

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.grid_world import GridWorld
from agents.deterministic_agent import DeterministicAgent
from agents.bayesian_agent import BayesianAgent
from agents.rl_agent import RLAgent
from learning.q_learning import QLearningEngine
from utils.metrics import MetricsLogger, EpisodeMetrics
from config import BENCHMARK_EPISODES, BENCHMARK_SEEDS, MAX_LIVES
from grid_gen import generate_grid


def run_episode(agent, env: GridWorld, seed: int, max_steps: int = 300) -> EpisodeMetrics:
    """Run a single episode and return metrics."""
    env.reset()
    agent.reset()
    total_reward = 0.0
    steps = 0

    for _ in range(max_steps):
        action = agent.act(env)
        trans = env.step(action)
        total_reward += trans.reward
        steps += 1
        if trans.done:
            break

    success = env.agent_pos == env.goal and env.lives > 0
    stats = agent.get_stats()
    return EpisodeMetrics(
        agent_type=stats['agent_type'],
        success=success,
        steps=steps,
        lives_remaining=env.lives,
        total_reward=total_reward,
        time_units=env.time_units,
        turns=env.turns,
        scans=stats.get('scans', 0),
        final_score=env.get_score(),
        seed=seed,
    )


def benchmark_agents(n_episodes: int = BENCHMARK_EPISODES,
                     seeds: Optional[List[int]] = None,
                     train_rl: bool = True,
                     rl_episodes: int = 1000) -> MetricsLogger:
    """
    Run full benchmark comparing all agent types.
    """
    if seeds is None:
        seeds = BENCHMARK_SEEDS

    logger = MetricsLogger()
    print("=" * 60)
    print("  ORACLE AGENT BENCHMARKING SUITE")
    print("=" * 60)

    # --- Train RL Agent First ---
    rl_agent = None
    if train_rl:
        print("\n[Phase 1] Training RL Agent...")
        grid, _, _, _ = generate_grid()
        rl_agent = RLAgent(grid)

        def env_factory():
            g, _, _, _ = generate_grid()
            return GridWorld(g)

        rl_agent.train(env_factory, n_episodes=rl_episodes)
        rl_agent.save('models/q_table.json')
        print("[Phase 1] RL Training complete.\n")

    # --- Benchmarking ---
    print("[Phase 2] Running benchmark episodes...")
    for i in range(n_episodes):
        seed = random.choice(seeds)
        random.seed(seed)
        np.random.seed(seed)

        grid, _, _, _ = generate_grid()
        env = GridWorld(grid)

        # Deterministic
        det_agent = DeterministicAgent(grid)
        metrics = run_episode(det_agent, env, seed)
        logger.log(metrics)

        # Bayesian
        env = GridWorld(grid)
        bay_agent = BayesianAgent(grid)
        metrics = run_episode(bay_agent, env, seed)
        logger.log(metrics)

        # Bayesian + MCTS
        env = GridWorld(grid)
        bay_mcts_agent = BayesianAgent(grid, use_mcts=True)
        metrics = run_episode(bay_mcts_agent, env, seed)
        logger.log(metrics)

        # RL (if trained)
        if rl_agent is not None:
            env = GridWorld(grid)
            rl_eval = RLAgent(grid, pretrained_q=rl_agent.q_engine)
            metrics = run_episode(rl_eval, env, seed)
            logger.log(metrics)

        if (i + 1) % 50 == 0:
            print(f"  Completed {i+1}/{n_episodes} episodes...")

    print("\n[Phase 2] Benchmarking complete.\n")
    return logger


def print_benchmark_results(logger: MetricsLogger):
    """Pretty-print benchmark results."""
    summary = logger.summary()
    print("=" * 80)
    print("  BENCHMARK RESULTS")
    print("=" * 80)
    print(f"{'Agent':<20} {'Episodes':>10} {'Success%':>10} {'Avg Reward':>12} "
          f"{'Std Reward':>12} {'Avg Steps':>10} {'Avg Lives':>10} {'Avg Scans':>10}")
    print("-" * 80)
    for agent_type, stats in summary.items():
        print(f"{agent_type:<20} {stats['episodes']:>10} {stats['success_rate']:>9.1%} "
              f"{stats['avg_reward']:>11.2f} {stats['std_reward']:>11.2f} "
              f"{stats['avg_steps']:>9.1f} {stats['avg_lives']:>9.2f} {stats['avg_scans']:>9.1f}")
    print("=" * 80)


def hyperparameter_search(grid, n_trials: int = 20) -> Dict:
    """
    Grid search over A* heuristic weights and risk thresholds.
    """
    from config import HP_GRID_SEARCH
    from planning.astar import AStarPlanner

    best_params = None
    best_score = float('inf')
    results = []

    for hw in HP_GRID_SEARCH['heuristic_weight']:
        for rt in HP_GRID_SEARCH['risk_threshold']:
            scores = []
            for _ in range(n_trials):
                env = GridWorld(grid)
                planner = AStarPlanner(grid, heuristic_weight=hw, risk_threshold=rt)
                result = planner.plan()
                if result:
                    _, turns, time_u, lives = result
                    score = (turns + time_u) / max(1, lives)
                    scores.append(score)
                else:
                    scores.append(9999)

            avg_score = np.mean(scores)
            results.append({
                'heuristic_weight': hw,
                'risk_threshold': rt,
                'avg_score': avg_score,
            })

            if avg_score < best_score:
                best_score = avg_score
                best_params = {'heuristic_weight': hw, 'risk_threshold': rt}

    return {'best': best_params, 'results': results}
