import heapq
import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any

from config import (
    MAX_LIVES, WALK_TIME_COST, JUMP_TIME_COST, TURN_COST,
    CELL_LAND, CELL_VOLCANO, CELL_WATER, CELL_BRICK, CELL_START, CELL_GOAL,
    P_LAVA, P_WATER, P_LAND, P_WALL,
    P_THERMAL_GIVEN, P_SEISMIC_GIVEN,
    MAX_SCANS_PER_CELL, RISK_THRESHOLD,
)

HAZARD_CELLS = {CELL_VOLCANO, CELL_WATER}
SAFE_CELLS   = {CELL_LAND, CELL_START, CELL_GOAL}

@dataclass
class StepRecord:
    """One step in the simulation log (shared Ex1 & Ex2)."""
    step        : int
    from_cell   : Tuple[int,int]
    to_cell     : Tuple[int,int]
    action      : str            # 'walk' or 'jump'
    took_damage : bool
    lives       : int
    turns       : int
    time_units  : int
    score       : float
    beliefs     : Optional[List[List[Dict]]] = None   # Ex2 only
    scan_events : Optional[List[Dict]]       = None   # Ex2 only


@dataclass
class ScanRecord:
    """One sensor scan event (Ex2 only)."""
    cell      : Tuple[int,int]
    thermal   : bool
    seismic   : bool
    beliefs   : Dict[str,float]
    scan_num  : int
    turn_at   : int
