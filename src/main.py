"""
Oracle Agent: Unified Main Entry Point
Supports demonstration, training, and benchmarking modes.
"""

import os
import sys
import argparse
import random

try:
    import numpy as np
except ImportError:
    np = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from env.grid_world import GridWorld
from agents.deterministic_agent import DeterministicAgent
from agents.bayesian_agent import BayesianAgent
from agents.rl_agent import RLAgent
from learning.q_learning import QLearningEngine
from experiments.benchmark import benchmark_agents, print_benchmark_results, run_episode
from visualize.plots import plot_reward_curve, plot_success_rate, plot_benchmark_comparison
from utils.metrics import MetricsLogger, EpisodeMetrics
from config import RL_EPISODES, BENCHMARK_EPISODES, OUTPUT_DIR, FIGURES_DIR
from grid_gen import generate_grid


def demo_deterministic(seed: int = 42):
    """Run a single demonstration episode with the deterministic agent."""
    print("\n" + "=" * 60)
    print("  DEMONSTRATION: Deterministic Agent (Perfect Sensors)")
    print("=" * 60)
    random.seed(seed)
    np.random.seed(seed)

    grid, path, a1, a2 = generate_grid()
    env = GridWorld(grid)
    agent = DeterministicAgent(grid)

    print(f"Grid generated: {env.rows}x{env.cols}")
    print(f"Safe path length: {len(path)} cells")

    steps = 0
    while True:
        action = agent.act(env)
        trans = env.step(action)
        steps += 1
        if trans.done or steps > 200:
            break

    print(f"\nResults:")
    print(f"  Success: {env.agent_pos == env.goal}")
    print(f"  Steps: {steps}")
    print(f"  Lives remaining: {env.lives}")
    print(f"  Final score: {env.get_score():.3f}")
    print(f"  Agent stats: {agent.get_stats()}")


def demo_bayesian(use_mcts: bool = False, seed: int = 42):
    """Run a single demonstration episode with the Bayesian agent."""
    label = "Bayesian+MCTS" if use_mcts else "Bayesian"
    print(f"\n{'=' * 60}")
    print(f"  DEMONSTRATION: {label} Agent (Noisy Sensors)")
    print("=" * 60)
    random.seed(seed)
    np.random.seed(seed)

    grid, path, a1, a2 = generate_grid()
    env = GridWorld(grid)
    agent = BayesianAgent(grid, use_mcts=use_mcts)

    print(f"Grid generated: {env.rows}x{env.cols}")

    steps = 0
    belief_history = []
    while True:
        action = agent.act(env)
        trans = env.step(action)
        steps += 1

        # Record belief state
        belief_history.append({
            'step': steps,
            'beliefs': agent.belief.to_array()
        })

        if trans.done or steps > 300:
            break

    print(f"\nResults:")
    print(f"  Success: {env.agent_pos == env.goal}")
    print(f"  Steps: {steps}")
    print(f"  Lives remaining: {env.lives}")
    print(f"  Scans performed: {agent.stats['scans']}")
    print(f"  Final score: {env.get_score():.3f}")
    print(f"  Agent stats: {agent.get_stats()}")

    # Plot belief evolution
    try:
        from visualize.plots import plot_belief_evolution
        os.makedirs(FIGURES_DIR, exist_ok=True)
        plot_belief_evolution(belief_history, os.path.join(FIGURES_DIR, f'belief_evolution_{label.lower()}.png'))
    except ImportError as e:
        print(f"[Plot] Skipped belief evolution plot: {e}")


def train_rl(n_episodes: int = RL_EPISODES, save_path: str = 'models/q_table.json'):
    """Train the RL agent and plot training curves."""
    print("\n" + "=" * 60)
    print(f"  TRAINING: RL Agent ({n_episodes} episodes)")
    print("=" * 60)

    grid, _, _, _ = generate_grid()
    rl_agent = RLAgent(grid)

    def env_factory():
        g, _, _, _ = generate_grid()
        return GridWorld(g)

    rl_agent.train(env_factory, n_episodes=n_episodes)
    rl_agent.save(save_path)

    # Plot training curves
    try:
        os.makedirs(FIGURES_DIR, exist_ok=True)
        plot_reward_curve(rl_agent.episode_rewards, path=os.path.join(FIGURES_DIR, 'rl_reward_curve.png'))
        successes = [r > 0 for r in rl_agent.episode_rewards]
        plot_success_rate(successes, path=os.path.join(FIGURES_DIR, 'rl_success_rate.png'))
    except ImportError as e:
        print(f"[Plot] Skipped training curves: {e}")

    print(f"\n[Train] Model saved to {save_path}")
    print(f"[Train] Final epsilon: {rl_agent.q_engine.epsilon:.4f}")
    print(f"[Train] Q-table size: {len(rl_agent.q_engine.q_table)} states")


