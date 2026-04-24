# Oracle Agent — Complete Command Reference

## 1. Environment Setup

### Using Conda (Recommended)
```bash
# Create the conda environment from config.yml
conda env create -f config.yml

# Activate the environment
conda activate oracle-agent

# Verify Python version
python --version
```

### Using pip (Alternative)
```bash
# Install dependencies directly
pip install -r requirements.txt

# Or manually:
pip install numpy matplotlib pillow imageio
```

---

## 2. Running the Oracle Agent

All commands should be run from the `src/` directory:

```bash
cd src
```

### 2.1 Demo Modes

```bash
# Run ALL demonstrations (deterministic + bayesian + RL training + RL demo + benchmark)
python main.py --mode all --seed 42

# Demo only the Deterministic Agent (perfect sensors)
python main.py --mode demo_deterministic --seed 42

# Demo only the Bayesian Agent (noisy sensors)
python main.py --mode demo_bayesian --seed 42

# Demo Bayesian Agent WITH Monte Carlo Tree Search
python main.py --mode demo_bayesian --mcts --seed 42

# Demo only the trained RL Agent
python main.py --mode demo_rl --seed 42 --model_path models/q_table.json
```

### 2.2 Training Mode

```bash
# Train the RL agent with default episodes (3000)
python main.py --mode train_rl

# Train with custom number of episodes
python main.py --mode train_rl --rl_episodes 5000

# Train and save to custom model path
python main.py --mode train_rl --rl_episodes 2000 --model_path models/my_model.json
```

### 2.3 Benchmarking Mode

```bash
# Run full benchmark suite (default: 500 episodes)
python main.py --mode benchmark

# Benchmark with fewer episodes (faster)
python main.py --mode benchmark --n_episodes 100

# Benchmark with more RL training
python main.py --mode benchmark --n_episodes 200 --rl_episodes 1000

# Benchmark WITHOUT training RL first
python main.py --mode benchmark --n_episodes 100 --rl_episodes 0
```

### 2.4 Complete Pipeline

```bash
# Run everything: demos, training, benchmarks
python main.py --mode all --seed 42 --rl_episodes 3000 --n_episodes 500
```

---

## 3. Git Commands

```bash
# Check status
git status

# Stage all changes
git add -A

# Commit with message
git commit -m "Your commit message here"

# Push to remote
git push origin main

# View commit history
git log --oneline -10

# Pull latest changes
git pull origin main
```

---

## 4. Utility Commands

```bash
# Create output directories manually
mkdir -p outputs figures models

# Clean generated files
rm -rf outputs/* figures/* models/*

# List all Python files
find src -name "*.py" | sort

# Check for syntax errors in all Python files
python -m py_compile src/main.py
```

---

## 5. Troubleshooting

### Missing Dependencies
```bash
# If matplotlib/numpy not found:
pip install numpy matplotlib pillow imageio

# If conda environment missing:
conda env create -f config.yml
conda activate oracle-agent
```

### Xcode License Error (macOS)
```bash
# Run this in Terminal manually (requires password)
sudo xcodebuild -license accept
```

### Import Errors
```bash
# Ensure you're in the src/ directory
cd src
python main.py --mode demo_deterministic
```

---

## 6. Advanced Usage

### Hyperparameter Search
```bash
# Edit src/config.py to modify:
# - RL_LEARNING_RATE
# - RL_DISCOUNT_FACTOR
# - MC_ROLLOUTS
# - HP_GRID_SEARCH parameters
```

### Custom Grid Size
```bash
# Edit src/config.py:
# GRID_ROWS = 11
# GRID_COLS = 11
```

### Load Saved Model
```bash
# After training, load and evaluate:
python main.py --mode demo_rl --model_path models/q_table.json
```

---

## Quick Reference Table

| Command | Purpose | Time |
|---------|---------|------|
| `python main.py --mode demo_deterministic` | See A* in action | < 5s |
| `python main.py --mode demo_bayesian` | See Bayesian inference | < 10s |
| `python main.py --mode train_rl --rl_episodes 500` | Quick RL training | ~30s |
| `python main.py --mode train_rl --rl_episodes 3000` | Full RL training | ~3min |
| `python main.py --mode benchmark --n_episodes 100` | Quick benchmark | ~2min |
| `python main.py --mode benchmark --n_episodes 500` | Full benchmark | ~10min |
| `python main.py --mode all` | Everything | ~15min |
