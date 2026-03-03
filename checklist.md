---

## ⚙️ Rohith — `config.py` + Testing

### 📄 config.py
- [ ] `GRID_ROWS = 9`, `GRID_COLS = 9` (choose any value between 8–10)
- [ ] `WALK_TIME_COST = 2`, `JUMP_TIME_COST = 3`, `TURN_COST = 1`
- [ ] `MAX_LIVES = 4`
- [ ] Cell type constants: `CELL_LAND`, `CELL_VOLCANO`, `CELL_WATER`, `CELL_BRICK`, `CELL_START`, `CELL_GOAL`
- [ ] `HAZARD_RATIO = 0.50`, `LAND_RATIO = 0.40`, `BRICK_RATIO = 0.10`
- [ ] `PATH_VOLCANOES = 2`, `PATH_WATERS = 2`
- [ ] `P_VOLCANO_PRIOR = 0.4`, `P_WATER_PRIOR = 0.4`
- [ ] Derived priors: `P_LAVA=0.24`, `P_WATER=0.24`, `P_LAND=0.16`, `P_WALL=0.36`
- [ ] `P_THERMAL_GIVEN` dict: `V=0.85`, `W=0.01`, `L=0.10`, `B=0.05`
- [ ] `P_SEISMIC_GIVEN` dict: `V=0.60`, `W=0.85`, `L=0.05`, `B=0.01`
- [ ] `MAX_SCANS_PER_CELL = 4`, `RISK_THRESHOLD = 0.5`
- [ ] Color codes: `COLOR_LAND`, `COLOR_VOLCANO`, `COLOR_WATER`, `COLOR_BRICK`, `COLOR_START`, `COLOR_GOAL`, `COLOR_UNKNOWN`
- [ ] Arrow colors: `COLOR_WALK_ARROW`, `COLOR_JUMP_ARROW`, `COLOR_DAMAGE_ARROW`
- [ ] Output paths: `OUTPUT_DIR`, `GROUND_TRUTH_PNG`, `INITIAL_GRID_PNG`, `SIMULATION_GIF`, `FRAMES_DIR`
- [ ] Share `config.py` with all members by Day 2

### 🧪 Testing — config.py
- [ ] `from config import *` runs without any errors
- [ ] Derived priors sum to 1.0 → `0.24 + 0.24 + 0.16 + 0.36 = 1.0`
- [ ] `P_THERMAL_GIVEN` and `P_SEISMIC_GIVEN` values match assignment exactly
- [ ] All color codes are valid hex strings
- [ ] Output paths are consistent with the folder structure

---

## 🗺️ Samanyu — `grid_gen.py` + `agent.py` (Ex1) + `visualizer.py` + `main.py` (Ex1) + Testing

### 📄 grid_gen.py
- [ ] `generate_unique_path(rows, cols)`: random walk from `(0,0)` → anchor1 → anchor2 → `(M-1,N-1)`
- [ ] Anchor1 picked in top-left quadrant (row 1 to `rows//2-1`, col 1 to `cols//2-1`)
- [ ] Anchor2 picked in bottom-right quadrant (row `rows//2` to `rows-2`, col `cols//2` to `cols-2`)
- [ ] Anchor1 and anchor2 have **different rows AND different columns**
- [ ] Anchor1 and anchor2 are **not adjacent** (`abs diff > 1` in both row and col)
- [ ] Random walk uses ~30% noise deviation to ensure unique path every run
- [ ] Combine segments: `start→anchor1`, `anchor1→anchor2`, `anchor2→goal`
- [ ] Deduplicate path cells while preserving order
- [ ] `place_hazards_on_path()`: exactly **2 Volcanoes + 2 Waters** placed on path cells
- [ ] Same-type hazards are **not adjacent** to each other on the path
- [ ] Hazards never placed on start, goal, or anchor cells
- [ ] All remaining path cells set to `Land (L)`
- [ ] Fill non-path cells: 50% hazard (W/V), 40% Land, 10% Brick
- [ ] `generate_grid()` returns: `grid` (2D list), `path` (list), `anchor1`, `anchor2`
- [ ] `grid[0][0] = START` and `grid[M-1][N-1] = GOAL` always enforced

