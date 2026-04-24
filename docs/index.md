---
layout: default
title: Oracle Agent
---

# 🔮 Oracle Agent

**Adaptive Grid Navigation with A* Search, Bayesian Inference, MCTS, and Q-Learning**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![AI](https://img.shields.io/badge/Search-A*_Search-FF6F00)]()
[![RL](https://img.shields.io/badge/Learning-Q--Learning-9C27B0)]()
[![MC](https://img.shields.io/badge/Planning-MCTS-2E7D32)]()
[![Status](https://img.shields.io/badge/Research_Grade-PUBLISHABLE-brightgreen)]()

---

## 🎬 Live Demos

| Deterministic Agent | Bayesian Agent | RL Agent Training |
|:---:|:---:|:---:|
| Perfect sensors, optimal path | Noisy sensors, belief maps | Learning over 3000 episodes |
| 100% success, 4 lives | 100% success, 4 lives | 31.5% → improving |

---

## 🧠 What It Does

Oracle navigates a hazardous 9×9 grid containing:
- 🔥 **Volcanoes** — lose 1 life on contact
- 🌊 **Water** — lose 1 life on contact  
- 🧱 **Brick Walls** — impassable
- 🟩 **Land** — safe terrain

The agent starts at `(0,0)` and must reach `(8,8)` while preserving its 4 lives.

---

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Sensors    │───▶│   Belief    │───▶│  Decision   │
│ (Thermal +  │    │   Engine    │    │   Engine    │
│  Seismic)   │    │  (Bayes)    │    │             │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                              │
                   ┌──────────────────────────┼──────────┐
                   ▼                          ▼          ▼
           ┌──────────────┐           ┌──────────────┐  ┌──────┐
           │  A* Planner  │           │ MCTS Planner │  │  Q   │
           │ (Determin.)  │           │ (Simulation) │  │Table │
           └──────────────┘           └──────────────┘  └──────┘
```

---

## 📊 Benchmark Results

| Agent | Success Rate | Avg Reward | Avg Steps | Avg Lives |
|-------|-------------|------------|-----------|-----------|
| **Deterministic** | **100%** | **+274** | 10 | **4.0** |
| **Bayesian** | **100%** | **+254** | 20 | **4.0** |
| **Bayesian+MCTS** | **99%** | +11 | 28 | 1.0 |
| **RL (untrained)** | **0%** | -114 | 7 | 0.0 |

*Benchmarked over 100 episodes on randomly generated grids.*

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Samanyu-dev/oracle-agent.git
cd oracle-agent

# Install dependencies
pip install -r requirements.txt

# Run a demo
python main.py --mode demo_deterministic --seed 42

# Run full benchmark
python main.py --mode benchmark --n_episodes 100
```

---

## 📁 Repository

🔗 **[View on GitHub](https://github.com/Samanyu-dev/oracle-agent)**

```
src/
├── config.py              # All hyperparameters
├── main.py                # Unified CLI entry point
├── env/grid_world.py      # Environment physics
├── belief/bayesian_update.py  # Probabilistic state estimation
├── planning/astar.py      # Life-aware A* search
├── planning/monte_carlo.py    # MCTS with UCB1
├── agents/                # Deterministic, Bayesian, RL agents
├── learning/q_learning.py # Tabular Q-learning engine
├── utils/metrics.py       # Benchmarking & logging
├── experiments/benchmark.py   # Full evaluation suite
└── visualize/plots.py     # Publication-quality plots
```

---

## 🧪 Experiments

1. **Deterministic vs Bayesian** — Perfect info guarantees success; partial observability requires smart scanning
2. **Information Gain vs Random** — Entropy-based scanning outperforms random by 40%
3. **RL Convergence** — Success rate increases from 0% → 31.5% over 3000 training episodes
4. **Cross-Episode Memory** — Transfer learning improves first-episode success by 15%

---

## 📚 References

1. Russell & Norvig, *AI: A Modern Approach* (4th Ed.)
2. Watkins & Dayan, "Q-Learning" (1992)
3. Kocsis & Szepesvári, "Bandit Based Monte-Carlo Planning" (2006)
4. Thrun, "Probabilistic Robotics" (2002)

---

<div align="center">

**Made with 🧠, 🐍, and a lot of ☕**

[⭐ Star on GitHub](https://github.com/Samanyu-dev/oracle-agent) · [🐛 Report Issue](https://github.com/Samanyu-dev/oracle-agent/issues)

</div>
