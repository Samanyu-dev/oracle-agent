from __future__ import annotations

import html
import math
import os
import random
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.api.simulation import SimulationSession
from env.grid_world import GridWorld


MISSION_MODES: List[Tuple[str, str]] = [
    ('survival', 'Survival // Endure dynamic hazards'),
    ('extraction', 'Extraction // Secure route to evac zone'),
    ('recon', 'Recon // Rapidly map unknown sectors'),
    ('escape', 'Escape // Breakout with minimum damage'),
    ('hazard-sweep', 'Hazard Sweep // Tag and neutralize danger'),
    ('blackout', 'Blackout Mode // Limited visual confidence'),
    ('infinite-terrain', 'Infinite Terrain // Extended simulation sectors'),
    ('sensor-failure', 'Sensor Failure // Noisy telemetry regime'),
    ('rl-arena', 'RL Arena // Policy adaptation battleground'),
    ('adaptive-nightmare', 'Adaptive Nightmare // Hostile uncertainty surge'),
]

DIFFICULTY_PRESETS: Dict[str, Dict[str, Any]] = {
    'easy': {'label': 'Easy', 'grid_size': 8, 'default_mcts': False, 'hazard_drift': 0.012, 'hazard_bias': 0.24},
    'tactical': {'label': 'Tactical', 'grid_size': 9, 'default_mcts': True, 'hazard_drift': 0.022, 'hazard_bias': 0.34},
    'veteran': {'label': 'Veteran', 'grid_size': 11, 'default_mcts': True, 'hazard_drift': 0.03, 'hazard_bias': 0.39},
    'impossible': {'label': 'Impossible', 'grid_size': 13, 'default_mcts': True, 'hazard_drift': 0.037, 'hazard_bias': 0.45},
    'chaos-ai': {'label': 'Chaos AI', 'grid_size': 15, 'default_mcts': True, 'hazard_drift': 0.051, 'hazard_bias': 0.53},
}

MISSION_DRIFT: Dict[str, float] = {
    'survival': 0.008,
    'extraction': 0.004,
    'recon': 0.003,
    'escape': 0.006,
    'hazard-sweep': -0.006,
    'blackout': 0.008,
    'infinite-terrain': 0.012,
    'sensor-failure': 0.005,
    'rl-arena': 0.009,
    'adaptive-nightmare': 0.022,
}

TILE_LABELS = {
    'L': 'Safe Corridor',
    'V': 'Lava Field',
    'W': 'Flooded Zone',
    'B': 'Reinforced Wall',
    'S': 'Deployment Cell',
    'G': 'Extraction Zone',
}

AGENT_OPTIONS = ['Deterministic', 'Bayesian', 'RL']
ACTION_OVERRIDE = ['AUTO'] + GridWorld.ACTIONS

BOOT_SEQUENCE_HTML = """
<div class="oracle-boot-layer">
  <div class="oracle-boot-grid"></div>
  <div class="oracle-boot-panel">
    <p class="boot-title">ORACLE // AUTONOMOUS TACTICAL INTELLIGENCE SYSTEM</p>
    <div class="boot-console">
      <p>&gt; INITIALIZING COMBAT RUNTIME...</p>
      <p>&gt; SYNCHRONIZING SENSOR ARRAY...</p>
      <p>&gt; CALIBRATING BAYESIAN ENGINE...</p>
      <p>&gt; ESTABLISHING MISSION GRID...</p>
      <p>&gt; NEURAL COMMAND LINK READY.</p>
    </div>
    <div class="boot-load">
      <div class="boot-load-fill"></div>
    </div>
  </div>
</div>
"""

TITLE_SHELL_HTML = """
<section class="oracle-title-shell">
  <div>
    <p class="oracle-kicker">ORACLE GRID // ADAPTIVE SURVIVAL SIMULATION</p>
    <h1>Command an autonomous tactical intelligence unit.</h1>
    <p class="oracle-subtitle">Live grid world, dynamic hazards, Bayesian cognition, and policy arbitration in one playable command surface.</p>
  </div>
  <div class="oracle-chip-row">
    <span class="oracle-chip">TACTICAL SIM</span>
    <span class="oracle-chip">AI COGNITION</span>
    <span class="oracle-chip">REPLAY READY</span>
  </div>
</section>
"""

