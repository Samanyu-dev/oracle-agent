import random
from collections import deque

try:
    import numpy as np
except ImportError:
    np = None
from config import (
    GRID_ROWS, GRID_COLS,
    CELL_LAND, CELL_VOLCANO, CELL_WATER, CELL_BRICK, CELL_START, CELL_GOAL,
    HAZARD_RATIO, LAND_RATIO, PATH_VOLCANOES, PATH_WATERS,
)



def _bfs_path(grid_blocked, start, end, rows, cols):
    """
    BFS from start to end avoiding CELL_BRICK cells.
    grid_blocked is a set of (r,c) that are impassable.
    Returns list of (r,c) from start to end inclusive, or None.
    """
    queue = deque()
    queue.append((start, [start]))
    visited = {start}
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            return path
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr,nc) not in visited
                    and (nr,nc) not in grid_blocked):
                visited.add((nr,nc))
                queue.append(((nr,nc), path+[(nr,nc)]))
    return None


def _random_walk_segment(start, end, rows, cols, avoid=None, noise=0.35):
    """
    Walk from start to end using a biased random walk.
    avoid  : set of cells to avoid if possible
    noise  : probability of taking a random orthogonal step instead of goal-directed
    Returns list of cells from start to end inclusive.
    Falls back to BFS if random walk fails.
    """
    if avoid is None:
        avoid = set()

    path    = [start]
    current = start
    visited = {start}
    max_steps = rows * cols * 4

    for _ in range(max_steps):
        if current == end:
            break
        r, c  = current
        er, ec = end

      
        directed = []
        if r < er: directed.append((r+1, c))
        if r > er: directed.append((r-1, c))
        if c < ec: directed.append((r, c+1))
        if c > ec: directed.append((r, c-1))

        
        all_moves = [(r+dr, c+dc) for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]]

        def valid(cell):
            nr, nc = cell
            return (0 <= nr < rows and 0 <= nc < cols
                    and cell not in visited)

        directed = [m for m in directed if valid(m)]
        all_ok   = [m for m in all_moves if valid(m)]

        if not directed and not all_ok:
            break   

        use_noise = random.random() < noise and all_ok
        candidates = all_ok if use_noise else (directed if directed else all_ok)

        
        preferred = [m for m in candidates if m not in avoid]
        chosen = random.choice(preferred if preferred else candidates)

        path.append(chosen)
        visited.add(chosen)
        current = chosen

    if current != end:
       
        bfs = _bfs_path(set(), current, end, rows, cols)
        if bfs:
            for cell in bfs[1:]:
                if cell not in visited:
                    path.append(cell)
                    visited.add(cell)
                current = cell
        else:
            return None

    return path


