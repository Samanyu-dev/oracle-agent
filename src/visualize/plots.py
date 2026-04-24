"""
Visualization suite for Oracle Agent benchmarking and training.
Generates publication-quality plots for analysis.
Gracefully handles missing matplotlib.
"""

import os
import random
from typing import List, Dict, Optional

try:
    import numpy as np
except ImportError:
    np = None

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    REWARD_CURVE_PNG, SUCCESS_RATE_PNG,
    BELIEF_EVOLUTION_PNG, BENCHMARK_TABLE_PNG,
    FIGURES_DIR,
)


def _check_deps():
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "Matplotlib is required for plotting. "
            "Install with: pip install matplotlib"
        )
    if np is None:
        raise ImportError(
            "NumPy is required for plotting. "
            "Install with: pip install numpy"
        )


def plot_reward_curve(rewards: List[float], window: int = 100, path: str = REWARD_CURVE_PNG):
    """Plot training reward curve with moving average."""
    _check_deps()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    episodes = np.arange(1, len(rewards) + 1)
    ax.plot(episodes, rewards, alpha=0.3, color='steelblue', label='Raw Reward')

    if len(rewards) >= window:
        moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
        ax.plot(episodes[window-1:], moving_avg, color='darkred', linewidth=2,
                label=f'Moving Average ({window})')

    ax.set_xlabel('Episode', fontsize=12)
    ax.set_ylabel('Total Reward', fontsize=12)
    ax.set_title('Q-Learning Training: Reward vs Episodes', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_success_rate(successes: List[bool], window: int = 100, path: str = SUCCESS_RATE_PNG):
    """Plot success rate over training."""
    _check_deps()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    episodes = np.arange(1, len(successes) + 1)
    if len(successes) >= window:
        success_window = []
        for i in range(window - 1, len(successes)):
            window_data = successes[i - window + 1:i + 1]
            success_window.append(sum(window_data) / window)
        ax.plot(episodes[window - 1:], success_window, color='green', linewidth=2)

    ax.set_xlabel('Episode', fontsize=12)
    ax.set_ylabel('Success Rate', fontsize=12)
    ax.set_title(f'Training Success Rate (Window={window})', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_benchmark_comparison(summary: Dict[str, Dict[str, float]], path: str = BENCHMARK_TABLE_PNG):
    """Bar chart comparing agent performance."""
    _check_deps()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    agents = list(summary.keys())
    metrics = ['success_rate', 'avg_reward', 'avg_lives']
    labels = ['Success Rate', 'Avg Reward', 'Avg Lives Remaining']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = ['#E63946', '#457B9D', '#2A9D8F', '#E9C46A']

    for idx, (metric, label) in enumerate(zip(metrics, labels)):
        values = [summary[a][metric] for a in agents]
        axes[idx].bar(agents, values, color=colors[:len(agents)])
        axes[idx].set_ylabel(label, fontsize=11)
        axes[idx].set_title(label, fontsize=12, fontweight='bold')
        axes[idx].tick_params(axis='x', rotation=15)
        if metric == 'success_rate':
            axes[idx].set_ylim(0, 1)

    plt.suptitle('Agent Performance Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_belief_evolution(belief_history: List[Dict], path: str = BELIEF_EVOLUTION_PNG):
    """
    Plot how belief entropy evolves over steps for a single episode.
    belief_history: list of {step: int, beliefs: 2D array of dicts}
    """
    _check_deps()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    steps = []
    avg_entropies = []
    max_entropies = []

    for record in belief_history:
        step = record['step']
        beliefs = record['beliefs']
        entropies = []
        for row in beliefs:
            for bp in row:
                h = 0.0
                for p in bp.values():
                    if p > 1e-10:
                        h -= p * np.log2(p)
                entropies.append(h)
        steps.append(step)
        avg_entropies.append(np.mean(entropies))
        max_entropies.append(np.max(entropies))

    ax.plot(steps, avg_entropies, label='Average Entropy', color='steelblue', linewidth=2)
    ax.fill_between(steps, avg_entropies, alpha=0.3)
    ax.plot(steps, max_entropies, label='Max Entropy', color='orange', linestyle='--')

    ax.set_xlabel('Step', fontsize=12)
    ax.set_ylabel('Entropy (bits)', fontsize=12)
    ax.set_title('Belief Entropy Evolution During Episode', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")