class OracleAgentEx1:
    """
    Deterministic agent with perfect sensors.
    Uses A* to find the path that minimises score = (turns+time)/lives.
    (Lower score = better: fewer wasted actions, more lives preserved.)
    """

    def __init__(self, grid: List[List[str]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.goal = (self.rows-1, self.cols-1)

    # ── Sensors
    def thermal_sensor(self, r:int, c:int) -> bool:
        return self.grid[r][c] == CELL_VOLCANO

    def seismic_sensor(self, r:int, c:int) -> bool:
        return self.grid[r][c] == CELL_WATER

    def _cell_type(self, r:int, c:int) -> str:
        return self.grid[r][c]

    def _is_hazard(self, r:int, c:int) -> bool:
        return self.grid[r][c] in HAZARD_CELLS

    def _in_bounds(self, r:int, c:int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    # ── Neighbor generation
    def _neighbors(self, r:int, c:int):
        """
        Yields (nr, nc, action, time_cost, turn_cost).
        Walk: 1 cell, costs WALK_TIME_COST + TURN_COST.
        Jump: 2 cells (skip middle), costs JUMP_TIME_COST + TURN_COST.
        Cannot walk or jump INTO a brick wall.
        Cannot jump OVER a brick wall (middle cell must not be brick).
        If an invalid move is attempted (brick destination on walk):
            → costs only TURN_COST (bounce), no position change.
        """
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            # Walk
            nr, nc = r+dr, c+dc
            if self._in_bounds(nr, nc):
                if self.grid[nr][nc] != CELL_BRICK:
                    yield (nr, nc, 'walk', WALK_TIME_COST, TURN_COST)
                # brick walk → bounce, but we just skip it in planning
                # (handled by not yielding a valid move there)

            # Jump
            mr, mc = r+dr,   c+dc    # middle cell
            jr, jc = r+2*dr, c+2*dc  # landing cell
            if self._in_bounds(mr, mc) and self._in_bounds(jr, jc):
                if (self.grid[mr][mc] != CELL_BRICK and
                        self.grid[jr][jc] != CELL_BRICK):
                    yield (jr, jc, 'jump', JUMP_TIME_COST, TURN_COST)

    # ── Heuristic 
    def _heuristic(self, r:int, c:int, lives:int) -> float:
        """
        Admissible heuristic: minimum time to reach goal / current lives.
        Uses Manhattan distance / 2 (jump covers 2 cells in 3TU,
        walk covers 1 cell in 2TU; min per cell ≈ 1.5TU).
        Penalises low lives heavily.
        """
        gr, gc = self.goal
        manhattan = abs(r-gr) + abs(c-gc)
        min_time  = math.ceil(manhattan / 2) * JUMP_TIME_COST
        life_pen  = (MAX_LIVES - lives) * 4
        if lives <= 0:
            return float('inf')
        return (min_time + life_pen + manhattan) / lives

    # ── A* Search
    def a_star(self):
        """
        A* where state = (row, col, lives_remaining).
        Priority = estimated_score = (turns+time) / lives.
        Returns (path, total_turns, total_time, final_lives)
        or (None, ...) if no solution.
        """
        start = (0, 0)

        # heap: (priority, turns, time, lives, pos, path)
        heap = [(0.0, 0, 0, MAX_LIVES, start, [start])]
        best = {}   # state → best cost seen

        while heap:
            priority, turns, time_u, lives, pos, path = heapq.heappop(heap)
            r, c = pos

            key = (r, c, lives)
            if key in best and best[key] <= (turns + time_u):
                continue
            best[key] = turns + time_u

            if pos == self.goal:
                return path, turns, time_u, lives

            if lives <= 0:
                continue

            for nr, nc, action, t_cost, turn_cost in self._neighbors(r, c):
                new_turns = turns + turn_cost
                new_time  = time_u + t_cost
                new_lives = lives

                if self.grid[nr][nc] in HAZARD_CELLS:
                    new_lives -= 1

                if new_lives <= 0:
                    continue   # don't explore death states

                new_score = (new_turns + new_time) / new_lives
                h = self._heuristic(nr, nc, new_lives)
                prio = new_score + h * 0.1

                heapq.heappush(heap, (
                    prio, new_turns, new_time,
                    new_lives, (nr, nc), path + [(nr, nc)]
                ))

        return None, 0, 0, 0

    # ── Run simulation
    def run(self) -> Tuple[Optional[List[StepRecord]], Optional[List]]:
        """
        Find optimal path with A*, then simulate step by step.
        Returns (simulation_log, path) or (None, None).
        """
        path, _, _, _ = self.a_star()
        if path is None:
            print("[Ex1] No valid path found!")
            return None, None

        log   = []
        lives = MAX_LIVES
        turns = 0
        time_u = 0

        for i in range(len(path)-1):
            fc = path[i]
            tc = path[i+1]
            fr, ff = fc
            tr, tc_ = tc

            dist   = abs(tr-fr) + abs(tc_-ff)
            action = 'walk' if dist == 1 else 'jump'
            t_cost = WALK_TIME_COST if action == 'walk' else JUMP_TIME_COST

            turns  += TURN_COST
            time_u += t_cost

            cell_type   = self.grid[tr][tc_]
            took_damage = cell_type in HAZARD_CELLS
            if took_damage:
                lives -= 1

            score = (turns + time_u) / lives if lives > 0 else float('inf')

            log.append(StepRecord(
                step        = i+1,
                from_cell   = fc,
                to_cell     = tc,
                action      = action,
                took_damage = took_damage,
                lives       = lives,
                turns       = turns,
                time_units  = time_u,
                score       = score,
            ))

            if lives <= 0:
                print(f"[Ex1] Agent died at step {i+1}!")
                break

        return log, path


# ============================================================
#  Exercise 2  —  Probabilistic Oracle Agent
# ============================================================

class OracleAgentEx2:
    """
    Probabilistic agent with noisy sensors.
    Maintains belief maps for Volcano and Water.
    Uses Bayesian updates after each sensor scan.
    Explores multiple paths to find the optimal one.
    """

    def __init__(self, grid: List[List[str]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.goal = (self.rows-1, self.cols-1)
        
        # Initialize belief maps
        self.beliefs = self._init_beliefs()
        
        # Track scan history
        self.scan_log = []
        self.scan_counts = {}  # (r,c) -> count
        
        # Track multiple paths explored
        self.explored_paths = []
        self.best_path = None
        self.best_score = float('inf')

    def _init_beliefs(self) -> List[List[Dict]]:
        """Initialize belief maps with priors."""
        beliefs = []
        for r in range(self.rows):
            row_beliefs = []
            for c in range(self.cols):
                # Use correct priors from config
                bp = {
                    CELL_VOLCANO: P_LAVA,
                    CELL_WATER:   P_WATER,
                    CELL_LAND:    P_LAND,
                    CELL_BRICK:   P_WALL,
                }
                row_beliefs.append(bp)
            beliefs.append(row_beliefs)
        return beliefs

    def _normalize_beliefs(self, bp: Dict):
        """Normalize belief probabilities."""
        total = sum(bp.values())
        if total > 0:
            for key in bp:
                bp[key] /= total

    def _bayesian_update(self, r: int, c: int, thermal: bool, seismic: bool):
        """Update beliefs using Bayesian inference."""
        bp = self.beliefs[r][c]
        
        # Store original probabilities for debugging
        original_volcano = bp[CELL_VOLCANO]
        original_water = bp[CELL_WATER]
        
        # Thermal sensor update
        if thermal:
            # P(V|T+) = P(T+|V) * P(V) / P(T+)
            p_t_plus = (P_THERMAL_GIVEN['lava'] * bp[CELL_VOLCANO] +
                       P_THERMAL_GIVEN['land'] * bp[CELL_LAND] +
                       P_THERMAL_GIVEN['water'] * bp[CELL_WATER] +
                       P_THERMAL_GIVEN['wall'] * bp[CELL_BRICK])
            if p_t_plus > 0:
                bp[CELL_VOLCANO] = (P_THERMAL_GIVEN['lava'] * bp[CELL_VOLCANO]) / p_t_plus
        
        else:
            # P(V|T-) = P(T-|V) * P(V) / P(T-)
            p_t_minus = ((1 - P_THERMAL_GIVEN['lava']) * bp[CELL_VOLCANO] +
                        (1 - P_THERMAL_GIVEN['land']) * bp[CELL_LAND] +
                        (1 - P_THERMAL_GIVEN['water']) * bp[CELL_WATER] +
                        (1 - P_THERMAL_GIVEN['wall']) * bp[CELL_BRICK])
            if p_t_minus > 0:
                bp[CELL_VOLCANO] = ((1 - P_THERMAL_GIVEN['lava']) * bp[CELL_VOLCANO]) / p_t_minus

        # Seismic sensor update
        if seismic:
            # P(W|S+) = P(S+|W) * P(W) / P(S+)
            p_s_plus = (P_SEISMIC_GIVEN['water'] * bp[CELL_WATER] +
                       P_SEISMIC_GIVEN['lava'] * bp[CELL_VOLCANO] +
                       P_SEISMIC_GIVEN['land'] * bp[CELL_LAND] +
                       P_SEISMIC_GIVEN['wall'] * bp[CELL_BRICK])
            if p_s_plus > 0:
                bp[CELL_WATER] = (P_SEISMIC_GIVEN['water'] * bp[CELL_WATER]) / p_s_plus
        
        else:
            # P(W|S-) = P(S-|W) * P(W) / P(S-)
            p_s_minus = ((1 - P_SEISMIC_GIVEN['water']) * bp[CELL_WATER] +
                        (1 - P_SEISMIC_GIVEN['lava']) * bp[CELL_VOLCANO] +
                        (1 - P_SEISMIC_GIVEN['land']) * bp[CELL_LAND] +
                        (1 - P_SEISMIC_GIVEN['wall']) * bp[CELL_BRICK])
            if p_s_minus > 0:
                bp[CELL_WATER] = ((1 - P_SEISMIC_GIVEN['water']) * bp[CELL_WATER]) / p_s_minus

        # Normalize all probabilities
        self._normalize_beliefs(bp)
        
        # Debug output to show Bayesian updates
        if abs(bp[CELL_VOLCANO] - original_volcano) > 0.01 or abs(bp[CELL_WATER] - original_water) > 0.01:
            print(f"[Ex2] Bayesian update at ({r},{c}): V {original_volcano:.3f}→{bp[CELL_VOLCANO]:.3f}, "
                  f"W {original_water:.3f}→{bp[CELL_WATER]:.3f}, thermal={thermal}, seismic={seismic}")

    def _get_risk_score(self, r: int, c: int) -> float:
        """Calculate risk score for a cell based on beliefs."""
        bp = self.beliefs[r][c]
        return bp[CELL_VOLCANO] + bp[CELL_WATER]

    def _is_hazardous(self, r: int, c: int) -> bool:
        """Check if cell is considered hazardous based on risk threshold."""
        # Be more conservative - only avoid cells with very high risk
        return self._get_risk_score(r, c) > 0.8

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def _neighbors(self, r: int, c: int):
        """Generate valid neighbors for movement."""
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            # Walk
            nr, nc = r+dr, c+dc
            if self._in_bounds(nr, nc) and self.grid[nr][nc] != CELL_BRICK:
                yield (nr, nc, 'walk', WALK_TIME_COST, TURN_COST)

            # Jump
            mr, mc = r+dr,   c+dc    # middle cell
            jr, jc = r+2*dr, c+2*dc  # landing cell
            if (self._in_bounds(mr, mc) and self._in_bounds(jr, jc) and
                self.grid[mr][mc] != CELL_BRICK and self.grid[jr][jc] != CELL_BRICK):
                yield (jr, jc, 'jump', JUMP_TIME_COST, TURN_COST)

    def _heuristic(self, r: int, c: int, lives: int) -> float:
        """Heuristic considering risk and distance."""
        gr, gc = self.goal
        manhattan = abs(r-gr) + abs(c-gc)
        min_time = math.ceil(manhattan / 2) * JUMP_TIME_COST
        
        # Add risk penalty
        risk_penalty = self._get_risk_score(r, c) * 10
        
        if lives <= 0:
            return float('inf')
        return (min_time + risk_penalty) / lives

    def _scan_cell(self, r: int, c: int, turn_at: int) -> Tuple[bool, bool]:
        """Perform sensor scan on a cell."""
        cell_type = self.grid[r][c]
        
        # Thermal sensor (noisy)
        thermal_true = (cell_type == CELL_VOLCANO)
        if thermal_true:
            thermal = random.random() < P_THERMAL_GIVEN['lava']
        else:
            # For non-lava cells, use the false positive rate
            thermal = random.random() < P_THERMAL_GIVEN['land']
        
        # Seismic sensor (noisy)
        seismic_true = (cell_type == CELL_WATER)
        if seismic_true:
            seismic = random.random() < P_SEISMIC_GIVEN['water']
        else:
            # For non-water cells, use the false positive rate
            seismic = random.random() < P_SEISMIC_GIVEN['land']
        
        # Update beliefs
        self._bayesian_update(r, c, thermal, seismic)
        
        # Log the scan
        scan_record = ScanRecord(
            cell=cell_type,
            thermal=thermal,
            seismic=seismic,
            beliefs=dict(self.beliefs[r][c]),
            scan_num=self.scan_counts.get((r,c), 0) + 1,
            turn_at=turn_at
        )
        self.scan_log.append(scan_record)
        
        # Update scan count
        self.scan_counts[(r,c)] = self.scan_counts.get((r,c), 0) + 1
        
        return thermal, seismic

    def _noisy_sensor(self, true_value: bool, p_detect: float, p_false_alarm: float) -> bool:
        """Simulate noisy sensor reading."""
        if true_value:
            return random.random() < p_detect
        else:
            return random.random() < p_false_alarm

    def _a_star_with_beliefs(self, start: Tuple[int,int], max_scans: int = 5) -> Tuple[Optional[List], int, int, int]:
        """A* search with belief-based risk assessment."""
        heap = [(0.0, 0, 0, MAX_LIVES, start, [start], 0)]  # (priority, turns, time, lives, pos, path, scans_used)
        best = {}
        
        while heap:
            priority, turns, time_u, lives, pos, path, scans_used = heapq.heappop(heap)
            r, c = pos
            
            key = (r, c, lives, scans_used)
            if key in best and best[key] <= (turns + time_u):
                continue
            best[key] = turns + time_u
            
            if pos == self.goal:
                return path, turns, time_u, lives
            
            if lives <= 0 or scans_used >= max_scans:
                continue
            
            # Scan current cell if not scanned too many times
            if self.scan_counts.get((r,c), 0) < MAX_SCANS_PER_CELL:
                thermal, seismic = self._scan_cell(r, c, turns)
                scans_used += 1
            
            for nr, nc, action, t_cost, turn_cost in self._neighbors(r, c):
                # Check if cell is too risky
                if self._is_hazardous(nr, nc):
                    continue
                
                new_turns = turns + turn_cost
                new_time = time_u + t_cost
                new_lives = lives
                
                # Simulate damage based on beliefs (for planning)
                if self._get_risk_score(nr, nc) > 0.5:  # High risk
                    if random.random() < 0.7:  # 70% chance of damage
                        new_lives -= 1
                
                if new_lives <= 0:
                    continue
                
                new_score = (new_turns + new_time) / new_lives
                h = self._heuristic(nr, nc, new_lives)
                prio = new_score + h * 0.1
                
                heapq.heappush(heap, (
                    prio, new_turns, new_time, new_lives,
                    (nr, nc), path + [(nr, nc)], scans_used
                ))
        
        return None, 0, 0, 0

    def run(self) -> Tuple[Optional[List[StepRecord]], Optional[List]]:
        """Run multiple path explorations to find optimal path."""
        print("[Ex2] Exploring multiple paths with probabilistic sensors...")
        
        # Explore multiple paths with different scan limits
        for scan_limit in [3, 5, 7, 10]:
            print(f"[Ex2] Path exploration {scan_limit} scans...")
            path, turns, time_u, lives = self._a_star_with_beliefs((0,0), scan_limit)
            
            if path:
                score = (turns + time_u) / lives if lives > 0 else float('inf')
                self.explored_paths.append({
                    'path': path,
                    'turns': turns,
                    'time': time_u,
                    'lives': lives,
                    'score': score,
                    'scans': scan_limit
                })
                
                if score < self.best_score:
                    self.best_score = score
                    self.best_path = path
        
        if not self.explored_paths:
            print("[Ex2] No valid paths found!")
            return None, None
        
        # Simulate the best path
        print(f"[Ex2] Selected best path with score: {self.best_score:.4f}")
        return self._simulate_best_path()

    def _simulate_best_path(self) -> Tuple[List[StepRecord], List]:
        """Simulate the best path found."""
        if not self.best_path:
            return None, None
        
        log = []
        lives = MAX_LIVES
        turns = 0
        time_u = 0
        
        # Reset beliefs for clean simulation (or keep exploration beliefs)
        # Let's keep the exploration beliefs to show the learning
        print(f"[Ex2] Starting simulation with {len(self.scan_log)} scan events from exploration")
        
        for i in range(len(self.best_path)-1):
            fc = self.best_path[i]
            tc = self.best_path[i+1]
            fr, ff = fc
            tr, tc_ = tc
            
            dist = abs(tr-fr) + abs(tc_-ff)
            action = 'walk' if dist == 1 else 'jump'
            t_cost = WALK_TIME_COST if action == 'walk' else JUMP_TIME_COST
            
            turns += TURN_COST
            time_u += t_cost
            
            # Scan the destination cell (continue learning during simulation)
            if self.scan_counts.get((tr, tc_), 0) < MAX_SCANS_PER_CELL:
                thermal, seismic = self._scan_cell(tr, tc_, turns)
                print(f"[Ex2] Simulation scan at ({tr},{tc_}): thermal={thermal}, seismic={seismic}")
            
            # Check for damage
            cell_type = self.grid[tr][tc_]
            took_damage = cell_type in HAZARD_CELLS
            if took_damage:
                lives -= 1
                print(f"[Ex2] Damage taken at ({tr},{tc_}) - cell type: {cell_type}")
            
            score = (turns + time_u) / lives if lives > 0 else float('inf')
            
            # Show current beliefs for key cells
            current_beliefs = self.beliefs[tr][tc_]
            risk_score = current_beliefs[CELL_VOLCANO] + current_beliefs[CELL_WATER]
            
            log.append(StepRecord(
                step=i+1,
                from_cell=fc,
                to_cell=tc,
                action=action,
                took_damage=took_damage,
                lives=lives,
                turns=turns,
                time_units=time_u,
                score=score,
                beliefs=[row[:] for row in self.beliefs],  # Deep copy beliefs
                scan_events=self.scan_log[:]  # Copy scan events
            ))
            
            print(f"[Ex2] Step {i+1}: ({fr},{ff}) → ({tr},{tc_}) | Action: {action} | "
                  f"Risk: {risk_score:.3f} | Lives: {lives} | Score: {score:.3f}")
            
            if lives <= 0:
                print(f"[Ex2] Agent died at step {i+1}!")
                break
        
        return log, self.best_path