ORACLE_CSS = """
:root {
  --bg-deep: #02050b;
  --panel-bg: rgba(6, 14, 27, 0.82);
  --panel-edge: rgba(99, 235, 255, 0.28);
  --hud-cyan: #7ceeff;
  --hud-cyan-soft: #3db3d1;
  --hud-green: #9cffc7;
  --hud-warn: #ffd28d;
  --hud-crit: #ff8f8f;
}

* {
  box-sizing: border-box;
}

body, html {
  margin: 0;
  background: radial-gradient(circle at 18% 9%, #0a2d3b 0%, transparent 32%), radial-gradient(circle at 84% 11%, #102848 0%, transparent 28%), linear-gradient(180deg, #030710 0%, #04060d 50%, #020307 100%);
}

.gradio-container {
  max-width: 100% !important;
  background: transparent !important;
  font-family: "Rajdhani", "Segoe UI", sans-serif;
}

#oracle-hf-root {
  min-height: 100vh;
  padding: 0.8rem;
  color: #e8fdff;
}

#oracle-main-grid {
  gap: 0.7rem !important;
  align-items: stretch !important;
}

#oracle-command,
#oracle-world-col,
#oracle-brain-col {
  border: 1px solid var(--panel-edge);
  border-radius: 14px;
  background:
    linear-gradient(180deg, rgba(11, 23, 38, 0.82), rgba(3, 9, 18, 0.9)),
    radial-gradient(circle at 22% 8%, rgba(48, 129, 149, 0.33), transparent 38%);
  box-shadow: inset 0 0 36px rgba(87, 233, 255, 0.07), 0 24px 60px rgba(0, 0, 0, 0.45);
}

#oracle-command {
  padding: 0.7rem;
}

#oracle-world-col,
#oracle-brain-col {
  padding: 0.45rem;
}

.oracle-panel-title {
  margin: 0 0 0.4rem;
  font-family: "Orbitron", "Segoe UI", sans-serif;
  font-size: 0.87rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #d7f7ff;
}

.oracle-panel-subtitle {
  margin: 0 0 0.65rem;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.13em;
  color: rgba(179, 243, 255, 0.72);
}

.oracle-title-shell {
  margin-bottom: 0.7rem;
  border: 1px solid rgba(130, 246, 255, 0.3);
  border-radius: 14px;
  padding: 0.75rem 0.95rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background:
    linear-gradient(180deg, rgba(7, 18, 33, 0.88), rgba(4, 9, 19, 0.92)),
    radial-gradient(circle at 12% 24%, rgba(50, 152, 179, 0.24), transparent 40%);
  box-shadow: inset 0 0 40px rgba(67, 219, 255, 0.08);
}

.oracle-kicker {
  margin: 0;
  color: rgba(169, 244, 255, 0.74);
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.64rem;
}

.oracle-title-shell h1 {
  margin: 0.2rem 0 0.18rem;
  font-family: "Orbitron", "Segoe UI", sans-serif;
  font-size: 1.34rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.oracle-subtitle {
  margin: 0;
  color: rgba(196, 248, 255, 0.84);
  font-size: 0.84rem;
}

.oracle-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.oracle-chip {
  border: 1px solid rgba(127, 240, 255, 0.42);
  border-radius: 999px;
  background: rgba(8, 23, 37, 0.72);
  color: #d9fbff;
  padding: 0.33rem 0.7rem;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-family: "Orbitron", "Segoe UI", sans-serif;
}

.oracle-boot-layer {
  position: fixed;
  inset: 0;
  z-index: 90;
  background: rgba(2, 4, 8, 0.98);
  animation: bootFadeOut 5.2s ease forwards;
  pointer-events: none;
}

.oracle-boot-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(93, 233, 255, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(93, 233, 255, 0.07) 1px, transparent 1px);
  background-size: 36px 36px;
}

.oracle-boot-panel {
  position: absolute;
  width: min(840px, 90vw);
  left: 50%;
  top: 14vh;
  transform: translateX(-50%);
  border-radius: 14px;
  border: 1px solid rgba(115, 244, 255, 0.4);
  background: rgba(2, 8, 17, 0.9);
  padding: 1rem;
  box-shadow: 0 0 60px rgba(80, 217, 250, 0.22);
}

.boot-title {
  margin: 0;
  color: #c7f9ff;
  font-family: "Orbitron", "Segoe UI", sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.76rem;
}

.boot-console {
  margin-top: 0.7rem;
  border: 1px solid rgba(102, 224, 247, 0.33);
  border-radius: 10px;
  background: rgba(3, 12, 23, 0.86);
  padding: 0.55rem 0.7rem;
  font-family: "Share Tech Mono", monospace;
  font-size: 0.78rem;
  line-height: 1.55;
  color: #91f5ff;
}

.boot-console p {
  margin: 0;
  opacity: 0;
  animation: bootLineIn 0.45s ease forwards;
}

.boot-console p:nth-child(1) { animation-delay: 0.28s; }
.boot-console p:nth-child(2) { animation-delay: 0.62s; }
.boot-console p:nth-child(3) { animation-delay: 0.98s; }
.boot-console p:nth-child(4) { animation-delay: 1.33s; }
.boot-console p:nth-child(5) { animation-delay: 1.7s; }

.boot-load {
  margin-top: 0.7rem;
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(95, 245, 255, 0.2);
}

.boot-load-fill {
  height: 100%;
  width: 0%;
  border-radius: 999px;
  background: linear-gradient(90deg, #75f6ff, #98ffc5);
  animation: bootLoad 3.1s ease forwards;
}

#world-render,
#brain-render,
#feed-render,
#status-render {
  min-height: 0 !important;
}

.oracle-world-shell {
  position: relative;
  border-radius: 12px;
  border: 1px solid rgba(116, 235, 255, 0.25);
  background: linear-gradient(180deg, rgba(4, 11, 22, 0.92), rgba(2, 6, 14, 0.95));
  padding: 0.55rem;
  overflow: hidden;
}

.world-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.6rem;
  margin-bottom: 0.44rem;
}

.world-header p {
  margin: 0;
}

.world-h1 {
  font-family: "Orbitron", "Segoe UI", sans-serif;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 0.75rem;
}

.world-h2 {
  margin-top: 0.16rem !important;
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.13em;
  color: rgba(172, 241, 255, 0.7);
}

.world-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.35rem;
}

.world-badge {
  border-radius: 999px;
  border: 1px solid rgba(115, 237, 255, 0.38);
  padding: 0.22rem 0.45rem;
  font-size: 0.57rem;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  background: rgba(4, 18, 31, 0.72);
  font-family: "Orbitron", "Segoe UI", sans-serif;
}

.world-stage {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(98, 223, 255, 0.24);
  background:
    radial-gradient(circle at 20% 18%, rgba(18, 64, 76, 0.45), transparent 42%),
    radial-gradient(circle at 82% 16%, rgba(30, 72, 101, 0.45), transparent 38%),
    #02060f;
  min-height: 530px;
}

.world-stage::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(114, 240, 255, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(114, 240, 255, 0.07) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events: none;
}

.world-stage::after {
  content: "";
  position: absolute;
  inset: -40% 0 0 0;
  background: linear-gradient(180deg, transparent, rgba(113, 249, 255, 0.08), transparent);
  animation: radarSweep 4.4s linear infinite;
  pointer-events: none;
}

.world-camera {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  transition: transform 240ms ease;
}

.oracle-grid {
  width: 100%;
  height: 100%;
  display: grid;
  gap: 2px;
  padding: 2px;
  background: rgba(116, 236, 255, 0.11);
}

.oracle-tile {
  position: relative;
  border-radius: 5px;
  border: 1px solid rgba(109, 222, 246, 0.12);
  overflow: hidden;
  min-height: 0;
}

.oracle-tile .tile-risk {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 45%, rgba(255, 104, 87, calc(var(--risk) * 0.62)), transparent 72%);
  pointer-events: none;
}

.oracle-tile .tile-entropy {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(79, 233, 255, calc(var(--entropy) * 0.16)), transparent 80%);
  pointer-events: none;
}

.oracle-tile .tile-scan {
  position: absolute;
  top: 2px;
  right: 3px;
  font-size: 0.53rem;
  font-family: "Share Tech Mono", monospace;
  color: #dbfdff;
  opacity: 0.92;
}

.oracle-tile .tile-path {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 5px;
  height: 5px;
  border-radius: 999px;
  transform: translate(-50%, -50%);
  background: rgba(190, 255, 211, 0.86);
  box-shadow: 0 0 12px rgba(190, 255, 211, 0.86);
}

.oracle-tile.t-s {
  background: radial-gradient(circle at 38% 35%, #67ffd7, #0b6555 62%);
}

.oracle-tile.t-g {
  background: radial-gradient(circle at 40% 35%, #ffe886, #8d5d11 62%);
}

.oracle-tile.t-l {
  background: linear-gradient(160deg, #103a34, #0b2327 62%, #06181c);
}

.oracle-tile.t-v {
  background: radial-gradient(circle at 30% 25%, rgba(255, 157, 102, 0.93), rgba(87, 17, 12, 0.92));
  animation: magmaPulse 2.8s ease-in-out infinite;
}

.oracle-tile.t-w {
  background:
    radial-gradient(circle at 42% 24%, rgba(110, 210, 255, 0.82), rgba(9, 38, 70, 0.95)),
    linear-gradient(180deg, rgba(13, 58, 88, 0.9), rgba(4, 18, 38, 0.95));
  animation: waterDrift 2.5s linear infinite;
}

.oracle-tile.t-b {
  background:
    repeating-linear-gradient(45deg, rgba(89, 95, 108, 0.8), rgba(89, 95, 108, 0.8) 6px, rgba(57, 62, 74, 0.9) 6px, rgba(57, 62, 74, 0.9) 12px),
    #111722;
}

.oracle-tile.blackout {
  background: linear-gradient(145deg, #020407, #040913) !important;
}

.oracle-tile.blackout .tile-risk,
.oracle-tile.blackout .tile-entropy,
.oracle-tile.blackout .tile-scan,
.oracle-tile.blackout .tile-path {
  opacity: 0 !important;
}

.oracle-agent {
  position: absolute;
  width: 28px;
  height: 28px;
  margin-left: -14px;
  margin-top: -14px;
  border-radius: 999px;
  pointer-events: none;
  transform: rotate(var(--rot, 0deg));
}

.oracle-agent-core {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: radial-gradient(circle at 35% 35%, rgba(247, 255, 252, 0.95), rgba(70, 255, 214, 0.82) 35%, rgba(8, 119, 128, 0.9));
  box-shadow: 0 0 18px rgba(56, 255, 214, 0.72), inset 0 0 12px rgba(227, 255, 248, 0.4);
  animation: agentPulse 1.3s ease-in-out infinite;
}

.oracle-agent-ring {
  position: absolute;
  inset: -9px;
  border: 1px solid rgba(154, 251, 255, 0.78);
  border-radius: 999px;
  opacity: 0;
}

.oracle-agent.scanning .oracle-agent-ring {
  animation: scanPulse 0.9s ease-out infinite;
}

.world-footer {
  margin-top: 0.4rem;
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.13em;
  color: rgba(187, 243, 255, 0.74);
}

.brain-shell {
  border: 1px solid rgba(108, 231, 255, 0.22);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(4, 14, 27, 0.9), rgba(3, 9, 18, 0.95));
  padding: 0.55rem;
}

.brain-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.38rem;
}

.brain-stat {
  border: 1px solid rgba(98, 222, 245, 0.18);
  border-radius: 9px;
  background: rgba(4, 16, 29, 0.8);
  padding: 0.4rem;
}

.brain-stat p {
  margin: 0;
  font-size: 0.54rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: rgba(178, 244, 255, 0.7);
}

.brain-stat strong {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.95rem;
  font-family: "Orbitron", "Segoe UI", sans-serif;
}

.brain-card {
  margin-top: 0.5rem;
  border: 1px solid rgba(101, 225, 247, 0.18);
  border-radius: 10px;
  background: rgba(2, 11, 22, 0.78);
  padding: 0.5rem;
}

.brain-card h4 {
  margin: 0;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: rgba(185, 248, 255, 0.86);
  font-family: "Orbitron", "Segoe UI", sans-serif;
}

.brain-heatmap {
  margin-top: 0.36rem;
  display: grid;
  gap: 2px;
}

.brain-heat {
  height: 10px;
  border-radius: 2px;
}

.brain-bars {
  margin-top: 0.34rem;
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
}

.brain-bar-row {
  display: grid;
  grid-template-columns: 78px 1fr 44px;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.56rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.brain-bar {
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(125, 237, 255, 0.14);
}

.brain-bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #68f0ff, #a2ffc3);
}

.brain-policy {
  margin-top: 0.44rem;
  height: 9px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(108, 232, 255, 0.18);
}

.brain-policy-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #72f7ff, #9bffc7, #d6ff95);
}

.brain-split {
  margin-top: 0.35rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.56rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(181, 245, 255, 0.76);
}

.feed-shell {
  margin-top: 0.7rem;
  border: 1px solid rgba(115, 234, 255, 0.22);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(3, 12, 24, 0.88), rgba(2, 7, 15, 0.94));
  min-height: 210px;
  max-height: 240px;
  overflow: hidden;
  position: relative;
}

.feed-shell::after {
  content: "";
  position: absolute;
  inset: -60% 0 auto 0;
  height: 120%;
  background: linear-gradient(180deg, transparent, rgba(108, 248, 255, 0.07), transparent);
  animation: radarSweep 4.2s linear infinite;
  pointer-events: none;
}

.feed-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.65rem 0.34rem;
}

.feed-title {
  margin: 0;
  font-size: 0.71rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-family: "Orbitron", "Segoe UI", sans-serif;
}

.feed-sub {
  margin: 0.1rem 0 0;
  font-size: 0.57rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(176, 244, 255, 0.7);
}

.feed-scroll {
  overflow-y: auto;
  max-height: 176px;
  padding: 0 0.6rem 0.55rem;
}

.feed-item {
  border: 1px solid rgba(102, 224, 246, 0.15);
  border-radius: 9px;
  background: rgba(4, 15, 28, 0.76);
  padding: 0.35rem 0.42rem;
  margin-top: 0.34rem;
}

.feed-item:first-child {
  animation: entryFlash 0.5s ease;
}

.feed-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(174, 239, 255, 0.67);
}

.feed-msg {
  margin: 0.12rem 0 0;
  font-size: 0.66rem;
  line-height: 1.35;
  color: rgba(214, 251, 255, 0.9);
}

.level-info { border-color: rgba(100, 227, 249, 0.22); }
.level-warn { border-color: rgba(255, 205, 117, 0.5); }
.level-critical { border-color: rgba(255, 127, 127, 0.65); }
.level-success { border-color: rgba(136, 255, 186, 0.58); }

.status-shell {
  border: 1px solid rgba(110, 231, 253, 0.2);
  border-radius: 10px;
  background: rgba(4, 14, 27, 0.75);
  padding: 0.5rem;
}

.status-line {
  margin: 0;
  display: flex;
  justify-content: space-between;
  font-size: 0.58rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(185, 245, 255, 0.81);
}

.status-line + .status-line {
  margin-top: 0.22rem;
}

#oracle-command .gr-button {
  border: 1px solid rgba(103, 229, 251, 0.35) !important;
  border-radius: 9px !important;
  background: rgba(8, 22, 35, 0.87) !important;
  color: #dcfdff !important;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-family: "Orbitron", "Segoe UI", sans-serif;
  font-size: 0.62rem !important;
  min-height: 38px !important;
}

#oracle-command .gr-button:hover {
  border-color: rgba(158, 251, 255, 0.8) !important;
  box-shadow: 0 0 20px rgba(95, 245, 255, 0.2);
}

#oracle-command .gr-form,
#oracle-command .gr-box,
#oracle-command .gr-group {
  border-color: rgba(110, 231, 253, 0.22) !important;
  background: rgba(4, 12, 24, 0.65) !important;
  border-radius: 10px !important;
}

#oracle-command label,
#oracle-command .gradio-dropdown label,
#oracle-command .gradio-number label,
#oracle-command .gradio-slider label,
#oracle-command .gradio-textbox label,
#oracle-command .gradio-checkbox label {
  text-transform: uppercase !important;
  letter-spacing: 0.13em !important;
  font-size: 0.57rem !important;
  color: rgba(173, 244, 255, 0.86) !important;
}

#oracle-command input,
#oracle-command textarea,
#oracle-command select {
  border-radius: 8px !important;
  border: 1px solid rgba(111, 232, 253, 0.3) !important;
  background: rgba(4, 12, 23, 0.86) !important;
  color: #ddfbff !important;
}

@media (max-width: 1360px) {
  .world-stage {
    min-height: 460px;
  }
}

@media (max-width: 1140px) {
  #oracle-main-grid {
    flex-direction: column;
  }
  .world-stage {
    min-height: 420px;
  }
}

@keyframes bootFadeOut {
  0%, 72% { opacity: 1; visibility: visible; }
  100% { opacity: 0; visibility: hidden; }
}

@keyframes bootLineIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes bootLoad {
  from { width: 0%; }
  to { width: 100%; }
}

@keyframes radarSweep {
  from { transform: translateY(-100%); }
  to { transform: translateY(100%); }
}

@keyframes magmaPulse {
  0%, 100% { filter: brightness(0.94) saturate(1); }
  50% { filter: brightness(1.14) saturate(1.2); }
}

@keyframes waterDrift {
  0% { background-position: 0 0; }
  100% { background-position: 34px 18px; }
}

@keyframes agentPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.06); }
}

@keyframes scanPulse {
  from { transform: scale(0.25); opacity: 0.9; }
  to { transform: scale(1.25); opacity: 0; }
}

@keyframes entryFlash {
  from { filter: brightness(1.4); }
  to { filter: brightness(1); }
}
"""


