import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import imageio.v2 as imageio
from typing import Dict

from config import (
    COLOR_LAND, COLOR_VOLCANO, COLOR_WATER, COLOR_BRICK,
    COLOR_START, COLOR_GOAL, COLOR_UNKNOWN,
    COLOR_WALK_ARROW, COLOR_JUMP_ARROW, COLOR_DAMAGE_ARROW,
    COLOR_PATH_BORDER, COLOR_AGENT,
    OUTPUT_DIR, FRAMES_DIR,
    GROUND_TRUTH_PNG, INITIAL_GRID_PNG,
    SIMULATION_GIF,
    CELL_LAND, CELL_VOLCANO, CELL_WATER, CELL_BRICK, CELL_START, CELL_GOAL,
)


CELL_COLORS = {
    CELL_LAND    : COLOR_LAND,
    CELL_VOLCANO : COLOR_VOLCANO,
    CELL_WATER   : COLOR_WATER,
    CELL_BRICK   : COLOR_BRICK,
    CELL_START   : COLOR_START,
    CELL_GOAL    : COLOR_GOAL,
}

TEXT_COLORS = {
    CELL_LAND    : 'white',
    CELL_VOLCANO : 'white',
    CELL_WATER   : 'white',
    CELL_BRICK   : 'white',
    CELL_START   : '#1a1a1a',
    CELL_GOAL    : '#1a1a1a',
}


def _ensure_dirs():
    for d in [OUTPUT_DIR, FRAMES_DIR]:
        os.makedirs(d, exist_ok=True)



def cell_to_xy(r, c, rows):
    """Convert grid (row,col) to matplotlib (x,y) centre coordinates."""
    return c + 0.5, rows - r - 0.5


def draw_grid_base(ax, grid, title=''):
    rows = len(grid)
    cols = len(grid[0])
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9, pad=4, fontweight='bold')
    ax.axis('off')

    for r in range(rows):
        for c in range(cols):
            ctype = grid[r][c]
            color = CELL_COLORS.get(ctype, COLOR_UNKNOWN)
            rect  = plt.Rectangle((c, rows-r-1), 1, 1,
                                   facecolor=color,
                                   edgecolor='white', linewidth=0.8)
            ax.add_patch(rect)
            ax.text(c+0.5, rows-r-0.5, ctype,
                    ha='center', va='center',
                    fontsize=8, fontweight='bold',
                    color=TEXT_COLORS.get(ctype, 'white'))


def draw_arrow(ax, from_cell, to_cell, action, took_damage, rows):
    """
    Draw movement arrow between two cells.
    Walk → black straight arrow.
    Jump → purple curved arrow.
    Damage turn → dotted/dashed red arrow.
    """
    fr, fc = from_cell
    tr, tc = to_cell
    fx, fy = cell_to_xy(fr, fc, rows)
    tx, ty = cell_to_xy(tr, tc, rows)

    if took_damage:
        color = COLOR_DAMAGE_ARROW
        style = 'dashed'
        rad   = 0.3
    elif action == 'jump':
        color = COLOR_JUMP_ARROW
        style = 'solid'
        rad   = 0.35
    else:
        color = COLOR_WALK_ARROW
        style = 'solid'
        rad   = 0.0

    conn = f'arc3,rad={rad}'
    ax.annotate('',
        xy=(tx, ty), xytext=(fx, fy),
        arrowprops=dict(
            arrowstyle     = '->, head_width=0.25, head_length=0.2',
            color          = color,
            lw             = 2.0,
            linestyle      = style,
            connectionstyle= conn,
        ),
        zorder=5,
    )


def draw_damage_marker(ax, cell, rows):
    """Draw red ✗ at a cell."""
    r, c = cell
    ax.text(c+0.5, rows-r-0.5, '✗',
            ha='center', va='center',
            fontsize=14, color='red',
            fontweight='bold', zorder=6)


def draw_agent(ax, cell, rows):
    """Draw filled circle representing agent's current position."""
    r, c = cell
    circle = plt.Circle((c+0.5, rows-r-0.5), 0.28,
                          color=COLOR_AGENT, zorder=7, alpha=0.9)
    ax.add_patch(circle)
    ax.text(c+0.5, rows-r-0.5, '●',
            ha='center', va='center',
            fontsize=7, color='white', fontweight='bold', zorder=8)