### 📄 agent.py — Exercise 1
- [ ] `AgentState` class: fields `position`, `lives`, `turns`, `time_units`, `path_history`, `alive`
- [ ] `score()` method: returns `(turns + time_units) / lives`
- [ ] `OracleAgentEx1` class takes `grid` as input
- [ ] `thermal_sensor(r,c)`: returns `True` if `grid[r][c] == CELL_VOLCANO` (perfect sensor)
- [ ] `seismic_sensor(r,c)`: returns `True` if `grid[r][c] == CELL_WATER` (perfect sensor)
- [ ] `is_hazard(r,c)`: returns `True` if cell is `V` or `W`
- [ ] `is_walkable(r,c)`: returns `True` if cell is not Brick and is within bounds
- [ ] `get_neighbors(r,c)`: returns all valid **walk** moves (1 cell, cost `2TU + 1Turn`)
- [ ] `get_neighbors(r,c)`: returns all valid **jump** moves (2 cells, skip middle, cost `3TU + 1Turn`)
- [ ] Brick Wall constraint: if middle cell during jump is Brick → invalid, costs `+1 Turn`, bounce back
- [ ] `heuristic(r,c,lives)`: Manhattan distance to goal + penalty for low lives
- [ ] `a_star_search()`: state = `(position, lives)`, priority = `(turns + time) / lives`
- [ ] Life loss inside A*: step on V or W → `lives -= 1`, continue from that cell
- [ ] Terminal failure check: `lives == 0` → stop search, return failure
- [ ] `run()` method: execute found path step by step, build and return simulation log
- [ ] Simulation log format per step: `{step, from, to, action, took_damage, lives, turns, time, score}`

### 📄 visualizer.py — Exercise 1
- [ ] `cell_color(cell_type)`: maps `L/V/W/B/S/G` to hex color from `config.py`
- [ ] `draw_grid_base(ax, grid, title)`: draws colored rectangles + cell labels on matplotlib axes
- [ ] Walk arrow: **black straight arrow** (`connectionstyle=arc3,rad=0`)
- [ ] Jump arrow: **purple curved arrow** (`connectionstyle=arc3,rad=0.3`)
- [ ] Damage turn arrow: **dotted/dashed red arrow** (`linestyle='--'`, `color=red`)
- [ ] `draw_arrow()`: selects correct style based on `action` and `took_damage`
- [ ] Red **✗** marker drawn at every cell where agent took damage
- [ ] `save_ground_truth(grid, path, anchor1, anchor2)`: yellow border on path cells, A1/A2 labels, saved as PNG
- [ ] `save_initial_grid(grid)`: draws grid as-is, saved as PNG
- [ ] `render_simulation_ex1(grid, sim_log)`: one frame per step, title shows lives/score/turns/time
- [ ] Agent current position shown as filled circle on each frame
- [ ] Each frame saved as individual PNG to `FRAMES_DIR`
- [ ] All frames compiled into `simulation.gif` using `imageio.mimsave(fps=2)`

### 📄 main.py — Exercise 1 portion
- [ ] Import `config`, `grid_gen`, `OracleAgentEx1`, visualizer functions
- [ ] `os.makedirs(OUTPUT_DIR)` and `os.makedirs(FRAMES_DIR)` at startup
- [ ] Call `generate_grid()` → get `grid`, `path`, `anchor1`, `anchor2`
- [ ] Print grid to terminal row by row with row numbers
- [ ] Print path cell IDs: start, anchor1, anchor2, goal, and all steps
- [ ] Call `save_ground_truth(grid, path, anchor1, anchor2)`
- [ ] Call `save_initial_grid(grid)`
- [ ] Run `OracleAgentEx1(grid).run()` → get `sim_log`
- [ ] Call `render_simulation_ex1(grid, sim_log)`
- [ ] Print final Ex1 results: lives remaining, score, total turns, total time

### 🧪 Testing — Member 2
- [ ] Run `grid_gen` 5 times → confirm 5 visually different paths
- [ ] Count V and W on path → must be **exactly 2 each**
- [ ] Verify no two same-type hazards are adjacent on the path
- [ ] Confirm start and goal cells are never hazardous
- [ ] Agent tested on 3 different grids → valid path found each time
- [ ] Walk costs exactly `2 Time + 1 Turn` confirmed in log
- [ ] Jump costs exactly `3 Time + 1 Turn` confirmed in log
- [ ] Brick Wall bounce costs exactly `1 Turn` confirmed in log
- [ ] Lives never go below 0 in any test
- [ ] Score formula `(turns+time)/lives` is correct in every log entry
- [ ] All PNGs saved to correct output paths
- [ ] GIF plays correctly with correct arrow colors and styles

---

## 🧠 Dhanush — `agent.py` (Ex2) + `visualizer.py` (Ex2) + `main.py` (Ex2) + Testing