def make_event(code: str, level: str, message: str) -> Dict[str, str]:
    return {
        'id': f'{code}-{uuid.uuid4().hex[:8]}',
        'code': code,
        'level': level,
        'message': message,
        'time': datetime.utcnow().strftime('%H:%M:%S UTC'),
    }


def push_event(store: Dict[str, Any], code: str, level: str, message: str) -> None:
    feed = store.setdefault('feed', [])
    feed.insert(0, make_event(code, level, message))
    store['feed'] = feed[:100]


def build_store() -> Dict[str, Any]:
    return {
        'session': None,
        'snapshots': [],
        'feed': [
            make_event('SYS_READY', 'success', 'ORACLE GRID online. Configure mission profile and deploy tactical unit.'),
            make_event('BOOT_OK', 'info', 'Neural command bus stable. Awaiting mission envelope.'),
        ],
        'difficulty': 'tactical',
        'mission_mode': 'survival',
        'agent_type': 'bayesian',
        'camera_zoom': 1.0,
        'follow_mode': True,
        'view_index': 0,
    }


def as_int(value: Any, fallback: int) -> int:
    try:
        if value is None:
            return fallback
        return int(value)
    except Exception:
        return fallback


def as_float(value: Any, fallback: float) -> float:
    try:
        if value is None:
            return fallback
        return float(value)
    except Exception:
        return fallback


