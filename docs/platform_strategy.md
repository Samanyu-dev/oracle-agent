---
layout: default
title: Platform Strategy
---

# 🌌 Oracle Agent Platform Strategy

This document defines the ideal deployment and showcase strategy for Oracle Agent.
The core project remains a Python-based intelligence engine, while the public
experience is best delivered through a cinematic frontend and a reproducible
research playground.

## Primary Experience: Vercel

Oracle Agent is strongest when experienced as a **tactical simulation**, not just
as static code. The primary public face should be a polished Vercel site built
with:

- **Next.js 15** for fast page transitions and reactive UI
- **Tailwind CSS** for modern glassmorphism and neon-style layouts
- **Framer Motion** for cinematic animations and scrolling effects
- **Three.js + React Three Fiber** for grid rendering, particle effects, and
  agent movement
- **D3.js** for interactive charts, heatmaps, and mid-flight analytics

### Showcase Features

- Hero section with animated neural grid and pulse scan effects
- Live grid-world simulation with fog-of-war and hazard visualization
- Real-time path planning overlays and agent decision highlights
- Bayesian belief heatmaps and entropy maps
- MCTS rollout exploration and future branch animation
- RL training theater with curve evolution and policy emergence
- Benchmark command center with recruiter-friendly metrics

## Secondary Research Playground: Hugging Face

A Hugging Face Space should support the research audience by delivering:

- reproducible experiment runners
- benchmark dashboards and metric tables
- configurable parameters for sensor noise, hazard density, and agent type
- notebooks for algorithm walkthroughs and math explanations
- downloadable model/config artifacts and benchmark data

This space is ideal for **academic credibility**, publication-style demos, and
research sharing.

## Why Vercel Is the Best Main Platform

Oracle’s value is in the experience, not just the inference output. Vercel
supports the type of cinematic, interactive UI that turns this project into a
recruiter magnet:

- real-time visual simulation
- game-like interactivity
- premium product positioning
- shareable landing experience

## Product Positioning

Brand Oracle Agent as one of the following:

- **Adaptive Autonomous Planning Engine**
- **Interactive AI Navigation Laboratory**
- **Autonomous Survival Intelligence System**
- **Tactical AI Command Simulator**

The emphasis should be on:

- survival mechanics
- uncertainty reasoning
- intelligent exploration
- cinematic decision-making

## Recommended Next Steps

1. Build a Vercel frontend that consumes the Python engine via API or embeds
   simulation state.
2. Add a live grid-world stage with agent position, hazard animation, and UI
   panels for beliefs and actions.
3. Create a Hugging Face Space for experiment replay, parameter tuning, and
   benchmark reproducibility.
4. Update the README and landing page to highlight the hybrid strategy.
5. Record a cinematic demo video and feature it as the repository showcase.

## Developer Notes

The existing repo should remain the intelligence core. Future work can add
separate frontend and backend directories:

- `frontend/` — Next.js experience
- `backend/` — FastAPI simulation API and WebSockets
- `notebooks/` — Hugging Face research notebooks

This separation preserves the existing engine while enabling a high-end
presentation layer.