### 📄 agent.py — Exercise 2
- [ ] `BeliefCell` class: stores `P(V)`, `P(W)`, `P(L)`, `P(B)` for one cell
- [ ] Initialize `BeliefCell` priors: `P(V)=0.24`, `P(W)=0.24`, `P(L)=0.16`, `P(B)=0.36`
- [ ] `risk()` method: returns `P(V) + P(W)`
- [ ] `bayesian_update(thermal, seismic)`: multiply `P(T|type) × P(S|type) × prior` then normalize
- [ ] `scan_count` tracked per cell, incremented on each scan
- [ ] `blocked` flag: set `True` when `scan_count >= MAX_SCANS_PER_CELL (4)`
- [ ] `last_thermal` and `last_seismic` readings stored in `BeliefCell` for visualization
- [ ] `NoisySensor` class: generates noisy `True/False` using CPT from `config.py`
- [ ] `thermal(true_type)`: `random.random() < P_THERMAL_GIVEN[true_type]`
- [ ] `seismic(true_type)`: `random.random() < P_SEISMIC_GIVEN[true_type]`
- [ ] `OracleAgentEx2` class: initializes full 2D belief map (`rows × cols` of `BeliefCell`)
- [ ] `scan_cell(r,c)`: reads noisy sensors → `bayesian_update` → costs `+1 Turn`, agent does NOT move
- [ ] `scan_cell` returns `None` and sets blocked if `scan_count >= 4`
- [ ] `should_scan(r,c)`: returns `True` if `risk > RISK_THRESHOLD` and `scan_count < 4`
- [ ] `get_safe_neighbors(r,c)`: scans risky neighbors before adding to options, sorted by risk ascending
- [ ] `probabilistic_a_star()`: A* with risk-weighted cost, state = `(position, lives)`
- [ ] Risk penalty in A*: adds `risk × 3` to movement cost for uncertain cells
- [ ] `run()` method Ex2: executes path, discovers true types on arrival, updates beliefs to 100%
- [ ] Simulation log: same as Ex1 log **plus** `'beliefs'` field = full belief map snapshot per step
- [ ] Scan log format per scan: `{cell, thermal, seismic, beliefs, scan_num}`

### 📄 visualizer.py — Exercise 2 additions
- [ ] `belief_color(belief_p)`: Red if `P(V)>0.4`, Blue if `P(W)>0.4`, Green if `P(L)>0.5`, else Gray
- [ ] Left panel: color each cell by `belief_color()`, show `risk%` as text inside cell
- [ ] Yellow border `Rectangle` patch on all cells that have been scanned
- [ ] `T:True/False S:True/False` sensor label text on scanned cells (from scan log)
- [ ] Red **✗** marker on left panel at cells where agent took damage
- [ ] Right panel: `draw_grid_base()` with true colors and true cell labels
- [ ] Red **✗** marker on right panel at hazard encounter cells
- [ ] Dual panel: `plt.subplots(1,2)` — both panels rendered at the **same step simultaneously**
- [ ] Same path arrows shown on both panels
- [ ] `render_simulation_ex2(grid, sim_log, scan_log)`: loops steps, renders dual panel per step
- [ ] Each dual-panel frame saved as PNG to `FRAMES_DIR`
- [ ] All Ex2 frames compiled into `ex2_simulation.gif` using `imageio`

### 📄 main.py — Exercise 2 portion
- [ ] Import `OracleAgentEx2` and `render_simulation_ex2`
- [ ] Run `OracleAgentEx2(grid).run()` → get `sim_log`, `scan_log`
- [ ] Call `render_simulation_ex2(grid, sim_log, agent.scan_log)`
- [ ] Print final Ex2 results: lives, score, turns, time, total scans used
- [ ] Ex2 uses the **same grid** generated in the Ex1 portion of `main.py`

### 🧪 Testing — Member 3
- [ ] After every Bayesian update, confirm `P(V)+P(W)+P(L)+P(B) = 1.0`
- [ ] Manually compute one Bayesian update by hand and verify code matches
- [ ] Test: `Thermal=True, Seismic=False` → `P(V)` should be highest (~71%)
- [ ] Test: `Thermal=False, Seismic=False` → `P(B)` should be highest (Wall hint from assignment)
- [ ] Test: `Thermal=False, Seismic=True` → `P(W)` should be highest
- [ ] Confirm scanning costs `+1 Turn` and agent position does NOT change
- [ ] Confirm max 4 scans per cell enforced, `blocked=True` set after 4th scan
- [ ] `risk()` returns `P(V) + P(W)` correctly for each cell
- [ ] `should_scan()` triggers correctly when `risk > 0.5`
- [ ] Agent completes run without crashing on 3 different grids
- [ ] Simulation log contains `'beliefs'` field at every step
- [ ] Scan log contains correct `cell`, `thermal`, `seismic`, `scan_num` fields
- [ ] Dual-panel GIF renders both panels correctly and is fully synchronized