def normalize_agent(value: str) -> str:
    mapping = {
        'Deterministic': 'deterministic',
        'Bayesian': 'bayesian',
        'RL': 'rl',
        'deterministic': 'deterministic',
        'bayesian': 'bayesian',
        'rl': 'rl',
    }
    return mapping.get(value, 'bayesian')


def mode_label(mode: str) -> str:
    for key, label in MISSION_MODES:
        if key == mode:
            return label
    return mode


def grid_size_for(difficulty: str, mission_mode: str) -> int:
    base = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS['tactical'])['grid_size']
    if mission_mode == 'infinite-terrain':
        return max(base, 15)
    if mission_mode == 'adaptive-nightmare':
        return min(17, base + 2)
    if mission_mode == 'recon':
        return max(7, base - 1)
    if mission_mode == 'rl-arena':
        return max(base, 11)
    return base


def runtime_sync(session: SimulationSession) -> None:
    session.env.grid = session.grid
    agent = session.agent
    if hasattr(agent, 'grid'):
        agent.grid = session.grid
    if hasattr(agent, 'planner') and hasattr(agent.planner, 'grid'):
        agent.planner.grid = session.grid
    if hasattr(agent, 'mcts') and hasattr(agent.mcts, 'grid'):
        agent.mcts.grid = session.grid
    if hasattr(agent, 'path'):
        agent.path = None
    if hasattr(agent, 'current_path'):
        agent.current_path = None
    if hasattr(agent, 'plan_idx'):
        agent.plan_idx = 0


def inject_dynamic_hazards(store: Dict[str, Any]) -> int:
    session: SimulationSession = store['session']
    difficulty = store.get('difficulty', 'tactical')
    mission_mode = store.get('mission_mode', 'survival')

    preset = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS['tactical'])
    drift = max(0.0, preset['hazard_drift'] + MISSION_DRIFT.get(mission_mode, 0.0))

    if drift <= 0:
        return 0

    rows, cols = session.grid_rows, session.grid_cols
    protected = {tuple(session.env.start), tuple(session.env.goal), tuple(session.env.agent_pos)}
    changes = 0
    attempts = max(1, int(rows * cols * drift))

    for _ in range(attempts):
        if random.random() > drift:
            continue

        r = random.randrange(rows)
        c = random.randrange(cols)
        if (r, c) in protected:
            continue

        current = session.grid[r][c]
        if current in {'S', 'G'}:
            continue

        if mission_mode == 'hazard-sweep' and current in {'V', 'W'} and random.random() < 0.38:
            nxt = 'L'
        else:
            hazard_bias = preset['hazard_bias'] + (0.06 if mission_mode == 'adaptive-nightmare' else 0.0)
            roll = random.random()
            if roll < hazard_bias:
                nxt = random.choice(['V', 'W'])
            elif roll < hazard_bias + 0.21:
                nxt = 'B'
            else:
                nxt = 'L'

        if nxt != current:
            session.grid[r][c] = nxt
            changes += 1

    if changes:
        runtime_sync(session)
    return changes


def _noise_scalar(r: int, c: int, step: int) -> float:
    base = math.sin((r + 1) * 12.9898 + (c + 1) * 78.233 + (step + 1) * 37.719) * 43758.5453
    fraction = base - math.floor(base)
    return fraction * 2 - 1


