import os
import sys
from typing import Tuple, Dict, Any

import gradio as gr

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from env.grid_world import GridWorld
from grid_gen import generate_grid
from agents.deterministic_agent import DeterministicAgent
from agents.bayesian_agent import BayesianAgent
from agents.rl_agent import RLAgent
from learning.q_learning import QLearningEngine
from visualize.plots import plot_reward_curve, plot_success_rate, plot_benchmark_comparison, plot_belief_evolution


def build_agent(agent_choice: str, grid, use_mcts: bool, model_path: str):
    if agent_choice == 'Deterministic':
        return DeterministicAgent(grid)
    if agent_choice == 'Bayesian':
        return BayesianAgent(grid, use_mcts=use_mcts)
    if agent_choice == 'RL':
        q_engine = QLearningEngine()
        if os.path.exists(model_path):
            q_engine.load(model_path)
        return RLAgent(grid, pretrained_q=q_engine)
    raise ValueError('Unsupported agent')


def run_demo(agent_choice: str, grid_size: int, seed: int, use_mcts: bool, model_path: str) -> Tuple[str, Any, str]:
    grid, _, _, _ = generate_grid(grid_size, grid_size, seed=seed)
    env = GridWorld(grid, seed=seed)
    agent = build_agent(agent_choice, grid, use_mcts, model_path)
    history = []
    belief_history = []

    while not env.agent_pos == env.goal and env.lives > 0 and len(history) < 300:
        action = agent.act(env)
        trans = env.step(action)
        if hasattr(agent, 'belief') and hasattr(agent.belief, 'to_array'):
            belief_history.append({'step': len(history) + 1, 'beliefs': agent.belief.to_array()})
        history.append({'step': len(history) + 1, 'action': action, 'reward': trans.reward, 'info': trans.info, 'pos': env.agent_pos, 'lives': env.lives})

    metrics = {
        'success': env.agent_pos == env.goal,
        'steps': len(history),
        'lives': env.lives,
        'score': env.get_score(),
        'last_action': history[-1]['action'] if history else None,
        'total_reward': sum(item['reward'] for item in history),
    }

    metrics_text = '\n'.join([f'{key}: {value}' for key, value in metrics.items()])
    chart_path = os.path.join('hf_space_outputs', f'{agent_choice.lower()}_demo_{seed}.png')
    if belief_history and hasattr(plot_belief_evolution, '__call__'):
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        plot_belief_evolution(belief_history, path=chart_path)
        chart = chart_path
    else:
        chart = None

    grid_display = '\n'.join([''.join(str(cell) for cell in row) for row in grid])
    return metrics_text, chart, grid_display


def build_ui():
    with gr.Blocks(title='Oracle Agent Research Lab') as demo:
        gr.Markdown('# Oracle Agent Research Lab')
        gr.Markdown(
            'A Hugging Face Space-ready research interface for experiment tuning, benchmark visualization, and policy playback.'
        )

        with gr.Row():
            with gr.Column(scale=2):
                agent_choice = gr.Dropdown(['Deterministic', 'Bayesian', 'RL'], value='Bayesian', label='Agent Type')
                grid_size = gr.Slider(5, 15, value=9, step=1, label='Grid Size')
                seed = gr.Number(value=42, precision=0, label='Random Seed')
                use_mcts = gr.Checkbox(value=False, label='Enable MCTS for Bayesian')
                model_path = gr.Textbox(value='models/q_table.json', label='RL model path')
                run_button = gr.Button('Run Demo')

            with gr.Column(scale=3):
                output_text = gr.Textbox(lines=8, label='Summary Metrics')
                output_plot = gr.Image(label='Belief / Entropy Plot')
                output_grid = gr.Code(label='Generated Grid')

        run_button.click(
            fn=run_demo,
            inputs=[agent_choice, grid_size, seed, use_mcts, model_path],
            outputs=[output_text, output_plot, output_grid]
        )

    return demo


if __name__ == '__main__':
    app = build_ui()
    app.launch(server_name='0.0.0.0', server_port=7860)
