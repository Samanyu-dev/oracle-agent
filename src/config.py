
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


P_VOLCANO_PRIOR    = 0.4    
P_WATER_PRIOR      = 0.4    


P_LAVA             = 0.4 * (1 - 0.4)  
P_WATER            = (1 - 0.4) * 0.4 
P_LAND             = 0.4 * 0.4        
P_WALL             = (1 - 0.4) * (1 - 0.4)  


P_THERMAL_GIVEN    = {
    'lava': 0.85,      
    'water': 0.01,     
    'land': 0.10,     
    'wall': 0.05,      
}

P_SEISMIC_GIVEN    = {
    'lava': 0.60,     
    'water': 0.85,     
    'land': 0.05,     
    'wall': 0.01,     
}

MAX_SCANS_PER_CELL = 4     
RISK_THRESHOLD     = 0.5    



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