import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from .simulation import SimulationManager

app = FastAPI(
    title='Oracle Agent Backend API',
    description='FastAPI simulation backend for Oracle Agent frontend and research playground',
    version='0.1.0'
)

manager = SimulationManager()


class SessionCreateRequest(BaseModel):
    agent_type: str = Field('bayesian', description='Agent type: deterministic, bayesian, rl')
    use_mcts: bool = Field(False, description='Enable MCTS for Bayesian agent')
    grid_rows: int = Field(9, ge=5, le=25, description='Grid row count')
    grid_cols: int = Field(9, ge=5, le=25, description='Grid column count')
    seed: Optional[int] = Field(None, description='Optional RNG seed')
    model_path: str = Field('models/q_table.json', description='Path to saved RL Q-table')
    mission_mode: str = Field('survival', description='Mission mode profile')
    difficulty: str = Field('tactical', description='Difficulty profile')


class StepRequest(BaseModel):
    action: Optional[str] = Field(None, description='Optional explicit action for manual control')


@app.get('/health')
def health_check() -> Dict[str, str]:
    return {'status': 'ok', 'service': 'Oracle Agent API'}


@app.get('/agents')
def list_agents() -> Dict[str, list]:
    return {
        'agent_types': ['deterministic', 'bayesian', 'rl'],
        'actions': ['walk_n', 'walk_s', 'walk_e', 'walk_w', 'jump_n', 'jump_s', 'jump_e', 'jump_w', 'scan']
    }


@app.post('/sessions')
def create_session(request: SessionCreateRequest):
    try:
        return manager.create_session(
            agent_type=request.agent_type,
            use_mcts=request.use_mcts,
            grid_rows=request.grid_rows,
            grid_cols=request.grid_cols,
            seed=request.seed,
            model_path=request.model_path,
            mission_mode=request.mission_mode,
            difficulty=request.difficulty,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get('/sessions/{session_id}')
def get_session(session_id: str):
    try:
        return manager.get_session(session_id).serialize_state()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post('/sessions/{session_id}/step')
def step_session(session_id: str, request: StepRequest):
    try:
        return manager.step_session(session_id, action=request.action)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post('/sessions/{session_id}/reset')
def reset_session(session_id: str):
    try:
        return manager.reset_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
