'use client'

import { DIFFICULTY_PRESETS, MISSION_MODES, TILE_BRUSHES } from '@/lib/oracle-utils'
import { AgentType, Difficulty, MissionMode, TileBrush } from '@/lib/oracle-types'

interface CommandConsoleProps {
  missionMode: MissionMode
  difficulty: Difficulty
  agentType: AgentType
  useMcts: boolean
  seedInput: string
  modelPath: string
  stepIntervalMs: number
  autoRun: boolean
  loading: boolean
  selectedBrush: TileBrush
  onMissionMode: (value: MissionMode) => void
  onDifficulty: (value: Difficulty) => void
  onAgentType: (value: AgentType) => void
  onUseMcts: (value: boolean) => void
  onSeed: (value: string) => void
  onModelPath: (value: string) => void
  onStepInterval: (value: number) => void
  onToggleAuto: () => void
  onDeploy: () => void
  onStep: () => void
  onReset: () => void
  onBrush: (value: TileBrush) => void
  onClearOverrides: () => void
}

export function CommandConsole({
  missionMode,
  difficulty,
  agentType,
  useMcts,
  seedInput,
  modelPath,
  stepIntervalMs,
  autoRun,
  loading,
  selectedBrush,
  onMissionMode,
  onDifficulty,
  onAgentType,
  onUseMcts,
  onSeed,
  onModelPath,
  onStepInterval,
  onToggleAuto,
  onDeploy,
  onStep,
  onReset,
  onBrush,
  onClearOverrides,
}: CommandConsoleProps) {
  return (
    <aside className="panel-shell flex h-full flex-col gap-4 p-4">
      <div>
        <p className="panel-title">Command Terminal</p>
        <p className="panel-subtitle">Configure deployment, then execute tactical simulation loops.</p>
      </div>

      <div className="terminal-section">
        <label className="control-label">Mission Profile</label>
        <select value={missionMode} onChange={(event) => onMissionMode(event.target.value as MissionMode)} className="control-select">
          {MISSION_MODES.map((mode) => (
            <option key={mode.value} value={mode.value}>
              {mode.label}
            </option>
          ))}
        </select>
        <p className="control-note">
          {MISSION_MODES.find((mode) => mode.value === missionMode)?.subtitle ?? 'Adaptive mission envelope'}
        </p>
      </div>

      <div className="terminal-section grid grid-cols-2 gap-3">
        <div>
          <label className="control-label">Difficulty</label>
          <select value={difficulty} onChange={(event) => onDifficulty(event.target.value as Difficulty)} className="control-select">
            {Object.entries(DIFFICULTY_PRESETS).map(([key, value]) => (
              <option key={key} value={key}>
                {value.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="control-label">Agent Core</label>
          <select value={agentType} onChange={(event) => onAgentType(event.target.value as AgentType)} className="control-select">
            <option value="deterministic">Deterministic</option>
            <option value="bayesian">Bayesian</option>
            <option value="rl">RL</option>
          </select>
        </div>
      </div>

      <div className="terminal-section grid grid-cols-2 gap-3">
        <div>
          <label className="control-label">Seed</label>
          <input
            value={seedInput}
            onChange={(event) => onSeed(event.target.value)}
            className="control-input"
            placeholder="42"
            inputMode="numeric"
          />
        </div>

        <div>
          <label className="control-label">Auto Tick (ms)</label>
          <input
            type="number"
            min={220}
            max={1600}
            step={10}
            value={stepIntervalMs}
            onChange={(event) => onStepInterval(Number(event.target.value) || 700)}
            className="control-input"
          />
        </div>
      </div>

      <div className="terminal-section">
        <label className="control-label">RL Model Path</label>
        <input
          value={modelPath}
          onChange={(event) => onModelPath(event.target.value)}
          className="control-input"
          placeholder="models/q_table.json"
        />
        <label className="mt-3 flex items-center gap-2 text-xs uppercase tracking-[0.14em] text-cyan-100/80">
          <input
            type="checkbox"
            checked={useMcts}
            disabled={agentType !== 'bayesian'}
            onChange={(event) => onUseMcts(event.target.checked)}
            className="h-4 w-4 rounded border-cyan-500/60 bg-transparent"
          />
          Enable MCTS augmentation
        </label>
      </div>

      <div className="terminal-section">
        <label className="control-label">World Edit Brush</label>
        <div className="grid grid-cols-3 gap-2">
          {TILE_BRUSHES.map((brush) => (
            <button
              key={brush.value}
              type="button"
              onClick={() => onBrush(brush.value)}
              className={`brush-button ${selectedBrush === brush.value ? 'is-active' : ''}`}
            >
              {brush.label}
            </button>
          ))}
        </div>
        <button type="button" className="mt-2 text-xs uppercase tracking-[0.14em] text-cyan-300/80" onClick={onClearOverrides}>
          clear tactical edits
        </button>
      </div>

      <div className="mt-auto grid grid-cols-2 gap-2">
        <button type="button" className="command-button command-button--primary" onClick={onDeploy} disabled={loading}>
          Deploy
        </button>
        <button type="button" className="command-button" onClick={onStep} disabled={loading}>
          Tick
        </button>
        <button type="button" className={`command-button ${autoRun ? 'command-button--alert' : ''}`} onClick={onToggleAuto}>
          {autoRun ? 'Pause' : 'Autoplay'}
        </button>
        <button type="button" className="command-button" onClick={onReset} disabled={loading}>
          Reset
        </button>
      </div>
    </aside>
  )
}
