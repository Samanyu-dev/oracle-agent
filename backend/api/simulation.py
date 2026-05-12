import os
import sys
import uuid
import random
from typing import Dict, Optional, Tuple, Any, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from env.grid_world import GridWorld
from grid_gen import generate_grid
from agents.deterministic_agent import DeterministicAgent
from agents.bayesian_agent import BayesianAgent
from agents.rl_agent import RLAgent
from learning.q_learning import QLearningEngine

ACTION_OPTIONS = GridWorld.ACTIONS
AGENT_TYPES = {'deterministic': DeterministicAgent,
               'bayesian': BayesianAgent,
               'rl': RLAgent}


class SimulationSession:
    def __init__(self,
                 session_id: str,
                 agent_type: str = 'bayesian',
                 use_mcts: bool = False,
                 grid_rows: int = 9,
                 grid_cols: int = 9,
                 seed: Optional[int] = None,
                 model_path: str = 'models/q_table.json',
                 mission_mode: str = 'survival',
                 difficulty: str = 'tactical'):
        self.session_id = session_id
        self.agent_type = agent_type
        self.use_mcts = use_mcts
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.seed = seed if seed is not None else random.randint(0, 2**31 - 1)
        self.model_path = model_path
        self.mission_mode = mission_mode
        self.difficulty = difficulty
        self.reset()

    def reset(self):
        if self.seed is not None:
            random.seed(self.seed)
        self.grid, self.path, self.anchor1, self.anchor2 = generate_grid(self.grid_rows, self.grid_cols, seed=self.seed)
        self.env = GridWorld(self.grid, seed=self.seed)
        self.agent = self._build_agent(self.agent_type)
        self.step_count = 0
        self.history = []
        self.last_action = None
        self.last_info = None
        self.done = False
        self.session_metadata = {
            'session_id': self.session_id,
            'agent_type': self.agent_type,
            'use_mcts': self.use_mcts,
            'grid_rows': self.grid_rows,
            'grid_cols': self.grid_cols,
            'seed': self.seed,
            'mission_mode': self.mission_mode,
            'difficulty': self.difficulty,
        }

    def _build_agent(self, agent_type: str):
        if agent_type == 'deterministic':
            return DeterministicAgent(self.grid)
        if agent_type == 'bayesian':
            return BayesianAgent(self.grid, use_mcts=self.use_mcts)
        if agent_type == 'rl':
            q_engine = QLearningEngine()
            if os.path.exists(self.model_path):
                q_engine.load(self.model_path)
            return RLAgent(self.grid, pretrained_q=q_engine)
        raise ValueError(f"Unsupported agent type: {agent_type}")

    def step(self, action: Optional[str] = None) -> Dict[str, Any]:
        if self.done:
            raise RuntimeError('Episode already finished')

        if action is None:
            action = self.agent.act(self.env)

        if action not in ACTION_OPTIONS:
            raise ValueError(f'Invalid action: {action}')

        transition = self.env.step(action)
        self.last_action = action
        self.last_info = transition.info
        self.step_count += 1
        self.done = transition.done

        record = {
            'step': self.step_count,
            'action': action,
            'next_pos': self.env.agent_pos,
            'reward': transition.reward,
            'done': transition.done,
            'info': transition.info,
            'lives': self.env.lives,
            'turns': self.env.turns,
            'time_units': self.env.time_units,
            'scan_count': dict(self.env.scan_count),
            'score': self.env.get_score(),
        }
        self.history.append(record)
        return self.serialize_state()

    def serialize_state(self) -> Dict[str, Any]:
        belief = None
        risk_map = None
        entropy_map = None
        confidence_map = None
        scan_heatmap = self._scan_heatmap()
        cognition = {}
        if hasattr(self.agent, 'belief'):
            belief_engine = getattr(self.agent, 'belief')
            if hasattr(belief_engine, 'to_array'):
                belief = belief_engine.to_array()
                risk_map = []
                entropy_map = []
                confidence_map = []
                for r in range(self.grid_rows):
                    risk_row = []
                    entropy_row = []
                    confidence_row = []
                    for c in range(self.grid_cols):
                        risk = belief_engine.get_risk(r, c)
                        entropy = belief_engine.entropy(r, c)
                        conf = max(belief_engine.get_belief(r, c).values())
                        risk_row.append(round(float(risk), 4))
                        entropy_row.append(round(float(entropy), 4))
                        confidence_row.append(round(float(conf), 4))
                    risk_map.append(risk_row)
                    entropy_map.append(entropy_row)
                    confidence_map.append(confidence_row)

        if hasattr(self.agent, 'get_runtime_insights'):
            cognition = self.agent.get_runtime_insights()

        agent_stats = self.agent.get_stats() if hasattr(self.agent, 'get_stats') else {}

        return {
            'session': self.session_metadata,
            'grid': self.grid,
            'agent_pos': tuple(self.env.agent_pos),
            'goal': tuple(self.env.goal),
            'lives': self.env.lives,
            'turns': self.env.turns,
            'time_units': self.env.time_units,
            'done': self.done,
            'last_action': self.last_action,
            'last_info': self.last_info,
            'history': self.history,
            'history_tail': self.history[-25:],
            'belief': belief,
            'risk_map': risk_map,
            'entropy_map': entropy_map,
            'confidence_map': confidence_map,
            'scan_heatmap': scan_heatmap,
            'agent_stats': agent_stats,
            'cognition': cognition,
            'actions': ACTION_OPTIONS,
        }

    def _scan_heatmap(self) -> List[List[int]]:
        heatmap = [[0 for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
        for (r, c), count in self.env.scan_count.items():
            heatmap[r][c] = int(count)
        return heatmap


class SimulationManager:
    def __init__(self):
        self.sessions: Dict[str, SimulationSession] = {}

    def create_session(self,
                       agent_type: str = 'bayesian',
                       use_mcts: bool = False,
                       grid_rows: int = 9,
                       grid_cols: int = 9,
                       seed: Optional[int] = None,
                       model_path: str = 'models/q_table.json',
                       mission_mode: str = 'survival',
                       difficulty: str = 'tactical') -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        session = SimulationSession(
            session_id=session_id,
            agent_type=agent_type,
            use_mcts=use_mcts,
            grid_rows=grid_rows,
            grid_cols=grid_cols,
            seed=seed,
            model_path=model_path,
            mission_mode=mission_mode,
            difficulty=difficulty,
        )
        self.sessions[session_id] = session
        return session.serialize_state()

    def get_session(self, session_id: str) -> SimulationSession:
        session = self.sessions.get(session_id)
        if session is None:
            raise KeyError(f'Unknown session {session_id}')
        return session

    def step_session(self, session_id: str, action: Optional[str] = None) -> Dict[str, Any]:
        session = self.get_session(session_id)
        return session.step(action)

    def reset_session(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        session.reset()
        return session.serialize_state()
