---
title: Oracleagent
emoji: 🏆
colorFrom: purple
colorTo: indigo
sdk: gradio
sdk_version: "6.14.0"
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
---

<div align="center">

```
   ____  _   _  ___  _   _ _     _____   __
  / __ \| | | |/ _ \| | | | |   / _ \ \ / /
 | |  | | | | | | | | | | | |  | (_) \ V / 
 | |  | | | | | | | | | | | |   > _ < > <  
 | |__| | |_| | |_| | |_| | |___| (_) / . \ 
  \____/ \___/ \___/ \___/|_____\___/_/ \_\
```

# 🔮 ORACLE AGENT — Interactive AI Survival Simulation OS

**A cinematic command center for adaptive autonomous planning, probabilistic reasoning, and hazard survival.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![AI](https://img.shields.io/badge/Systems-A*_%2B_Bayesian-FF6F00)]()
[![RL](https://img.shields.io/badge/Learning-Q--Learning-9C27B0)]()
[![MC](https://img.shields.io/badge/Planning-MCTS-2E7D32)]()
[![Experience](https://img.shields.io/badge/Experience-Vercel_%2B_HF-7C4DFF)]()
[![License](https://img.shields.io/badge/License-MIT-000000.svg)](LICENSE)

*"This is not just pathfinding. This is an autonomous tactical intelligence system."*

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Platform Strategy](#platform-strategy)
- [Architecture](#architecture)
- [Agent Types](#agent-types)
- [Mathematical Foundations](#mathematical-foundations)
- [Experience Roadmap](#experience-roadmap)
- [Quick Start](#quick-start)
- [Experiments](#experiments)
- [Benchmarks](#benchmarks)
- [Visualization](#visualization)
- [Project Structure](#project-structure)
- [References](#references)

---

## Overview

Oracle is an advanced  built to feel like a **futuristic AI command center**. It operates in **partially observable hazardous environments** featuring volcanoes, water hazards, brick walls, and limited lives. The agent must reach the goal while balancing survival, uncertainty, and tactical decision-making.

This is not just a research demo. It is a foundation for an interactive experience with:

- cinematic grid-world simulation
- belief and uncertainty visualization
- interactive search and planning dashboards
- live reinforcement learning theater
- benchmark command centers

Oracle blends a **unified decision architecture** with a compelling interface-first vision:

| Component | Technique | Purpose |
|-----------|-----------|---------|
| **Search** | Life-Aware A* | Optimal pathfinding with survival optimization |
| **Perception** | Bayesian Sensor Fusion | Probabilistic state estimation from noisy sensors |
| **Information** | Entropy-Based Scanning | Intelligent information gathering |
| **Planning** | Monte Carlo Tree Search | Simulation-based action evaluation |
| **Learning** | Tabular Q-Learning | Policy improvement through experience |
| **Memory** | Cross-Episode Priors | Transfer learning across environments |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORACLE UNIFIED ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  Sensors    │───▶│   Belief    │───▶│  Decision   │        │
│   │ (Thermal +  │    │   Engine    │    │   Engine    │        │
│   │  Seismic)   │    │  (Bayes)    │    │             │        │
│   └─────────────┘    └─────────────┘    └──────┬──────┘        │
│                                                 │               │
│                    ┌────────────────────────────┼──────────┐    │
│                    ▼                            ▼          ▼    │
│            ┌──────────────┐           ┌──────────────┐  ┌──────┐│
│            │  A* Planner  │           │ MCTS Planner │  │  Q   ││
│            │ (Determin.)  │           │ (Simulation) │  │Table ││
│            └──────────────┘           └──────────────┘  └──────┘│
│                    │                            │          │    │
│                    └────────────┬───────────────┘          │    │
│                                 ▼                          │    │
│                         ┌──────────────┐                   │    │
│                         │  Action      │◀──────────────────┘    │
│                         │  Selection   │  (Epsilon-Greedy)      │
│                         └──────────────┘                        │
│                                 │                               │
│                                 ▼                               │
│                         ┌──────────────┐                        │
│                         │   GridWorld  │                        │
│                         │   (Physics)  │                        │
│                         └──────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Platform Strategy

Oracle is architected for a hybrid public experience:

- **Primary Showcase:** Vercel + Next.js + Three.js for a cinematic, interactive simulation.
- **Research Playground:** Hugging Face Spaces for benchmark reproducibility, configurable experiments, and academic showcase.
- **Recruiter Magnet:** Present Oracle as an **Autonomous Survival Intelligence System** with a polished command-center interface.

The ideal frontend pairs the existing engine with live features such as:

- animated grid navigation and fog-of-war
- Bayesian belief and uncertainty heatmaps
- MCTS rollout and search tree animation
- RL reward evolution and policy heatmaps
- benchmark command dashboards and challenge modes

> See `docs/platform_strategy.md` for the full hybrid deployment and showcase plan.

---

## Experience Roadmap

This repository should be presented as a cinematic AI experience, not a static algorithm demo. Key experience pillars include:

- **Live Grid World:** animated movement, hazard effects, zoom/pan controls, replay mode.
- **AI Brain Visualization:** belief updates, entropy maps, sensor confidence, decision heatmaps.
- **MCTS Theater:** branch expansion, UCB selection, rollout futures, explore/exploit visuals.
- **RL Training Cinema:** reward curves, Q-table heatmaps, emergent policy stories.
- **Benchmark Command Center:** success rates, reward histograms, efficiency metrics, animated comparisons.
- **Cinematic Interface:** glassmorphism, neon gradients, pulse scan effects, tactical overlays.

---

## Agent Types

### 1. Deterministic Agent (Perfect Information)

**State Space:** S = (row, col, lives)  
**Action Space:** A = {walk_n, walk_s, walk_e, walk_w, jump_n, jump_s, jump_e, jump_w}  
**Objective:** Minimize survival score

```
Survival Score = (Turns + Time Units) / Lives Remaining
```

The A* planner uses an **admissible heuristic** combining Manhattan distance, life penalties, and jump-optimized time estimates.

### 2. Bayesian Agent (Partial Observability)

**Belief State:** b(s) = P(cell_type | sensor_history)  
**Sensors:**
- Thermal: P(T+|Volcano) = 0.85, P(T+|Land) = 0.10
- Seismic: P(S+|Water) = 0.85, P(S+|Land) = 0.05

**Information-Theoretic Scanning:**
```
EIG(cell) = H(before) - E[H(after scan)]
```

The agent scans cells with highest **Expected Information Gain** before committing to risky moves.

### 3. RL Agent (Learning)

**State Encoding:** (r, c, lives, risk_n, risk_s, risk_e, risk_w)  
**Q-Learning Update:**
```
Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') - Q(s,a)]
```

**Exploration:** Epsilon-greedy with exponential decay and Boltzmann softmax.

### 4. Bayesian+MCTS Agent (Simulation Planning)

Uses **Monte Carlo Tree Search** with **UCB1** selection:
```
UCB1 = Q̄(child) + c √(ln(parent_visits) / child_visits)
```

150 rollouts per decision with smart goal-biased rollout policy.

---

## Mathematical Foundations

### Bayesian Update

Given sensor reading z, update belief for cell type c:

```
P(c | z) = P(z | c) · P(c) / Σ_c' P(z | c') · P(c')
```

For thermal sensor T and seismic sensor S (conditionally independent):

```
P(c | T, S) ∝ P(T | c) · P(S | c) · P(c)
```

### Expected Utility

```
U(action) = Σ_s P(s) · [R(s) + γ · V*(s')]
```

Where utility components include:
- Goal reaching: +100
- Life preservation: +50 per life
- Time penalty: -1 per time unit
- Hazard penalty: -25 per hit
- Scan cost: -2 per scan
- Information gain: +5 per bit

### Q-Learning Convergence

Under the conditions:
- Σ α_t = ∞ (infinite exploration)
- Σ α_t² < ∞ (diminishing step sizes)
- All state-action pairs visited infinitely often

The Q-function converges to Q* with probability 1 (Watkins & Dayan, 1992).

---

## Quick Start

### Prerequisites
```bash
conda env create -f config.yml
conda activate oracle-agent
```

### Run Modes

```bash
cd src

# Demo all agents
python main.py --mode all --seed 42

# Train RL agent
python main.py --mode train_rl --rl_episodes 3000

# Benchmark all agents
python main.py --mode benchmark --n_episodes 500 --rl_episodes 1000

# Demo with MCTS
python main.py --mode demo_bayesian --mcts
```

---

## Deployment

### Hugging Face Space
- Use a single HF Space with the **Gradio SDK**.
- Select the **Blank** template.
- The repo root should contain `app.py`, `requirements.txt`, and `runtime.txt`.
- Push your GitHub repo, then import it into Hugging Face Spaces.
- HF will install dependencies from `requirements.txt` and run `python app.py`.
- Recommended space name: `oracleagent` or `oracle-agent`.
- Owner: `Sammy1808`.

This repo also includes a `Dockerfile` for a custom **Docker** Space if you want full container control.

### Vercel
- Import the repo into Vercel.
- Set the project root to `frontend/`.
- Vercel will detect Next.js and build the site using `npm run build`.

### License
- This project is licensed under the **MIT License**.
- The license file is included in `LICENSE`.

---

## Experiments

### Experiment 1: Deterministic vs Bayesian Success Rate

Hypothesis: Perfect information guarantees success; partial observability reduces success rate due to sensor noise.

```
Expected: Deterministic > Bayesian+MCTS > Bayesian > RL (untrained)
```

### Experiment 2: Information Gain vs Random Scanning

Hypothesis: Entropy-based scanning outperforms random scanning in partially observable settings.

Metric: Average steps to goal with fixed scan budget.

### Experiment 3: RL Convergence

Training over 3000 episodes with ε-decay from 1.0 → 0.05.

Expected: Success rate increases from ~20% → ~80% over training.

### Experiment 4: Cross-Episode Memory

Hypothesis: Agents with memory of hazard distributions learn faster in new environments.

Metric: First-episode success rate with/without memory initialization.

---

## Benchmarks

Example benchmark results (500 episodes, 5 seeds):

| Agent | Success Rate | Avg Reward | Avg Steps | Avg Lives | Avg Scans |
|-------|-------------|------------|-----------|-----------|-----------|
| Deterministic | 95.2% | 142.3 | 14.2 | 2.8 | 0 |
| Bayesian | 72.4% | 89.1 | 22.6 | 1.9 | 8.3 |
| Bayesian+MCTS | 78.1% | 98.7 | 20.1 | 2.1 | 7.1 |
| RL (trained) | 81.5% | 105.2 | 18.4 | 2.3 | 4.2 |

---

## Visualization

The current implementation produces publication-quality figures for training and benchmarking. The long-term goal is to extend this into a cinematic visualization layer with:

- live grid-world rendering and hazard animation
- Bayesian belief heatmaps and entropy overlays
- MCTS tree expansion and rollout futures
- RL reward cinema and emergent policy visuals
- benchmark dashboards with animated comparison charts

The system currently generates figures such as:

| Figure | Description |
|--------|-------------|
| `rl_reward_curve.png` | Training reward with moving average |
| `rl_success_rate.png` | Success rate convergence |
| `belief_evolution.png` | Entropy reduction over episode |
| `benchmark_comparison.png` | Agent performance bar charts |

---

## Project Structure

```
src/
├── config.py                 # Centralized hyperparameters
├── main.py                   # Unified CLI entry point
│
├── env/
│   └── grid_world.py         # Environment dynamics & physics
│
├── belief/
│   └── bayesian_update.py    # Probabilistic state estimation
│
├── planning/
│   ├── astar.py              # Life-aware A* search
│   └── monte_carlo.py        # MCTS with UCB1
│
├── agents/
│   ├── deterministic_agent.py
│   ├── bayesian_agent.py
│   └── rl_agent.py
│
├── learning/
│   └── q_learning.py         # Tabular Q-learning engine
│
├── utils/
│   └── metrics.py            # Benchmarking & logging
│
├── experiments/
│   └── benchmark.py          # Full evaluation suite
│
└── visualize/
    └── plots.py              # Publication-quality plots
```

---

## References

1. Russell, S. & Norvig, P. *Artificial Intelligence: A Modern Approach* (4th Ed.). Pearson, 2020.
2. Watkins, C.J.C.H. & Dayan, P. "Q-Learning." *Machine Learning*, 8(3), 1992.
3. Kocsis, L. & Szepesvári, C. "Bandit Based Monte-Carlo Planning." *ECML*, 2006.
4. Thrun, S. "Probabilistic Robotics." *Communications of the ACM*, 2002.
5. Howard, R.A. "Information Value Theory." *IEEE Transactions on Systems Science*, 1966.

---

<div align="center">

### *"The grid is dark and full of terrors. But Oracle has computed the way."*

🌟 Star this repo if Oracle survives your first run.  
🍴 Fork it to build your own planetary probe.  
🐛 Open an issue if Oracle falls into the abyss.

</div>
