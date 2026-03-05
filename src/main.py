import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    GRID_ROWS, GRID_COLS,
    OUTPUT_DIR, FRAMES_DIR,
)
from grid_gen   import generate_grid, print_grid
from agent      import OracleAgentEx1, OracleAgentEx2
from visualizer import (
    save_ground_truth, save_initial_grid,
    render_simulation_ex1, render_simulation_ex2,
)



def print_path_info(path, anchor1, anchor2):
    print('\n── Ground Truth Path ')
    print(f'  Start   : {path[0]}')
    print(f'  Anchor1 : {anchor1}')
    print(f'  Anchor2 : {anchor2}')
    print(f'  Goal    : {path[-1]}')
    print(f'  Length  : {len(path)} cells')
    print('  Full path:')
    for i, cell in enumerate(path):
        marker = ''
        if cell == path[0]:    marker = '  ← START'
        elif cell == path[-1]: marker = '  ← GOAL'
        elif cell == anchor1:  marker = '  ← ANCHOR 1'
        elif cell == anchor2:  marker = '  ← ANCHOR 2'
        print(f'    [{i:3d}] {cell}{marker}')
    print()


def print_results(tag, log):
    if not log:
        print(f'[{tag}] No results.')
        return
    last = log[-1]
    print(f'\n── {tag} Results ')
    print(f'  Steps completed : {last.step}')
    print(f'  Final lives     : {last.lives}')
    print(f'  Total turns     : {last.turns}')
    print(f'  Total time units: {last.time_units}')
    print(f'  Final score     : {last.score:.4f}')
    status = 'VICTORY' if last.lives > 0 else 'FAILED'
    print(f'  Outcome         : {status}')
    print()



def main():
    print('=' * 60)
    print('  CS F407  —  Oracle Agent  —  BITS Pilani Hyderabad')
    print('=' * 60)

   
    for d in [OUTPUT_DIR, FRAMES_DIR]:
        os.makedirs(d, exist_ok=True)

    print(f'\nGenerating {GRID_ROWS}×{GRID_COLS} grid...')
    grid, path, anchor1, anchor2 = generate_grid(GRID_ROWS, GRID_COLS)


    print('\n── Initial Grid ')
    print_grid(grid)
    print_path_info(path, anchor1, anchor2)

   
    save_ground_truth(grid, path, anchor1, anchor2)
    save_initial_grid(grid)

 
    print('\n' + '='*60)
    print('  EXERCISE 1  —  Deterministic Oracle Agent')
    print('='*60)

    agent_ex1 = OracleAgentEx1(grid)
    print('[Ex1] Running A* search...')
    sim_log_ex1, path_ex1 = agent_ex1.run()

    print_results('Exercise 1', sim_log_ex1)

    if sim_log_ex1:
        render_simulation_ex1(grid, sim_log_ex1)

    print('\n' + '='*60)
    print('  EXERCISE 2  —  Probabilistic Oracle Agent')
    print('='*60)

    agent_ex2 = OracleAgentEx2(grid)   
    print('[Ex2] Running probabilistic A* with Bayesian sensors...')
    sim_log_ex2, path_ex2 = agent_ex2.run()

    print_results('Exercise 2', sim_log_ex2)

    if sim_log_ex2:
        print(f'[Ex2] Total sensor scans performed: {len(agent_ex2.scan_log)}')
        print(f'[Ex2] Paths explored: {len(agent_ex2.explored_paths)}')
        if agent_ex2.best_path:
            print(f'[Ex2] Best path length: {len(agent_ex2.best_path)} cells')
            print(f'[Ex2] Best path score: {agent_ex2.best_score:.4f}')
        
        
        render_simulation_ex2(grid, sim_log_ex2, agent_ex2.scan_log)

  
    print('\n' + '='*60)
    print('  OUTPUT FILES')
    print('='*60)
    output_files = [
        ('Ground truth PNG',    'outputs/ground_truth.png'),
        ('Initial grid PNG',    'outputs/initial_grid.png'),
        ('Ex1 simulation GIF',  'outputs/simulation_ex1.gif'),
        ('Ex1 frames',          'outputs/frames/'),
    ]
    for label, fpath in output_files:
        exists = '✓' if os.path.exists(fpath) else '✗'
        print(f'  [{exists}] {label:25s}  {fpath}')

    print('\nDone.')


if __name__ == '__main__':
    main()