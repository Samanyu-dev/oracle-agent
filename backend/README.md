# Oracle Agent Backend

This backend provides a FastAPI simulation API for the Oracle Agent engine.
It is designed to be the server-side companion for a Vercel frontend experience
and a Hugging Face research playground.

## Features

- Simulation session management
- Deterministic, Bayesian, and RL agents
- Grid generation and episode stepping
- Belief state serialization for visualization
- Manual action override support

## Run locally

```bash
pip install -r requirements.txt
cd backend/api
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /health` — health check
- `GET /agents` — supported agents and actions
- `POST /sessions` — create a new simulation session
- `GET /sessions/{session_id}` — retrieve session state
- `POST /sessions/{session_id}/step` — advance the simulation one step
- `POST /sessions/{session_id}/reset` — reset the session

## Notes

The backend imports the existing Oracle intelligence engine from `src/`.
Use `model_path` when creating RL sessions to load a pretrained Q-table.
