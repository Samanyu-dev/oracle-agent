# Oracle Agent Hugging Face Space

This folder contains a starter Gradio application for a Hugging Face research
space.

## Purpose

- parameter tuning and experiment control
- benchmark playback and result visualization
- reproducibility-friendly simulation
- research-quality demo interface

## Run locally

```bash
pip install -r requirements.txt
cd hf_space
python app.py
```

Then open the UI at `http://127.0.0.1:7860`.

## Notes

The demo uses the existing `src/` intelligence engine and GridWorld simulation.
It is designed to be a research playground where users can compare Bayesian,
RL, and deterministic planning with reproducible seed control.