def select_snapshot(store: Dict[str, Any], requested_index: Optional[int]) -> Tuple[Optional[Dict[str, Any]], int, int]:
    snapshots: List[Dict[str, Any]] = store.get('snapshots', [])
    if not snapshots:
        return None, 0, 0

    max_index = len(snapshots) - 1
    if requested_index is None:
        index = as_int(store.get('view_index', max_index), max_index)
    else:
        index = as_int(requested_index, max_index)

    index = max(0, min(index, max_index))
    store['view_index'] = index
    return snapshots[index], index, max_index


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def render_world(snapshot: Optional[Dict[str, Any]], store: Dict[str, Any], view_index: int, max_index: int) -> str:
    if snapshot is None:
        return """
<section class="oracle-world-shell">
  <div class="world-header">
    <div>
      <p class="world-h1">Live Grid World</p>
      <p class="world-h2">Deploy mission profile to activate tactical renderer.</p>
    </div>
  </div>
  <div class="world-stage"></div>
</section>
"""

    mission_mode = store.get('mission_mode', 'survival')
    difficulty = store.get('difficulty', 'tactical')
    zoom = clamp(as_float(store.get('camera_zoom', 1.0), 1.0), 0.72, 1.9)
    follow_mode = bool(store.get('follow_mode', True))

    grid = snapshot['grid']
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    agent_r, agent_c = snapshot['agent_pos']
    done = bool(snapshot.get('done', False))
    step_count = len(snapshot.get('history', []))
    last_action = snapshot.get('last_action') or 'none'
    lives = snapshot.get('lives', 0)
    score = snapshot['history'][-1]['score'] if snapshot.get('history') else snapshot.get('turns', 0)
    risk_map = snapshot.get('risk_map') or [[0.0 for _ in range(cols)] for _ in range(rows)]
    entropy_map = snapshot.get('entropy_map') or [[0.0 for _ in range(cols)] for _ in range(rows)]
    scan_map = snapshot.get('scan_heatmap') or [[0 for _ in range(cols)] for _ in range(rows)]

    path_preview = snapshot.get('cognition', {}).get('path_preview') or []
    path_set = {f'{cell[0]}:{cell[1]}' for cell in path_preview if isinstance(cell, (list, tuple)) and len(cell) == 2}

    live_status = 'Replay' if view_index < max_index else 'Live'
    action_rotation = 0
    if str(last_action).endswith('_n'):
        action_rotation = -90
    elif str(last_action).endswith('_s'):
        action_rotation = 90
    elif str(last_action).endswith('_w'):
        action_rotation = 180

    origin_x = ((agent_c + 0.5) / cols * 100.0) if cols else 50.0
    origin_y = ((agent_r + 0.5) / rows * 100.0) if rows else 50.0
    camera_origin = f'{origin_x:.2f}% {origin_y:.2f}%' if follow_mode else '50% 50%'

    tile_markup: List[str] = []
    for r in range(rows):
        for c in range(cols):
            tile = grid[r][c]
            risk_raw = float(risk_map[r][c]) if risk_map and risk_map[r] else 0.0
            entropy_raw = float(entropy_map[r][c]) if entropy_map and entropy_map[r] else 0.0
            scan_count = int(scan_map[r][c]) if scan_map and scan_map[r] else 0

            risk = risk_raw
            if mission_mode == 'sensor-failure':
                risk = clamp(risk_raw + _noise_scalar(r, c, step_count) * 0.16, 0.0, 1.0)
            elif mission_mode == 'adaptive-nightmare':
                risk = clamp(risk_raw + 0.08, 0.0, 1.0)

            entropy = clamp(entropy_raw / 2.2, 0.0, 1.0)
            hidden = mission_mode == 'blackout' and scan_count == 0 and max(abs(r - agent_r), abs(c - agent_c)) > 2
            tile_class = f'oracle-tile t-{tile.lower()}'
            if hidden:
                tile_class += ' blackout'

            parts: List[str] = []
            parts.append(f'<div class="{tile_class}" style="--risk:{risk:.3f};--entropy:{entropy:.3f};" title="{html.escape(TILE_LABELS.get(tile, tile))}">')
            parts.append('<span class="tile-risk"></span>')
            parts.append('<span class="tile-entropy"></span>')
            if scan_count > 0 and not hidden:
                parts.append(f'<span class="tile-scan">{scan_count}</span>')
            if f'{r}:{c}' in path_set and not hidden:
                parts.append('<span class="tile-path"></span>')
            parts.append('</div>')
            tile_markup.append(''.join(parts))

    agent_left = ((agent_c + 0.5) / cols) * 100.0 if cols else 0.0
    agent_top = ((agent_r + 0.5) / rows) * 100.0 if rows else 0.0
    scanning = ' scanning' if last_action == 'scan' else ''

    mode_tag = mode_label(mission_mode).split('//')[0].strip()
    phase = 'Mission Complete' if done else 'Engaged'
    phase_class = 'CRITICAL' if done and tuple(snapshot['agent_pos']) != tuple(snapshot['goal']) else ('SUCCESS' if done else 'LIVE')

    return f"""
<section class="oracle-world-shell">
  <div class="world-header">
    <div>
      <p class="world-h1">Live Grid World</p>
      <p class="world-h2">Terrain dynamics + hazard confidence + path forecast</p>
    </div>
    <div class="world-badges">
      <span class="world-badge">{live_status} View</span>
      <span class="world-badge">{mode_tag}</span>
      <span class="world-badge">{difficulty.upper()}</span>
      <span class="world-badge">{phase} / {phase_class}</span>
    </div>
  </div>
  <div class="world-stage">
    <div class="world-camera" style="transform: scale({zoom:.3f}); transform-origin: {camera_origin};">
      <div class="oracle-grid" style="grid-template-columns: repeat({cols}, minmax(0, 1fr));">
        {''.join(tile_markup)}
      </div>
      <div class="oracle-agent{scanning}" style="left: {agent_left:.3f}%; top: {agent_top:.3f}%; --rot: {action_rotation}deg;">
        <span class="oracle-agent-core"></span>
        <span class="oracle-agent-ring"></span>
      </div>
    </div>
  </div>
  <div class="world-footer">
    <span>STEP {step_count} / LIVES {lives} / ACTION {html.escape(str(last_action).upper())}</span>
    <span>TURNS {snapshot.get('turns', 0)} / SCORE {float(score):.2f}</span>
  </div>
</section>
"""


def render_brain(snapshot: Optional[Dict[str, Any]], store: Dict[str, Any]) -> str:
    if snapshot is None:
        return """
<section class="brain-shell">
  <p class="oracle-panel-title">AI Brain</p>
  <p class="oracle-panel-subtitle">Deploy mission to stream cognition telemetry.</p>
</section>
"""

    grid = snapshot['grid']
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    agent_r, agent_c = snapshot['agent_pos']

    risk_map = snapshot.get('risk_map') or [[0.0 for _ in range(cols)] for _ in range(rows)]
    entropy_map = snapshot.get('entropy_map') or [[0.0 for _ in range(cols)] for _ in range(rows)]
    confidence_map = snapshot.get('confidence_map') or [[0.0 for _ in range(cols)] for _ in range(rows)]
    cognition = snapshot.get('cognition') or {}

    local_risk = float(risk_map[agent_r][agent_c]) if rows and cols else 0.0
    local_entropy = float(entropy_map[agent_r][agent_c]) if rows and cols else 0.0
    local_confidence = float(confidence_map[agent_r][agent_c]) if rows and cols else 0.0

    flatten_risk = [val for row in risk_map for val in row] if risk_map else [0.0]
    flatten_entropy = [val for row in entropy_map for val in row] if entropy_map else [0.0]
    avg_risk = sum(flatten_risk) / max(1, len(flatten_risk))
    avg_entropy = sum(flatten_entropy) / max(1, len(flatten_entropy))

    action_values = ((cognition.get('last_mcts_stats') or {}).get('action_values') or {})
    if not action_values and isinstance(cognition.get('last_decision'), dict):
        q_values = cognition['last_decision'].get('q_values')
        if isinstance(q_values, dict):
            action_values = q_values

    ranked_actions = sorted(
        [(str(action), float(value)) for action, value in action_values.items()],
        key=lambda item: item[1],
        reverse=True,
    )[:6]

    top_val = ranked_actions[0][1] if ranked_actions else 0.0
    second_val = ranked_actions[1][1] if len(ranked_actions) > 1 else top_val - 0.4
    confidence = clamp((top_val - second_val + 1.0) / 2.0, 0.05, 1.0)

    heat_cells: List[str] = []
    for r in range(rows):
        for c in range(cols):
            risk = float(risk_map[r][c])
            entropy = float(entropy_map[r][c])
            intensity = clamp((risk + entropy / 2.2) / 1.8, 0.0, 1.0)
            hue = 192 - intensity * 168
            lightness = 20 + intensity * 38
            highlight = 'outline:1px solid rgba(214,252,255,0.95);' if (r, c) == (agent_r, agent_c) else ''
            heat_cells.append(f'<div class="brain-heat" style="background:hsl({hue:.1f}deg 85% {lightness:.1f}%);{highlight}"></div>')

    fan_nodes: List[str] = []
    for idx, (action, value) in enumerate(ranked_actions):
        spread = idx / max(1, len(ranked_actions) - 1) if ranked_actions else 0.5
        x = 38 + spread * 284
        normalized = clamp((value + 12.0) / 24.0, 0.0, 1.0)
        radius = 9 + normalized * 12
        y = 130
        label = action.replace('walk_', '').replace('jump_', 'J').upper()
        stroke = 1.4 + normalized * 2.5
        fan_nodes.append(
            f'<line x1="180" y1="38" x2="{x:.2f}" y2="{y - 16:.2f}" stroke="rgba(97,213,255,0.42)" stroke-width="{stroke:.2f}" />'
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="hsla({166 - normalized * 96:.1f}, 92%, 58%, 0.86)" />'
            f'<text x="{x:.2f}" y="{y + 3:.2f}" text-anchor="middle" font-size="8" font-weight="700" fill="#04111a">{html.escape(label)}</text>'
        )

    bars: List[str] = []
    min_val = min([value for _, value in ranked_actions], default=0.0)
    max_val = max([value for _, value in ranked_actions], default=1.0)
    spread = max(0.001, max_val - min_val)
    for action, value in ranked_actions:
        width = clamp((value - min_val) / spread, 0.05, 1.0)
        bars.append(
            '<div class="brain-bar-row">'
            f'<span>{html.escape(action.upper())}</span>'
            f'<div class="brain-bar"><div class="brain-bar-fill" style="width:{width * 100:.1f}%"></div></div>'
            f'<span>{value:.2f}</span>'
            '</div>'
        )

    decision_mode = ''
    if isinstance(cognition.get('last_decision'), dict):
        decision_mode = str(cognition['last_decision'].get('mode', ''))

    return f"""
<section class="brain-shell">
  <p class="oracle-panel-title">AI Brain</p>
  <p class="oracle-panel-subtitle">Belief probabilities, entropy pressure, rollout arbitration.</p>

  <div class="brain-grid">
    <div class="brain-stat"><p>Local Risk</p><strong>{local_risk * 100:.0f}%</strong></div>
    <div class="brain-stat"><p>Local Entropy</p><strong>{local_entropy:.2f}</strong></div>
    <div class="brain-stat"><p>Certainty</p><strong>{local_confidence * 100:.0f}%</strong></div>
    <div class="brain-stat"><p>Avg Grid Risk</p><strong>{avg_risk * 100:.0f}%</strong></div>
  </div>

  <div class="brain-card">
    <h4>Belief Heatmap</h4>
    <div class="brain-heatmap" style="grid-template-columns: repeat({cols}, minmax(0, 1fr));">
      {''.join(heat_cells)}
    </div>
  </div>

  <div class="brain-card">
    <h4>MCTS / Policy Fanout</h4>
    <svg viewBox="0 0 360 170" style="width:100%;height:170px;border-radius:8px;background:#031120;">
      <circle cx="180" cy="30" r="12" fill="rgba(70,236,255,0.9)" />
      {''.join(fan_nodes)}
    </svg>
    <div class="brain-bars">{''.join(bars) if bars else '<p style="margin:0.3rem 0 0;font-size:0.65rem;color:#b4f5ff;">Awaiting rollout values...</p>'}</div>
    <div class="brain-policy"><div class="brain-policy-fill" style="width:{confidence * 100:.1f}%"></div></div>
    <div class="brain-split">
      <span>Exploration {(100 - confidence * 100):.0f}%</span>
      <span>Exploitation {(confidence * 100):.0f}%</span>
    </div>
    <div class="brain-split">
      <span>Decision Mode {html.escape(decision_mode.upper() or 'N/A')}</span>
      <span>Entropy Grid {avg_entropy:.2f}</span>
    </div>
  </div>
</section>
"""