def generate_unique_path(rows, cols):
    """
    Generate a unique randomized path:
      (0,0) → anchor1 → anchor2 → (rows-1, cols-1)

    Anchor constraints:
    - anchor1 in top-left quadrant (row in [1, rows//2-1], col in [1, cols//2-1])
    - anchor2 in bottom-right quadrant
    - Different rows AND different columns
    - Not adjacent to each other (chebyshev dist > 2)
    - Both are Land cells

    Returns: (path, anchor1, anchor2)
    """
    start = (0, 0)
    goal  = (rows-1, cols-1)

    max_attempts = 200
    for _ in range(max_attempts):
        
        r1 = random.randint(1, rows//2 - 1)
        c1 = random.randint(1, cols//2 - 1)

        
        r2 = random.randint(rows//2, rows-2)
        c2 = random.randint(cols//2, cols-2)

       
        if r1 == r2 or c1 == c2:
            continue
        if abs(r1-r2) <= 2 and abs(c1-c2) <= 2:
            continue
        
        if (r1,c1) in [start, goal] or (r2,c2) in [start, goal]:
            continue

        anchor1 = (r1, c1)
        anchor2 = (r2, c2)

       
        seg1 = _random_walk_segment(start,   anchor1, rows, cols, noise=0.30)
        seg2 = _random_walk_segment(anchor1, anchor2, rows, cols, noise=0.30,
                                    avoid=set(seg1) if seg1 else set())
        avoid_so_far = set(seg1 or []) | set(seg2 or [])
        seg3 = _random_walk_segment(anchor2, goal,    rows, cols, noise=0.30,
                                    avoid=avoid_so_far)

        if not seg1 or not seg2 or not seg3:
            continue

        
        seen = set()
        full_path = []
        for cell in seg1 + seg2[1:] + seg3[1:]:
            if cell not in seen:
                seen.add(cell)
                full_path.append(cell)

        
        if anchor1 not in seen or anchor2 not in seen:
            continue

        return full_path, anchor1, anchor2

    raise RuntimeError("Could not generate a valid path after many attempts. "
                       "Try increasing grid size.")


def place_hazards_on_path(path, anchor1, anchor2):
    """
    Place exactly PATH_VOLCANOES Volcanoes and PATH_WATERS Waters
    on path cells (excluding start, goal, and anchor cells).
    Same hazard type must not be adjacent on the path.

    Returns dict: (r,c) → cell_type for ALL path cells.
    """
    protected = {path[0], path[-1], anchor1, anchor2}

    
    eligible = [i for i, cell in enumerate(path) if cell not in protected]

    def non_adjacent_pick(pool, n, already_placed, path):
        """Pick n indices from pool such that no two are path-adjacent."""
        random.shuffle(pool)
        picked = []
        for idx in pool:
            if idx in already_placed:
                continue
            r, c   = path[idx]
            conflict = False
            for pi in picked:
                pr, pc = path[pi]
                if abs(r-pr) + abs(c-pc) <= 1:
                    conflict = True
                    break
            if not conflict:
                picked.append(idx)
            if len(picked) == n:
                return picked
        return None 

    for _ in range(500):
        pool = list(eligible)
        volcano_idx = non_adjacent_pick(pool, PATH_VOLCANOES, [], path)
        if volcano_idx is None:
            continue
        water_idx = non_adjacent_pick(
            [i for i in pool if i not in volcano_idx],
            PATH_WATERS, volcano_idx, path
        )
        if water_idx is None:
            continue

     
        volcano_set = set(volcano_idx)
        water_set   = set(water_idx)
        result = {}
        for i, cell in enumerate(path):
            if i == 0:
                result[cell] = CELL_START
            elif i == len(path)-1:
                result[cell] = CELL_GOAL
            elif i in volcano_set:
                result[cell] = CELL_VOLCANO
            elif i in water_set:
                result[cell] = CELL_WATER
            else:
                result[cell] = CELL_LAND
        return result

    raise RuntimeError("Could not place hazards on path without adjacency conflicts.")


def generate_grid(rows=GRID_ROWS, cols=GRID_COLS, seed=None):
    """
    Full grid generation pipeline.

    Steps:
    1. Generate unique random path with two anchor cells.
    2. Place exactly 2V + 2W on path (non-adjacent same type).
    3. Fill non-path cells: 50% hazard, 40% land, 10% brick.

    Returns: (grid 2D list, path list, anchor1, anchor2)
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    path, anchor1, anchor2 = generate_unique_path(rows, cols)
    path_types = place_hazards_on_path(path, anchor1, anchor2)

    path_set = set(path)

    grid = [[None]*cols for _ in range(rows)]
    for (r,c), ctype in path_types.items():
        grid[r][c] = ctype

   
    non_path = [(r,c) for r in range(rows) for c in range(cols)
                if (r,c) not in path_set]
    random.shuffle(non_path)
    n = len(non_path)

    n_hazard = int(n * HAZARD_RATIO)
    n_land   = int(n * LAND_RATIO)
    

    
    hazard_pool = [CELL_VOLCANO, CELL_WATER] * (n_hazard // 2 + 1)
    random.shuffle(hazard_pool)

    for i, (r,c) in enumerate(non_path):
        if i < n_hazard:
            grid[r][c] = hazard_pool[i % len(hazard_pool)]
        elif i < n_hazard + n_land:
            grid[r][c] = CELL_LAND
        else:
            grid[r][c] = CELL_BRICK

    
    grid[0][0]           = CELL_START
    grid[rows-1][cols-1] = CELL_GOAL

    return grid, path, anchor1, anchor2


def print_grid(grid):
    """Pretty-print grid to terminal."""
    rows = len(grid)
    cols = len(grid[0])
    col_header = '     ' + '  '.join(f'{c:2d}' for c in range(cols))
    print(col_header)
    print('     ' + '----'*cols)
    for r in range(rows):
        row_str = '  '.join(f'{grid[r][c]:2s}' for c in range(cols))
        print(f'  {r:2d} | {row_str}')
    print()