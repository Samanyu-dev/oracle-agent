"""
Global configuration for the Oracle Agent ecosystem.
All hyperparameters are centralized here for easy tuning.
"""

# ============================================================
# GRID WORLD
# ============================================================
GRID_ROWS = 9
GRID_COLS = 9

CELL_LAND    = 'L'
CELL_VOLCANO = 'V'
CELL_WATER   = 'W'
CELL_BRICK   = 'B'
CELL_START   = 'S'
CELL_GOAL    = 'G'

MAX_LIVES        = 4
WALK_TIME_COST   = 2
JUMP_TIME_COST   = 3
TURN_COST        = 1

HAZARD_RATIO     = 0.50
LAND_RATIO       = 0.40
BRICK_RATIO      = 0.10
PATH_VOLCANOES   = 2
PATH_WATERS      = 2

# ============================================================
# BAYESIAN SENSORS
# ============================================================
P_LAVA             = 0.24
P_WATER            = 0.24
P_LAND             = 0.16
P_WALL             = 0.36

P_THERMAL_GIVEN    = {
    'lava':  0.85,
    'water': 0.01,
    'land':  0.10,
    'wall':  0.05,
}

P_SEISMIC_GIVEN    = {
    'lava':  0.60,
    'water': 0.85,
    'land':  0.05,
    'wall':  0.01,
}

MAX_SCANS_PER_CELL = 4
RISK_THRESHOLD     = 0.5

# ============================================================
# DECISION THEORY
# ============================================================
UTILITY_GOAL        = 100.0
UTILITY_LIFE        = 50.0
UTILITY_TIME_PENALTY = -1.0
UTILITY_HAZARD      = -25.0
UTILITY_SCAN_COST   = -2.0
UTILITY_INFO_GAIN   = 5.0

# ============================================================
# RL / Q-LEARNING
# ============================================================
RL_EPISODES         = 3000
RL_LEARNING_RATE    = 0.15
RL_DISCOUNT_FACTOR  = 0.95
RL_EPSILON_START    = 1.0
RL_EPSILON_END      = 0.05
RL_EPSILON_DECAY    = 0.995

# Tile encoding for RL state
TILE_ENCODING = {
    CELL_LAND:    0,
    CELL_VOLCANO: 1,
    CELL_WATER:   2,
    CELL_BRICK:   3,
    CELL_START:   0,
    CELL_GOAL:    4,
}

# ============================================================
# MONTE CARLO PLANNING
# ============================================================
MC_ROLLOUTS         = 150
MC_HORIZON          = 25
MC_UCB_CONSTANT     = 1.414

# ============================================================
# CROSS-EPISODE MEMORY
# ============================================================
MEMORY_DECAY        = 0.95
MEMORY_UPDATE_RATE  = 0.1

# ============================================================
# HYPERPARAMETER SEARCH
# ============================================================
HP_GRID_SEARCH = {
    'heuristic_weight': [0.05, 0.1, 0.2, 0.5],
    'risk_threshold':   [0.3, 0.5, 0.7, 0.9],
    'scan_budget':      [3, 5, 7, 10],
}

# ============================================================
# BENCHMARKING
# ============================================================
BENCHMARK_EPISODES  = 500
BENCHMARK_SEEDS     = [42, 1337, 2024, 999, 31415]

# ============================================================
# VISUALIZATION
# ============================================================
COLOR_LAND          = '#5DBB63'
COLOR_VOLCANO       = '#E63946'
COLOR_WATER         = '#457B9D'
COLOR_BRICK         = '#6B6B6B'
COLOR_START         = '#FFD166'
COLOR_GOAL          = '#06D6A0'
COLOR_UNKNOWN       = '#CCCCCC'
COLOR_WALK_ARROW    = 'black'
COLOR_JUMP_ARROW    = 'purple'
COLOR_DAMAGE_ARROW  = 'red'
COLOR_PATH_BORDER   = 'yellow'
COLOR_SCAN_BORDER   = '#FFD700'
COLOR_AGENT         = '#FF6B35'

OUTPUT_DIR           = 'outputs'
FRAMES_DIR           = 'outputs/frames'
FRAMES_DIR_EX2       = 'outputs/frames_ex2'
GROUND_TRUTH_PNG     = 'outputs/ground_truth.png'
INITIAL_GRID_PNG     = 'outputs/initial_grid.png'
SIMULATION_GIF       = 'outputs/simulation_ex1.gif'
SIMULATION_GIF_EX2   = 'outputs/simulation_ex2.gif'

FIGURES_DIR          = 'figures'
REWARD_CURVE_PNG     = 'figures/reward_curve.png'
SUCCESS_RATE_PNG     = 'figures/success_rate.png'
BELIEF_EVOLUTION_PNG = 'figures/belief_evolution.png'
BENCHMARK_TABLE_PNG  = 'figures/benchmark_table.png'
