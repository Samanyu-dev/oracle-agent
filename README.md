<div align="center">

# 🔮 ORACLE: The Last Probe

**An autonomous exploration agent navigating the uncharted wastelands of Kepler-186f.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![AI](https://img.shields.io/badge/AI-A*_Search-FF6F00?logo=openai&logoColor=white)]()
[![Bayesian](https://img.shields.io/badge/Sensor_Fusion-Bayesian_Inference-9C27B0)]()
[![Status](https://img.shields.io/badge/Mission_Status-OPERATIONAL-brightgreen)]()

*"In a world of noise and uncertainty, only the Oracle sees the path."*

</div>

---

## 🌌 The Lore

> **Stardate 2187.** The colony ship *Aether* has dispatched its final probe — **Oracle** — to chart a safe passage across the volatile surface of Kepler-186f. The terrain is unforgiving: **magma vents** erupt without warning, **toxic aquifers** lie hidden beneath crusted dust, **impassable basalt walls** fracture the landscape, and stretches of **stable bedrock** are the only refuge.
>
> Oracle begins at the **Northern Landing Zone** (0,0). The extraction point awaits at the **Southern Ridge** (n,n). Lives are limited. Time is scarce. The mission: **survive the crossing.**

---

## 🎮 Game Modes

Oracle operates in two distinct modes of consciousness. Choose your challenge:

### 🧿 MODE I: The All-Seeing Eye *(Deterministic)*
> **Difficulty:** ⭐⭐⭐☆☆  
> **Sensor Status:** OMNI-OPTIC ONLINE

Oracle possesses perfect omniscience. Every tile is known. Every threat is mapped. It deploys **A\* Search** with a custom survival heuristic, optimizing not merely for distance, but for the sacred ratio:

```
Survival Score = (Turns + Time Units) ÷ Lives Remaining
```

Lower is better. Oracle doesn't just find *a* path — it finds the path where **you live longest.**

**Moveset:**
| Action | Cost | Mechanics |
|--------|------|-----------|
| 🚶 Walk | 2 TU + 1 Turn | Move 1 tile. Standard reconnaissance. |
| 🦘 Jump | 3 TU + 1 Turn | Leap 2 tiles, skipping the middle. No wall vaulting. |
| 💀 Misstep | 1 Life | Touch Lava or Water. Oracle bleeds. |

---

### 🔥 MODE II: The Blind Prophet *(Probabilistic)*
> **Difficulty:** ⭐⭐⭐⭐⭐  
> **Sensor Status:** DEGRADED — THERMAL/SEISMIC ARRAY ONLY

Oracle is blind. The grid is darkness. Before each risky step, it must **scan** the unknown using damaged sensors:

- 🔥 **Thermal Array** — Detects magma vents (noisy, prone to false positives)
- 🌊 **Seismic Resonator** — Detects subsurface water (erratic in basalt fields)

Every scan feeds into a **Bayesian Belief Engine**. Priors update. Uncertainty collapses. Oracle builds a living probability map of the unseen world.

**Scan Limits:** 4 scans per cell. After that? The tile is declared **unreachable** and Oracle adapts.

```
Prior Beliefs (Every Tile at Birth):
┌──────────┬──────────┬──────────┬──────────┐
│ Volcano  │  Water   │   Land   │  Brick   │
│   24%    │   24%    │   16%    │   36%    │
└──────────┴──────────┴──────────┴──────────┘
```

> *"To navigate the unseen is not madness — it is mathematics."*

---

## 🗺️ World Generation

The planet surface is procedurally generated. No two missions are alike.

```
Mission Parameters:
├── Grid Size: 9×9 (configurable 8×8 to 10×10)
├── Path Generation: Biased Random Walk (30% chaos factor)
├── Anchor Points: 2 (quadrant-locked, non-collinear)
├── Path Hazards: 2 Volcanoes + 2 Waters (non-adjacent)
├── Off-Path Fill: 50% Hazard | 40% Land | 10% Brick Wall
└── Result: INFINITE REPLAYABILITY
```

The procedural engine ensures the safe corridor between anchors is never a boring straight line. Oracle must *think*, not just walk.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Conda (recommended)

### Launch Sequence

```bash
# Step 1: Initialize the habitat
conda env create -f config.yml

# Step 2: Awaken Oracle
conda activate oracle-agent

# Step 3: Deploy
cd src
python main.py
```

**Output artifacts** auto-materialize in `outputs/`:

| Artifact | Description |
|----------|-------------|
| `ground_truth.png` | Satellite view with the true safe corridor |
| `initial_grid.png` | Pre-mission reconnaissance snapshot |
| `simulation_ex1.gif` | 🎬 Cinematic playback of Mode I |
| `simulation_ex2.gif` | 🎬 Split-screen: Belief Map vs Reality (Mode II) |
| `frames/` | Frame-by-frame stills for analysis |

---

## 🏆 Oracle's Telemetry Dashboard

Each mission generates a **debrief log**:

```
╔══════════════════════════════════════╗
║         MISSION DEBRIEF              ║
╠══════════════════════════════════════╣
║  Steps Completed : 14                ║
║  Final Lives     : 2  ❤️❤️🖤         ║
║  Total Turns     : 14                ║
║  Time Units      : 29                ║
║  Final Score     : 10.2500           ║
║  Outcome         : 🏆 VICTORY        ║
╚══════════════════════════════════════╝
```

---

## 🧠 Technical Architecture

```
┌─────────────────────────────────────────────┐
│              ORACLE CORE v1.0               │
├─────────────────────────────────────────────┤
│  🎛️  CONFIG        → Mission parameters    │
│  🗺️  GRID GEN      → Procedural world      │
│  🧠  AGENT         → A* + Bayesian brain   │
│  🎨  VISUALIZER    → Matplotlib cinema     │
│  ⚡  MAIN           → Orchestrator          │
└─────────────────────────────────────────────┘
```

### Algorithmic Arsenal
- **A\* Search** with life-aware heuristic
- **Bayesian Inference** for noisy sensor fusion
- **Multi-path exploration** with scan-budgeted retries
- **Manhattan-distance heuristics** optimized for jump mechanics

---

## 🎯 Can You Beat the Oracle?

Try your hand at out-piloting the agent:

> **Challenge I:** Run Mode I. Can *you* trace a path with a lower Survival Score than Oracle's A\*?
>
> **Challenge II:** Run Mode II. Given only the belief map at Step 5, guess the ground truth. How close are your instincts to Bayes' theorem?
>
> **Challenge III:** Tweak `NOISE` in `config.py`. At what chaos factor does Oracle fail to find *any* valid path?

Post your scores. Tag your runs. `#BeatTheOracle`

---

## 🛠️ System Requirements

```yaml
Engine: Python 3.10
Core Modules:
  - numpy        # Matrix operations & probability
  - matplotlib   # Tactical display rendering
  - imageio      # Cinematic GIF export
  - pillow       # Image frame processing
```

---

## ⚠️ Field Notes

- 🔄 **Every launch is unique.** The random walk ensures no memorization — only adaptation.
- 🔗 **Mode II shares the exact same world** as Mode I. The only variable is Oracle's *mind*.
- ⏳ **Mode II may run slower.** Real-time Bayesian updates during pathfinding are computationally expensive. This is expected behavior.
- 📁 **All artifacts auto-save.** No manual intervention required post-launch.

---

<div align="center">

### *"The grid is dark and full of terrors. But Oracle has computed the way."*

🌟 Star this repo if Oracle survives your first run.  
🍴 Fork it to build your own planetary probe.  
🐛 Open an issue if Oracle falls into the abyss.

</div>
