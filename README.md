# CSF407_2026_2022A4PS0398H - Oracle Agent

This is our submission for Project Assignment 1 of CS F407 (Artificial Intelligence).

---

## Group Details

Group ID: CSF407_2026_2022A4PS0398H

Group Leader  
Name – Nandana Krishna Konduru
ID – 2022A4PS0398H

Member 2  
Name –  Allipuram Samanyu Reddy
ID – 2023A2PS0910H

Member 3  
Name – Rohith Srinivas Bollineni
ID – 2022A7PS1294H

Member 4  
Name – Dhanush Reddy J 
ID – 2022A7PS0005H

---

## What This Project Is About

We built an agent called Oracle that has to navigate through a grid full of hazards and reach the goal without dying. The grid has volcanoes, water bodies, land, and brick walls. The agent starts at the top left corner and has to reach the bottom right corner.

We did this in two parts:

**Exercise 1** - The agent can see everything clearly. It knows exactly what each cell is and uses A* search to find the best path.

**Exercise 2** - The agent is now blind. It cannot see what type each cell is. It uses two noisy sensors (thermal and seismic) and applies Bayesian inference to guess what each cell might be before deciding to move.

---

## File Structure

```
CSF407_2026_IDX/
├── src/
│   ├── config.py         all the parameters and settings
│   ├── grid_gen.py       generates the grid and the path
│   ├── agent.py          the Oracle agent for both exercises
│   ├── visualizer.py     draws the grid and saves the animation
│   └── main.py           run this file to start everything
├── outputs/              all generated images and GIFs go here
├── config.yml            conda environment file
└── README.md             this file
```

---

## How to Set Up and Run

**Step 1: Create the conda environment**

```bash
conda env create -f config.yml
```

**Step 2: Activate the environment**

```bash
conda activate CSF407_2026_2022A4PS0398H
```

**Step 3: Go into the src folder and run**

```bash
cd src
python main.py
```

That's it. The program will generate the grid, run both agents, and save everything to the outputs folder.

---

## What Gets Generated

After running main.py you will find these files in the outputs folder:

- ground_truth.png - shows the grid with the safe path highlighted in yellow
- initial_grid.png - shows the full generated grid before the agent runs
- simulation_ex1.gif - animated simulation of Exercise 1 step by step
- simulation_ex2.gif - animated simulation of Exercise 2 with the belief map and ground truth side by side
- frames/ - all individual PNG frames for Exercise 1
- frames_ex2/ - all individual PNG frames for Exercise 2

---

## How the Grid is Generated

The grid is between 8x8 and 10x10 cells. We used a 9x9 grid.

The grid generation works like this:

1. We first pick two anchor cells. One goes in the top left region of the grid and the other goes in the bottom right region. They have to be in different rows and different columns so the path is not just a straight line.

2. We then build a path from (0,0) to anchor1 to anchor2 to (8,8) using a random walk. We added some noise to the walk (around 30% chance of taking a random step instead of going toward the goal) so that the path looks different every time the program runs.

3. On this path, we place exactly 2 volcanoes and 2 water tiles. We make sure the same type of hazard is never placed next to itself on the path.

4. For all the cells that are not on the path, we randomly fill them as 50% hazards, 40% land, and 10% brick walls.

---

## How the Agent Works

**Exercise 1 Agent**

The agent uses A* search. The state is the current position plus how many lives are left. The cost function is (turns + time units) divided by lives remaining. The agent tries to minimize this, which means it prefers paths where it keeps more lives and wastes less time.

- Walking 1 cell costs 2 time units and 1 turn
- Jumping 2 cells (skipping the middle) costs 3 time units and 1 turn
- Jumping over a brick wall is not allowed
- Stepping on a volcano or water costs 1 life
- Dying means 0 lives which ends the episode

**Exercise 2 Agent**

The agent starts with no knowledge of the grid. Every cell starts with these prior probabilities:

- P(Volcano) = 0.24
- P(Water) = 0.24
- P(Land) = 0.16
- P(Brick) = 0.36

Before moving to a risky cell, the agent can scan it. Each scan gives a noisy reading from the thermal and seismic sensors. The agent updates its belief using Bayes theorem after each scan. It can scan each cell up to 4 times. After 4 scans the cell is marked as blocked.

The thermal and seismic values used for the Bayesian update come from the conditional probability table given in the assignment.

---

## Visualization Details

**Exercise 1:**
- Black straight arrows for walking
- Purple curved arrows for jumping
- Red dashed arrows when the agent takes damage that turn
- Red X symbol at cells where the agent lost a life
- Title bar shows lives, score, turns, and time at each step

**Exercise 2:**
- Left panel shows the agent's belief map with risk percentages in each cell
- Right panel shows the actual ground truth grid
- Cells with yellow borders have been scanned
- The sensor readings (T: True/False, S: True/False) are shown on scanned cells
- Both panels are synchronized to the same step

---

## Dependencies

Everything is in config.yml. The main ones are:

- Python 3.10
- numpy
- matplotlib
- pillow
- imageio with ffmpeg support

---

## Notes

- The path generated is different every time you run main.py. This is by design.
- Exercise 2 uses the exact same grid as Exercise 1. Only the agent changes.
- If the program runs slowly on Exercise 2, it is because the agent is scanning cells during the A* search. This is normal behavior.
- All outputs are saved automatically. You do not need to do anything extra after running main.py.