def run_benchmark(n_episodes: int = BENCHMARK_EPISODES,
                  train_rl_first: bool = True,
                  rl_episodes: int = 500):
    """Run full benchmark suite."""
    logger = benchmark_agents(
        n_episodes=n_episodes,
        train_rl=train_rl_first,
        rl_episodes=rl_episodes
    )

    print_benchmark_results(logger)

    # Save results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logger.to_json(os.path.join(OUTPUT_DIR, 'benchmark_results.json'))

    # Plot comparison
    try:
        summary = logger.summary()
        plot_benchmark_comparison(summary, path=os.path.join(FIGURES_DIR, 'benchmark_comparison.png'))
        print(f"\n[Benchmark] Figures saved to {FIGURES_DIR}/")
    except ImportError as e:
        print(f"[Plot] Skipped benchmark comparison plot: {e}")

    print(f"\n[Benchmark] Results saved to outputs/benchmark_results.json")


def demo_rl(seed: int = 42, model_path: str = 'models/q_table.json'):
    """Run a demonstration with a trained RL agent."""
    print("\n" + "=" * 60)
    print("  DEMONSTRATION: RL Agent (Trained Policy)")
    print("=" * 60)
    random.seed(seed)
    np.random.seed(seed)

    grid, path, a1, a2 = generate_grid()
    env = GridWorld(grid)

    # Load or create RL agent
    q_engine = QLearningEngine()
    if os.path.exists(model_path):
        q_engine.load(model_path)
        print(f"[RL] Loaded model from {model_path}")
    else:
        print(f"[RL] No model found at {model_path}, using untrained agent")

    agent = RLAgent(grid, pretrained_q=q_engine)
    agent.reset()

    steps = 0
    total_reward = 0.0
    while True:
        action = agent.act(env, training=False)
        trans = env.step(action)
        total_reward += trans.reward
        steps += 1
        if trans.done or steps > 300:
            break

    print(f"\nResults:")
    print(f"  Success: {env.agent_pos == env.goal}")
    print(f"  Steps: {steps}")
    print(f"  Total reward: {total_reward:.2f}")
    print(f"  Lives remaining: {env.lives}")
    print(f"  Final score: {env.get_score():.3f}")


def main():
    parser = argparse.ArgumentParser(
        description='Oracle Agent: Advanced Grid Navigation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode demo_deterministic --seed 42
  python main.py --mode demo_bayesian --mcts
  python main.py --mode train_rl --rl_episodes 2000
  python main.py --mode benchmark --n_episodes 200 --rl_episodes 500
  python main.py --mode all
        """
    )
    parser.add_argument('--mode', type=str, default='all',
                        choices=['demo_deterministic', 'demo_bayesian', 'demo_rl',
                                 'train_rl', 'benchmark', 'all'],
                        help='Execution mode')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--mcts', action='store_true', help='Enable MCTS for Bayesian agent')
    parser.add_argument('--n_episodes', type=int, default=BENCHMARK_EPISODES,
                        help='Number of benchmark episodes')
    parser.add_argument('--rl_episodes', type=int, default=RL_EPISODES,
                        help='Number of RL training episodes')
    parser.add_argument('--model_path', type=str, default='models/q_table.json',
                        help='Path to saved RL model')

    args = parser.parse_args()

    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs('models', exist_ok=True)

    if args.mode == 'demo_deterministic' or args.mode == 'all':
        demo_deterministic(seed=args.seed)

    if args.mode == 'demo_bayesian' or args.mode == 'all':
        demo_bayesian(use_mcts=args.mcts, seed=args.seed)

    if args.mode == 'train_rl' or args.mode == 'all':
        train_rl(n_episodes=args.rl_episodes, save_path=args.model_path)

    if args.mode == 'demo_rl' or args.mode == 'all':
        demo_rl(seed=args.seed, model_path=args.model_path)

    if args.mode == 'benchmark' or args.mode == 'all':
        run_benchmark(n_episodes=args.n_episodes,
                      train_rl_first=True,
                      rl_episodes=args.rl_episodes)

    print("\n" + "=" * 60)
    print("  ORACLE AGENT: Execution Complete")
    print("=" * 60)


if __name__ == '__main__':
    main()