def render_feed(store: Dict[str, Any]) -> str:
    feed = store.get('feed') or []
    items: List[str] = []
    for event in feed[:80]:
        level = event.get('level', 'info')
        code = html.escape(str(event.get('code', 'EVENT')))
        message = html.escape(str(event.get('message', '')))
        timestamp = html.escape(str(event.get('time', '')))
        items.append(
            f'<article class="feed-item level-{level}">'
            f'<div class="feed-meta"><span>{code}</span><span>{timestamp}</span></div>'
            f'<p class="feed-msg">{message}</p>'
            '</article>'
        )

    return f"""
<section class="feed-shell">
  <div class="feed-head">
    <div>
      <p class="feed-title">Mission Feed</p>
      <p class="feed-sub">Sensor anomalies, policy shifts, and tactical events.</p>
    </div>
  </div>
  <div class="feed-scroll">
    {''.join(items)}
  </div>
</section>
"""


def render_status(snapshot: Optional[Dict[str, Any]], store: Dict[str, Any]) -> str:
    if snapshot is None:
        return """
<section class="status-shell">
  <p class="status-line"><span>System</span><span>Awaiting Deployment</span></p>
  <p class="status-line"><span>Mission</span><span>Not Initialized</span></p>
  <p class="status-line"><span>Tip</span><span>Deploy to begin tactical loop</span></p>
</section>
"""

    history = snapshot.get('history') or []
    last = history[-1] if history else None
    status = 'COMPLETE' if snapshot.get('done') else 'ACTIVE'
    score = f"{float(last.get('score', 0.0)):.2f}" if last else f"{float(snapshot.get('turns', 0.0)):.2f}"
    replay = f"{store.get('view_index', 0) + 1}/{max(1, len(store.get('snapshots', [])))}"

    return f"""
<section class="status-shell">
  <p class="status-line"><span>Session</span><span>{html.escape(str(snapshot['session']['session_id']))[:10]}...</span></p>
  <p class="status-line"><span>Agent</span><span>{html.escape(str(snapshot['session']['agent_type']).upper())}</span></p>
  <p class="status-line"><span>Mission</span><span>{html.escape(str(snapshot['session']['mission_mode']).upper())}</span></p>
  <p class="status-line"><span>State</span><span>{status}</span></p>
  <p class="status-line"><span>Position</span><span>{snapshot['agent_pos'][0]},{snapshot['agent_pos'][1]}</span></p>
  <p class="status-line"><span>Replay</span><span>{replay}</span></p>
  <p class="status-line"><span>Score</span><span>{score}</span></p>
</section>
"""


def make_step_event(snapshot: Dict[str, Any]) -> Tuple[str, str, str]:
    history = snapshot.get('history') or []
    if not history:
        return 'TELEMETRY', 'info', 'Awaiting first action.'

    latest = history[-1]
    info = latest.get('info', {})
    step = latest.get('step', 0)
    action = str(latest.get('action', '')).upper()

    if info.get('scanned'):
        return 'SENSOR_ANOMALY', 'info', f'Sensor sweep executed at cell {latest["next_pos"]}. Entropy sample refreshed.'
    if info.get('took_damage'):
        return 'HAZARD_CONFIRMED', 'critical', f'Hazard impact on step {step}. Lives now {latest.get("lives", 0)}.'
    if snapshot.get('done') and tuple(snapshot['agent_pos']) == tuple(snapshot['goal']):
        return 'MISSION_SUCCESS', 'success', f'Extraction secured in {step} turns. Tactical score {latest.get("score", 0):.2f}.'
    if snapshot.get('done'):
        return 'UNIT_LOST', 'critical', f'Simulation ended at step {step}. Unit exhausted.'
    return 'PATH_RECOMPUTED', 'info', f'{action} executed. Reward {latest.get("reward", 0):.1f}.'


def compose_output(store: Dict[str, Any], requested_index: Optional[int] = None):
    snapshot, index, max_index = select_snapshot(store, requested_index)
    world = render_world(snapshot, store, index, max_index)
    brain = render_brain(snapshot, store)
    feed = render_feed(store)
    status = render_status(snapshot, store)

    size = 14
    if snapshot:
        size = int(snapshot['session']['grid_rows']) - 1
    size = max(0, size)

    replay_update = gr.update(minimum=0, maximum=max_index, value=index)
    row_value = as_int(store.get('edit_row', 0), 0)
    col_value = as_int(store.get('edit_col', 0), 0)
    row_update = gr.update(minimum=0, maximum=size, value=max(0, min(size, row_value)))
    col_update = gr.update(minimum=0, maximum=size, value=max(0, min(size, col_value)))
    return store, world, brain, feed, status, replay_update, row_update, col_update


