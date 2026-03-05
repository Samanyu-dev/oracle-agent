# ── Grid Settings
GRID_ROWS = 9
GRID_COLS = 9

# ── Cell Type Constants
CELL_LAND    = 'L'
CELL_VOLCANO = 'V'
CELL_WATER   = 'W'
CELL_BRICK   = 'B'
CELL_START   = 'S'
CELL_GOAL    = 'G'

# ── Agent Settings
MAX_LIVES        = 4
WALK_TIME_COST   = 2   # Time Units per walk action
JUMP_TIME_COST   = 3   # Time Units per jump action
TURN_COST        = 1   # Every action costs +1 Turn Unit

# ── Grid Generation Ratios 
HAZARD_RATIO     = 0.50   # 50% of non-path cells are hazardous (V or W)
LAND_RATIO       = 0.40   # 40% of non-path cells are Land
BRICK_RATIO      = 0.10   # 10% of non-path cells are Brick Wall
PATH_VOLCANOES   = 2      # Exactly 2 Volcanoes on the ground-truth path
PATH_WATERS      = 2      # Exactly 2 Waters on the ground-truth path


# ── Visualization Color Codes 
COLOR_LAND          = '#5DBB63'   # Green
COLOR_VOLCANO       = '#E63946'   # Red
COLOR_WATER         = '#457B9D'   # Blue
COLOR_BRICK         = '#6B6B6B'   # Dark Gray
COLOR_START         = '#FFD166'   # Gold
COLOR_GOAL          = '#06D6A0'   # Teal
COLOR_UNKNOWN       = '#CCCCCC'   # Light Gray (belief map unknown)
COLOR_WALK_ARROW    = 'black'
COLOR_JUMP_ARROW    = 'purple'
COLOR_DAMAGE_ARROW  = 'red'
COLOR_PATH_BORDER   = 'yellow'
COLOR_SCAN_BORDER   = '#FFD700'   # Yellow border for scanned cells
COLOR_AGENT         = '#FF6B35'   # Agent circle color

# ── Output Paths 
OUTPUT_DIR           = 'outputs'
FRAMES_DIR           = 'outputs/frames'
FRAMES_DIR_EX2       = 'outputs/frames_ex2'
GROUND_TRUTH_PNG     = 'outputs/ground_truth.png'
INITIAL_GRID_PNG     = 'outputs/initial_grid.png'
SIMULATION_GIF       = 'outputs/simulation_ex1.gif'
SIMULATION_GIF_EX2   = 'outputs/simulation_ex2.gif'