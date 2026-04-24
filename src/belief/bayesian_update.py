"""
Bayesian Belief Engine for Oracle Agent.
Maintains probabilistic belief maps and computes information-theoretic values.
"""

import math
from typing import List, Dict, Tuple

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    GRID_ROWS, GRID_COLS,
    CELL_LAND, CELL_VOLCANO, CELL_WATER, CELL_BRICK,
    P_LAVA, P_WATER, P_LAND, P_WALL,
    P_THERMAL_GIVEN, P_SEISMIC_GIVEN,
    MAX_SCANS_PER_CELL,
)


class BeliefEngine:
    """
    Maintains a full belief distribution over cell types for every grid cell.
    Supports Bayesian updates, entropy calculation, and information gain.
    """

    def __init__(self, rows: int = GRID_ROWS, cols: int = GRID_COLS):
        self.rows = rows
        self.cols = cols
        self.beliefs = self._init_uniform_beliefs()
        self.scan_counts = {}
        self.scanned_cells = set()

    def _init_uniform_beliefs(self) -> List[List[Dict[str, float]]]:
        beliefs = []
        for _ in range(self.rows):
            row = []
            for _ in range(self.cols):
                row.append({
                    CELL_VOLCANO: P_LAVA,
                    CELL_WATER:   P_WATER,
                    CELL_LAND:    P_LAND,
                    CELL_BRICK:   P_WALL,
                })
            beliefs.append(row)
        return beliefs

    def get_belief(self, r: int, c: int) -> Dict[str, float]:
        return self.beliefs[r][c].copy()

    def get_risk(self, r: int, c: int) -> float:
        bp = self.beliefs[r][c]
        return bp[CELL_VOLCANO] + bp[CELL_WATER]

    def is_known_wall(self, r: int, c: int, threshold: float = 0.9) -> bool:
        return self.beliefs[r][c][CELL_BRICK] > threshold

    # ── Bayesian Update ───────────────────────────────────────

    def update(self, r: int, c: int, thermal: bool, seismic: bool):
        """Perform Bayesian update after receiving sensor readings."""
        bp = self.beliefs[r][c]

        # Thermal update for VOLCANO
        if thermal:
            p_t = (P_THERMAL_GIVEN['lava'] * bp[CELL_VOLCANO] +
                   P_THERMAL_GIVEN['land'] * bp[CELL_LAND] +
                   P_THERMAL_GIVEN['water'] * bp[CELL_WATER] +
                   P_THERMAL_GIVEN['wall'] * bp[CELL_BRICK])
            if p_t > 0:
                bp[CELL_VOLCANO] = (P_THERMAL_GIVEN['lava'] * bp[CELL_VOLCANO]) / p_t
        else:
            p_t = ((1 - P_THERMAL_GIVEN['lava']) * bp[CELL_VOLCANO] +
                   (1 - P_THERMAL_GIVEN['land']) * bp[CELL_LAND] +
                   (1 - P_THERMAL_GIVEN['water']) * bp[CELL_WATER] +
                   (1 - P_THERMAL_GIVEN['wall']) * bp[CELL_BRICK])
            if p_t > 0:
                bp[CELL_VOLCANO] = ((1 - P_THERMAL_GIVEN['lava']) * bp[CELL_VOLCANO]) / p_t

        # Seismic update for WATER
        if seismic:
            p_s = (P_SEISMIC_GIVEN['water'] * bp[CELL_WATER] +
                   P_SEISMIC_GIVEN['lava'] * bp[CELL_VOLCANO] +
                   P_SEISMIC_GIVEN['land'] * bp[CELL_LAND] +
                   P_SEISMIC_GIVEN['wall'] * bp[CELL_BRICK])
            if p_s > 0:
                bp[CELL_WATER] = (P_SEISMIC_GIVEN['water'] * bp[CELL_WATER]) / p_s
        else:
            p_s = ((1 - P_SEISMIC_GIVEN['water']) * bp[CELL_WATER] +
                   (1 - P_SEISMIC_GIVEN['lava']) * bp[CELL_VOLCANO] +
                   (1 - P_SEISMIC_GIVEN['land']) * bp[CELL_LAND] +
                   (1 - P_SEISMIC_GIVEN['wall']) * bp[CELL_BRICK])
            if p_s > 0:
                bp[CELL_WATER] = ((1 - P_SEISMIC_GIVEN['water']) * bp[CELL_WATER]) / p_s

        self._normalize(bp)
        self.scanned_cells.add((r, c))
        self.scan_counts[(r, c)] = self.scan_counts.get((r, c), 0) + 1

    def _normalize(self, bp: Dict[str, float]):
        total = sum(bp.values())
        if total > 0:
            for k in bp:
                bp[k] /= total

    # ── Information Theory ────────────────────────────────────

    def entropy(self, r: int, c: int) -> float:
        """Shannon entropy of belief for a cell."""
        bp = self.beliefs[r][c]
        h = 0.0
        for p in bp.values():
            if p > 1e-10:
                h -= p * math.log2(p)
        return h

    def expected_information_gain(self, r: int, c: int) -> float:
        """
        Compute expected information gain from scanning cell (r,c).
        EIG = H(current) - E[H(after scan)]
        """
        current_entropy = self.entropy(r, c)
        bp = self.beliefs[r][c]

        # Expected posterior entropy weighted by P(reading)
        expected_post = 0.0
        for thermal in [True, False]:
            for seismic in [True, False]:
                p_reading = self._reading_probability(r, c, thermal, seismic)
                if p_reading < 1e-10:
                    continue
                # Simulate update
                temp_bp = bp.copy()
                self._simulate_update(temp_bp, thermal, seismic)
                post_h = self._entropy_dict(temp_bp)
                expected_post += p_reading * post_h

        return max(0.0, current_entropy - expected_post)

    def _reading_probability(self, r: int, c: int, thermal: bool, seismic: bool) -> float:
        bp = self.beliefs[r][c]
        # P(thermal | cell) averaged over beliefs
        p_t = 0.0
        for cell_type, prob in bp.items():
            key = {'V': 'lava', 'W': 'water', 'L': 'land', 'B': 'wall'}[cell_type]
            p_thermal = P_THERMAL_GIVEN[key] if thermal else (1 - P_THERMAL_GIVEN[key])
            p_seismic = P_SEISMIC_GIVEN[key] if seismic else (1 - P_SEISMIC_GIVEN[key])
            p_t += prob * p_thermal * p_seismic
        return p_t

    def _simulate_update(self, bp: Dict[str, float], thermal: bool, seismic: bool):
        if thermal:
            p_t = sum(P_THERMAL_GIVEN[{'V':'lava','W':'water','L':'land','B':'wall'}[k]] * bp[k]
                      for k in bp)
            if p_t > 0:
                bp[CELL_VOLCANO] = (P_THERMAL_GIVEN['lava'] * bp[CELL_VOLCANO]) / p_t
        else:
            p_t = sum((1 - P_THERMAL_GIVEN[{'V':'lava','W':'water','L':'land','B':'wall'}[k]]) * bp[k]
                      for k in bp)
            if p_t > 0:
                bp[CELL_VOLCANO] = ((1 - P_THERMAL_GIVEN['lava']) * bp[CELL_VOLCANO]) / p_t

        if seismic:
            p_s = sum(P_SEISMIC_GIVEN[{'V':'lava','W':'water','L':'land','B':'wall'}[k]] * bp[k]
                      for k in bp)
            if p_s > 0:
                bp[CELL_WATER] = (P_SEISMIC_GIVEN['water'] * bp[CELL_WATER]) / p_s
        else:
            p_s = sum((1 - P_SEISMIC_GIVEN[{'V':'lava','W':'water','L':'land','B':'wall'}[k]]) * bp[k]
                      for k in bp)
            if p_s > 0:
                bp[CELL_WATER] = ((1 - P_SEISMIC_GIVEN['water']) * bp[CELL_WATER]) / p_s

        self._normalize(bp)

    @staticmethod
    def _entropy_dict(bp: Dict[str, float]) -> float:
        h = 0.0
        for p in bp.values():
            if p > 1e-10:
                h -= p * math.log2(p)
        return h

    # ── Cross-Episode Memory ──────────────────────────────────

    def merge_memory(self, memory: Dict[Tuple[int, int], Dict[str, float]], alpha: float = 0.1):
        """Blend cross-episode learned priors into current beliefs."""
        for (r, c), mem_belief in memory.items():
            bp = self.beliefs[r][c]
            for k in bp:
                bp[k] = (1 - alpha) * bp[k] + alpha * mem_belief.get(k, bp[k])
            self._normalize(bp)

    def to_array(self) -> List[List[Dict[str, float]]]:
        """Deep copy of beliefs."""
        return [[cell.copy() for cell in row] for row in self.beliefs]