def save_ground_truth(grid, path, anchor1, anchor2):
    _ensure_dirs()
    rows = len(grid)
    cols = len(grid[0])
    fig, ax = plt.subplots(figsize=(cols*0.9, rows*0.9))
    draw_grid_base(ax, grid, title='Ground Truth Trajectory')

   
    for (r, c) in path:
        rect = plt.Rectangle((c, rows-r-1), 1, 1,
                               facecolor='none',
                               edgecolor=COLOR_PATH_BORDER, linewidth=2.5, zorder=3)
        ax.add_patch(rect)

    
    for i, (r, c) in enumerate([anchor1, anchor2], start=1):
        ax.text(c+0.5, rows-r-0.3, f'A{i}',
                ha='center', va='center',
                fontsize=7, color='yellow',
                fontweight='bold', zorder=9)

    
    patches = [
        mpatches.Patch(color=COLOR_PATH_BORDER, label='Ground-truth path'),
        mpatches.Patch(color=COLOR_VOLCANO,     label='Volcano (V)'),
        mpatches.Patch(color=COLOR_WATER,       label='Water (W)'),
        mpatches.Patch(color=COLOR_LAND,        label='Land (L)'),
        mpatches.Patch(color=COLOR_BRICK,       label='Brick (B)'),
    ]
    ax.legend(handles=patches, loc='upper right',
              fontsize=6, framealpha=0.8)

    plt.tight_layout()
    plt.savefig(GROUND_TRUTH_PNG, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {GROUND_TRUTH_PNG}')


def save_initial_grid(grid):
    _ensure_dirs()
    rows = len(grid)
    cols = len(grid[0])
    fig, ax = plt.subplots(figsize=(cols*0.9, rows*0.9))
    draw_grid_base(ax, grid, title='Initial Grid State')
    plt.tight_layout()
    plt.savefig(INITIAL_GRID_PNG, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {INITIAL_GRID_PNG}')




def _render_ex1_frame(grid, sim_log, step_idx, frame_path):
    rows = len(grid)
    cols = len(grid[0])
    step = sim_log[step_idx]

    title = (f'Step {step.step}  |  Lives: {step.lives}  |  '
             f'Score: {step.score:.3f}  |  '
             f'Turns: {step.turns}  |  Time: {step.time_units}')

    fig, ax = plt.subplots(figsize=(cols*0.9 + 1, rows*0.9 + 0.5))
    draw_grid_base(ax, grid, title=title)

    damage_cells = set()

    
    for s in sim_log[:step_idx+1]:
        draw_arrow(ax, s.from_cell, s.to_cell, s.action, s.took_damage, rows)
        if s.took_damage:
            damage_cells.add(s.to_cell)

 
    for cell in damage_cells:
        draw_damage_marker(ax, cell, rows)

  
    draw_agent(ax, step.to_cell, rows)

    plt.tight_layout()
    plt.savefig(frame_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def render_simulation_ex1(grid, sim_log):
    _ensure_dirs()
    if not sim_log:
        print('[Ex1] No simulation log to render.')
        return

    frames = []
    print(f'[Ex1] Rendering {len(sim_log)} frames...')
    for i in range(len(sim_log)):
        fp = os.path.join(FRAMES_DIR, f'frame_{i:04d}.png')
        _render_ex1_frame(grid, sim_log, i, fp)
        frames.append(imageio.imread(fp))

    imageio.mimsave(SIMULATION_GIF, frames, fps=2, loop=0)
    print(f'Saved: {SIMULATION_GIF}')




def _belief_color(bp: Dict) -> str:
    """Determine cell color based on beliefs."""
    if bp.get('V', 0) > 0.4:
        return COLOR_VOLCANO 
    elif bp.get('W', 0) > 0.4:
        return COLOR_WATER    
    elif bp.get('L', 0) > 0.5:
        return COLOR_LAND     
    else:
        return COLOR_UNKNOWN  

def _draw_belief_map(ax, beliefs, grid, title=''):
    """Draw left panel: belief map with risk percentages and scan indicators."""
    rows = len(grid)
    cols = len(grid[0])
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9, pad=4, fontweight='bold')
    ax.axis('off')

    for r in range(rows):
        for c in range(cols):
            
            color = _belief_color(beliefs[r][c])
            rect = plt.Rectangle((c, rows-r-1), 1, 1,
                               facecolor=color,
                               edgecolor='white', linewidth=0.8)
            ax.add_patch(rect)
            
          
            risk = beliefs[r][c].get('V', 0) + beliefs[r][c].get('W', 0)
            ax.text(c+0.5, rows-r-0.5, f'{risk*100:.0f}%',
                    ha='center', va='center',
                    fontsize=7, fontweight='bold',
                    color='black' if risk < 0.5 else 'white')

def _draw_ground_truth_map(ax, grid, title=''):
    """Draw right panel: ground truth with cell labels."""
    rows = len(grid)
    cols = len(grid[0])
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9, pad=4, fontweight='bold')
    ax.axis('off')

    for r in range(rows):
        for c in range(cols):
            ctype = grid[r][c]
            color = CELL_COLORS.get(ctype, COLOR_UNKNOWN)
            rect = plt.Rectangle((c, rows-r-1), 1, 1,
                               facecolor=color,
                               edgecolor='white', linewidth=0.8)
            ax.add_patch(rect)
            ax.text(c+0.5, rows-r-0.5, ctype,
                    ha='center', va='center',
                    fontsize=8, fontweight='bold',
                    color=TEXT_COLORS.get(ctype, 'white'))

def _render_ex2_frame(grid, beliefs, sim_log, step_idx, frame_path):
    """Render dual-panel frame for Exercise 2."""
    rows = len(grid)
    cols = len(grid[0])
    step = sim_log[step_idx]

    title = (f'Step {step.step}  |  Lives: {step.lives}  |  '
             f'Score: {step.score:.3f}  |  '
             f'Turns: {step.turns}  |  Time: {step.time_units}')

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(cols*1.8 + 2, rows*0.9 + 0.5))
    
   
    _draw_belief_map(ax_left, beliefs, grid, title='Belief Map (Agent View)')
    
    
    _draw_ground_truth_map(ax_right, grid, title='Ground Truth')
    
    damage_cells = set()

    
    for s in sim_log[:step_idx+1]:
        draw_arrow(ax_left, s.from_cell, s.to_cell, s.action, s.took_damage, rows)
        draw_arrow(ax_right, s.from_cell, s.to_cell, s.action, s.took_damage, rows)
        if s.took_damage:
            damage_cells.add(s.to_cell)

    
    for cell in damage_cells:
        draw_damage_marker(ax_left, cell, rows)
        draw_damage_marker(ax_right, cell, rows)

   
    draw_agent(ax_left, step.to_cell, rows)
    draw_agent(ax_right, step.to_cell, rows)

    plt.tight_layout()
    plt.savefig(frame_path, dpi=100, bbox_inches='tight')
    plt.close(fig)

def render_simulation_ex2(grid, sim_log, scan_log):
    """Render Exercise 2 dual-panel animation.""" 
    _ensure_dirs()
    if not sim_log:
        print('[Ex2] No simulation log to render.')
        return

    frames_dir_ex2 = 'outputs/frames_ex2'
    os.makedirs(frames_dir_ex2, exist_ok=True)

    frames = []
    print(f'[Ex2] Rendering {len(sim_log)} dual-panel frames...')
    for i in range(len(sim_log)):
        fp = os.path.join(frames_dir_ex2, f'frame_{i:04d}.png')
        beliefs = sim_log[i].beliefs if sim_log[i].beliefs else [[{'V': 0.24, 'W': 0.24, 'L': 0.16, 'B': 0.36} for _ in range(len(grid[0]))] for _ in range(len(grid))]
        _render_ex2_frame(grid, beliefs, sim_log, i, fp)
        frames.append(imageio.imread(fp))

    sim_gif_ex2 = 'outputs/simulation_ex2.gif'
    imageio.mimsave(sim_gif_ex2, frames, fps=2, loop=0)
    print(f'Saved: {sim_gif_ex2}')