def deploy_mission(
    store: Dict[str, Any],
    agent_choice: str,
    mission_mode: str,
    difficulty: str,
    seed: Any,
    use_mcts: bool,
    model_path: str,
    camera_zoom: float,
    follow_mode: bool,
):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)

    agent_type = normalize_agent(agent_choice)
    grid_size = grid_size_for(difficulty, mission_mode)
    seed_value = as_int(seed, random.randint(1, 2**31 - 1))

    session = SimulationSession(
        session_id=str(uuid.uuid4()),
        agent_type=agent_type,
        use_mcts=bool(use_mcts and agent_type == 'bayesian'),
        grid_rows=grid_size,
        grid_cols=grid_size,
        seed=seed_value,
        model_path=model_path or 'models/q_table.json',
        mission_mode=mission_mode,
        difficulty=difficulty,
    )

    snapshot = session.serialize_state()
    store['session'] = session
    store['snapshots'] = [snapshot]
    store['difficulty'] = difficulty
    store['mission_mode'] = mission_mode
    store['agent_type'] = agent_type
    store['view_index'] = 0
    store['edit_row'] = 0
    store['edit_col'] = 0

    store['feed'] = [
        make_event('DEPLOY', 'success', f'Mission deployed: {mode_label(mission_mode)}. Difficulty profile {difficulty.upper()}.'),
        make_event('GRID_SYNC', 'info', f'Grid {grid_size}x{grid_size} linked. Unit inserted at deployment cell.'),
        make_event('AI_CORE', 'info', f'Agent core online: {agent_type.upper()}{" + MCTS" if use_mcts and agent_type == "bayesian" else ""}.'),
    ]

    return compose_output(store, requested_index=0)


def step_mission(
    store: Dict[str, Any],
    action_override: str,
    requested_index: int,
    camera_zoom: float,
    follow_mode: bool,
):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)

    session: Optional[SimulationSession] = store.get('session')
    if session is None:
        push_event(store, 'NO_SESSION', 'warn', 'No active mission session. Deploy before issuing tactical steps.')
        return compose_output(store, requested_index=requested_index)

    if session.done:
        push_event(store, 'MISSION_LOCK', 'warn', 'Mission already concluded. Reset or deploy a new profile.')
        return compose_output(store, requested_index=requested_index)

    drift_changes = inject_dynamic_hazards(store)
    action = None if action_override == 'AUTO' else action_override

    snapshot = session.step(action=action)
    store['snapshots'].append(snapshot)
    store['view_index'] = len(store['snapshots']) - 1

    code, level, msg = make_step_event(snapshot)
    push_event(store, code, level, msg)

    if drift_changes > 0:
        push_event(store, 'TERRAIN_SHIFT', 'warn', f'Dynamic terrain mutation detected: {drift_changes} tiles altered.')

    cognition = snapshot.get('cognition') or {}
    mcts_stats = (cognition.get('last_mcts_stats') or {})
    visits = mcts_stats.get('visits')
    if isinstance(visits, (int, float)) and visits > 0:
        push_event(store, 'MCTS_EXPANSION', 'info', f'MCTS expansion pass complete. Visit count {int(visits)}.')

    return compose_output(store, requested_index=store['view_index'])


def burst_mission(
    store: Dict[str, Any],
    action_override: str,
    burst_steps: int,
    requested_index: int,
    camera_zoom: float,
    follow_mode: bool,
):
    store = store or build_store()
    total_steps = max(1, min(48, as_int(burst_steps, 8)))
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)

    session: Optional[SimulationSession] = store.get('session')
    if session is None:
        push_event(store, 'NO_SESSION', 'warn', 'No mission runtime. Deploy before burst execution.')
        return compose_output(store, requested_index=requested_index)

    executed = 0
    for _ in range(total_steps):
        if session.done:
            break
        drift_changes = inject_dynamic_hazards(store)
        action = None if action_override == 'AUTO' else action_override
        snapshot = session.step(action=action)
        store['snapshots'].append(snapshot)
        executed += 1
        code, level, msg = make_step_event(snapshot)
        push_event(store, code, level, msg)
        if drift_changes > 0:
            push_event(store, 'TERRAIN_SHIFT', 'warn', f'Live terrain drift mutated {drift_changes} tiles.')

    if executed == 0:
        push_event(store, 'BURST_IDLE', 'warn', 'Burst request ended immediately because mission is complete.')
    else:
        push_event(store, 'BURST_EXEC', 'success', f'Autonomous burst executed {executed} tactical ticks.')

    store['view_index'] = max(0, len(store.get('snapshots', [])) - 1)
    return compose_output(store, requested_index=store['view_index'])


def reset_mission(
    store: Dict[str, Any],
    requested_index: int,
    camera_zoom: float,
    follow_mode: bool,
):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)

    session: Optional[SimulationSession] = store.get('session')
    if session is None:
        push_event(store, 'NO_SESSION', 'warn', 'No active mission to reset.')
        return compose_output(store, requested_index=requested_index)

    session.reset()
    snapshot = session.serialize_state()
    store['snapshots'] = [snapshot]
    store['view_index'] = 0
    push_event(store, 'RESET', 'info', 'Mission clocks reset. Terrain restored to deployment configuration.')
    return compose_output(store, requested_index=0)


def apply_tile_edit(
    store: Dict[str, Any],
    brush: str,
    row: int,
    col: int,
    requested_index: int,
    camera_zoom: float,
    follow_mode: bool,
):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)

    session: Optional[SimulationSession] = store.get('session')
    if session is None:
        push_event(store, 'EDIT_BLOCKED', 'warn', 'Deploy mission before terrain editing.')
        return compose_output(store, requested_index=requested_index)

    r = as_int(row, 0)
    c = as_int(col, 0)
    store['edit_row'] = r
    store['edit_col'] = c
    if not (0 <= r < session.grid_rows and 0 <= c < session.grid_cols):
        push_event(store, 'EDIT_RANGE', 'warn', 'Tile edit out of bounds.')
        return compose_output(store, requested_index=requested_index)

    if (r, c) == session.env.start or (r, c) == session.env.goal:
        push_event(store, 'EDIT_LOCK', 'warn', 'Deployment and extraction cells are protected.')
        return compose_output(store, requested_index=requested_index)

    brush = (brush or 'L').upper()
    if brush not in {'L', 'V', 'W', 'B'}:
        brush = 'L'

    old = session.grid[r][c]
    session.grid[r][c] = brush
    runtime_sync(session)
    snapshot = session.serialize_state()
    store['snapshots'].append(snapshot)
    store['view_index'] = len(store['snapshots']) - 1
    push_event(store, 'TERRAIN_EDIT', 'success', f'Tile ({r},{c}) changed {old} -> {brush}.')
    return compose_output(store, requested_index=store['view_index'])


def relocate_goal(
    store: Dict[str, Any],
    row: int,
    col: int,
    requested_index: int,
    camera_zoom: float,
    follow_mode: bool,
):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)

    session: Optional[SimulationSession] = store.get('session')
    if session is None:
        push_event(store, 'VECTOR_BLOCK', 'warn', 'No mission session. Deploy before moving extraction vector.')
        return compose_output(store, requested_index=requested_index)

    r = as_int(row, 0)
    c = as_int(col, 0)
    store['edit_row'] = r
    store['edit_col'] = c
    if not (0 <= r < session.grid_rows and 0 <= c < session.grid_cols):
        push_event(store, 'VECTOR_RANGE', 'warn', 'Extraction vector out of range.')
        return compose_output(store, requested_index=requested_index)
    if (r, c) == session.env.start:
        push_event(store, 'VECTOR_LOCK', 'warn', 'Extraction cannot overlap deployment cell.')
        return compose_output(store, requested_index=requested_index)

    old_goal = tuple(session.env.goal)
    if old_goal != session.env.start:
        session.grid[old_goal[0]][old_goal[1]] = 'L'
    session.grid[r][c] = 'G'
    session.env.goal = (r, c)
    runtime_sync(session)

    snapshot = session.serialize_state()
    store['snapshots'].append(snapshot)
    store['view_index'] = len(store['snapshots']) - 1
    push_event(store, 'VECTOR_SHIFT', 'warn', f'Extraction vector reassigned from {old_goal} to {(r, c)}.')
    return compose_output(store, requested_index=store['view_index'])


