"""
Metrics and logging utilities for benchmarking agents.
"""

import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np


@dataclass
class EpisodeMetrics:
    """Metrics for a single episode."""
    agent_type: str
    success: bool
    steps: int
    lives_remaining: int
    total_reward: float
    time_units: int
    turns: int
    scans: int
    final_score: float
    seed: int


class MetricsLogger:
    """Logs and aggregates episode metrics across agents."""

    def __init__(self):
        self.episodes: List[EpisodeMetrics] = []
        self.agent_stats: Dict[str, List[EpisodeMetrics]] = defaultdict(list)

    def log(self, metrics: EpisodeMetrics):
        self.episodes.append(metrics)
        self.agent_stats[metrics.agent_type].append(metrics)

    def summary(self) -> Dict[str, Dict[str, float]]:
        """Compute summary statistics per agent type."""
        summary = {}
        for agent_type, eps in self.agent_stats.items():
            successes = [e for e in eps if e.success]
            summary[agent_type] = {
                'episodes': len(eps),
                'success_rate': len(successes) / len(eps) if eps else 0,
                'avg_reward': np.mean([e.total_reward for e in eps]) if eps else 0,
                'std_reward': np.std([e.total_reward for e in eps]) if eps else 0,
                'avg_steps': np.mean([e.steps for e in eps]) if eps else 0,
                'avg_lives': np.mean([e.lives_remaining for e in eps]) if eps else 0,
                'avg_scans': np.mean([e.scans for e in eps]) if eps else 0,
                'best_reward': max([e.total_reward for e in eps]) if eps else 0,
                'worst_reward': min([e.total_reward for e in eps]) if eps else 0,
            }
        return summary

    def to_json(self, path: str):
        data = {
            'episodes': [asdict(e) for e in self.episodes],
            'summary': self.summary(),
        }
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def from_json(path: str) -> 'MetricsLogger':
        with open(path, 'r') as f:
            data = json.load(f)
        logger = MetricsLogger()
        for e in data['episodes']:
            logger.log(EpisodeMetrics(**e))
        return logger