---

## 🚀 Nandan — GitHub + Bash + `config.yml` + Submission

### 🐙 GitHub Repository Setup
- [ ] Create **PRIVATE** GitHub repository named `CSF407_2026_IDX` (replace X with group ID)
- [ ] Verify repo visibility is set to **PRIVATE** (not public)
- [ ] Add Member 1 as collaborator → Settings → Collaborators → Add people
- [ ] Add Member 2 as collaborator
- [ ] Add Member 3 as collaborator
- [ ] Confirm all 4 members can clone and push without errors

### 💻 Bash — Folder Structure
- [ ] Clone repo: `git clone https://github.com/USERNAME/CSF407_2026_IDX.git`
- [ ] Create source folder: `mkdir src`
- [ ] Create all empty source files: `touch src/config.py src/grid_gen.py src/agent.py src/visualizer.py src/main.py`
- [ ] Create outputs folder: `mkdir outputs`
- [ ] Create frames folder: `mkdir outputs/frames`
- [ ] Create `.gitignore`: add `__pycache__/`, `*.pyc`, `outputs/frames/`
- [ ] Push initial structure: `git add . && git commit -m "Initial project structure" && git push`
- [ ] Confirm all members can pull the structure successfully

### 📄 config.yml — Conda Environment
- [ ] Environment name matches repo name: `name: CSF407_2026_IDX`
- [ ] Python version set: `python=3.10`
- [ ] Add `numpy` to dependencies
- [ ] Add `matplotlib` to dependencies
- [ ] Add `imageio` to dependencies
- [ ] Add `pillow` to dependencies
- [ ] Add pip section with `imageio[ffmpeg]` for MP4/GIF support
- [ ] Test locally: `conda env create -f config.yml` runs without errors
- [ ] Test activation: `conda activate CSF407_2026_IDX` works
- [ ] Confirm `python main.py` runs inside the conda environment
- [ ] Confirm all teammates can create the env from `config.yml` on their machines

### 🔄 Git Workflow Throughout Project
- [ ] All members pull before every coding session: `git pull origin main`
- [ ] Coordinate with Members 2 and 3 before pushing `agent.py` (both edit this file)
- [ ] Resolve any merge conflicts in `agent.py` carefully
- [ ] Commit with clear messages (e.g. `Add A* search to OracleAgentEx1`)
- [ ] Only push final PNGs and GIFs to `outputs/` — not all frame images

### 📦 Final Submission
- [ ] All files present in `src/`: `config.py`, `grid_gen.py`, `agent.py`, `visualizer.py`, `main.py`
- [ ] `config.yml` is at **root level** (not inside `src/`)
- [ ] `README.md` is complete with setup instructions and unique algorithm explanation
- [ ] Run full pipeline one final time: `python main.py` — zero errors
- [ ] `ground_truth.png` exists in `outputs/`
- [ ] `initial_grid.png` exists in `outputs/`
- [ ] `simulation.gif` exists in `outputs/`
- [ ] `ex2_simulation.gif` exists in `outputs/`
- [ ] Both GIFs play correctly with correct colors and arrows
- [ ] Repo name matches required format exactly: `CSF407_2026_IDX`
- [ ] Create zip: `zip -r CSF407_2026_ID_Assignment-I.zip CSF407_2026_IDX/`
- [ ] Zip file name format is correct: `CSF407_2026_ID_Assignment-I.zip`
- [ ] Email to: `skaziz.ali@hyderabad.bits-pilani.ac.in`
- [ ] Email subject **exactly**: `[CSF407_2026_ID_Assignment-I]`
- [ ] Only **ONE** zip file attached to the email
- [ ] Only **ONE** member submits — do not send multiple times
- [ ] Submitted before **05/03/2026 at 05:00 PM** ⚠️

---

## 📊 Progress Tracker

| Member | File(s) | Status |
|--------|---------|--------|
| Rohith | `config.py` + Testing | 🔴 Not Started |
| Samanyu | `grid_gen.py` + `agent.py` Ex1 + `visualizer.py` + `main.py` Ex1 + Testing | 🔴 Not Started |
| Dhanush | `agent.py` Ex2 + `visualizer.py` Ex2 + `main.py` Ex2 + Testing | 🔴 Not Started |
| Nandan | GitHub + Bash + `config.yml` + Submission | 🔴 Not Started |

> Update status manually: 🔴 Not Started → 🟡 In Progress → 🟢 Done

---

*Last updated: —*