def probe_cell(
    store: Dict[str, Any],
    row: int,
    col: int,
    requested_index: int,
    camera_zoom: float,
    follow_mode: bool,
):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)

    snapshot, _, _ = select_snapshot(store, requested_index)
    if snapshot is None:
        push_event(store, 'PROBE_IDLE', 'warn', 'No active tactical world to probe.')
        return compose_output(store, requested_index=requested_index)

    r = as_int(row, 0)
    c = as_int(col, 0)
    store['edit_row'] = r
    store['edit_col'] = c
    rows = len(snapshot['grid'])
    cols = len(snapshot['grid'][0]) if rows else 0
    if not (0 <= r < rows and 0 <= c < cols):
        push_event(store, 'PROBE_RANGE', 'warn', 'Probe coordinates out of bounds.')
        return compose_output(store, requested_index=requested_index)

    tile = snapshot['grid'][r][c]
    risk_map = snapshot.get('risk_map') or [[0.0 for _ in range(cols)] for _ in range(rows)]
    entropy_map = snapshot.get('entropy_map') or [[0.0 for _ in range(cols)] for _ in range(rows)]
    risk = float(risk_map[r][c]) if risk_map else 0.0
    entropy = float(entropy_map[r][c]) if entropy_map else 0.0
    push_event(
        store,
        'SENSOR_PROBE',
        'info',
        f'Probe ({r},{c}) -> {TILE_LABELS.get(tile, tile)} | risk {risk * 100:.0f}% | entropy {entropy:.2f}.',
    )
    return compose_output(store, requested_index=requested_index)


def camera_update(store: Dict[str, Any], requested_index: int, camera_zoom: float, follow_mode: bool):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)
    return compose_output(store, requested_index=requested_index)


def replay_update(store: Dict[str, Any], requested_index: int, camera_zoom: float, follow_mode: bool):
    store = store or build_store()
    store['camera_zoom'] = clamp(as_float(camera_zoom, 1.0), 0.72, 1.9)
    store['follow_mode'] = bool(follow_mode)
    return compose_output(store, requested_index=requested_index)


def build_ui():
    with gr.Blocks(title='ORACLE // Autonomous Tactical Intelligence System', css=ORACLE_CSS, elem_id='oracle-hf-root') as demo:
        state = gr.State(build_store())

        gr.HTML(BOOT_SEQUENCE_HTML)
        gr.HTML(TITLE_SHELL_HTML)

        with gr.Row(elem_id='oracle-main-grid'):
            with gr.Column(scale=3, elem_id='oracle-command'):
                gr.HTML('<p class="oracle-panel-title">Command Terminal</p><p class="oracle-panel-subtitle">Configure mission envelope, deploy unit, and issue tactical controls.</p>')

                mission_mode = gr.Dropdown(
                    choices=[mode for mode, _ in MISSION_MODES],
                    value='survival',
                    label='Mission Mode',
                )
                difficulty = gr.Dropdown(
                    choices=list(DIFFICULTY_PRESETS.keys()),
                    value='tactical',
                    label='Difficulty Profile',
                )
                agent_choice = gr.Dropdown(choices=AGENT_OPTIONS, value='Bayesian', label='Agent Core')
                use_mcts = gr.Checkbox(value=True, label='Enable MCTS Augmentation')
                seed = gr.Number(value=42, precision=0, label='Random Seed')
                model_path = gr.Textbox(value='models/q_table.json', label='RL Model Path')
                action_override = gr.Dropdown(choices=ACTION_OVERRIDE, value='AUTO', label='Action Override')
                burst_steps = gr.Slider(minimum=1, maximum=48, value=8, step=1, label='Autonomy Burst Steps')

                with gr.Row():
                    deploy_btn = gr.Button('Deploy Mission', variant='primary')
                    step_btn = gr.Button('Step Once')
                with gr.Row():
                    burst_btn = gr.Button('Run Burst')
                    reset_btn = gr.Button('Reset Mission')

                gr.HTML('<p class="oracle-panel-title" style="margin-top:0.7rem;">World Editing</p><p class="oracle-panel-subtitle">Modify hazards, relocate extraction, and probe map telemetry.</p>')
                brush = gr.Dropdown(choices=['L', 'V', 'W', 'B'], value='V', label='Terrain Brush')
                edit_row = gr.Slider(minimum=0, maximum=14, step=1, value=0, label='Tile Row')
                edit_col = gr.Slider(minimum=0, maximum=14, step=1, value=0, label='Tile Col')

                with gr.Row():
                    apply_btn = gr.Button('Apply Brush')
                    goal_btn = gr.Button('Relocate Goal')
                with gr.Row():
                    probe_btn = gr.Button('Sensor Probe')

                gr.HTML('<p class="oracle-panel-title" style="margin-top:0.7rem;">Camera</p>')
                camera_zoom = gr.Slider(minimum=0.72, maximum=1.9, value=1.0, step=0.04, label='Cinematic Zoom')
                follow_mode = gr.Checkbox(value=True, label='Follow Agent Focus')
                status_html = gr.HTML(render_status(None, build_store()), elem_id='status-render')

            with gr.Column(scale=6, elem_id='oracle-world-col'):
                world_html = gr.HTML(render_world(None, build_store(), 0, 0), elem_id='world-render')
                replay_slider = gr.Slider(minimum=0, maximum=0, value=0, step=1, label='Replay Timeline (Rewind Episodes)')

            with gr.Column(scale=4, elem_id='oracle-brain-col'):
                brain_html = gr.HTML(render_brain(None, build_store()), elem_id='brain-render')

        feed_html = gr.HTML(render_feed(build_store()), elem_id='feed-render')

        outputs = [state, world_html, brain_html, feed_html, status_html, replay_slider, edit_row, edit_col]

        deploy_btn.click(
            fn=deploy_mission,
            inputs=[state, agent_choice, mission_mode, difficulty, seed, use_mcts, model_path, camera_zoom, follow_mode],
            outputs=outputs,
        )
        step_btn.click(
            fn=step_mission,
            inputs=[state, action_override, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        burst_btn.click(
            fn=burst_mission,
            inputs=[state, action_override, burst_steps, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        reset_btn.click(
            fn=reset_mission,
            inputs=[state, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        apply_btn.click(
            fn=apply_tile_edit,
            inputs=[state, brush, edit_row, edit_col, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        goal_btn.click(
            fn=relocate_goal,
            inputs=[state, edit_row, edit_col, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        probe_btn.click(
            fn=probe_cell,
            inputs=[state, edit_row, edit_col, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        replay_slider.change(
            fn=replay_update,
            inputs=[state, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        camera_zoom.change(
            fn=camera_update,
            inputs=[state, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )
        follow_mode.change(
            fn=camera_update,
            inputs=[state, replay_slider, camera_zoom, follow_mode],
            outputs=outputs,
        )

    return demo


if __name__ == '__main__':
    app = build_ui()
    app.launch(server_name='0.0.0.0', server_port=7860)
