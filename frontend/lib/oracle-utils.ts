import {
  CellType,
  Difficulty,
  MissionEvent,
  MissionMode,
  OracleStatePayload,
  TileBrush,
} from './oracle-types'

export const MISSION_MODES: Array<{ value: MissionMode; label: string; subtitle: string }> = [
  { value: 'survival', label: 'Survival', subtitle: 'Endure dynamic hazards.' },
  { value: 'extraction', label: 'Extraction', subtitle: 'Secure route to evac zone.' },
  { value: 'recon', label: 'Recon', subtitle: 'Map unknown sectors quickly.' },
  { value: 'escape', label: 'Escape', subtitle: 'Minimal life-loss breakout.' },
  { value: 'hazard-sweep', label: 'Hazard Sweep', subtitle: 'Identify and tag danger tiles.' },
  { value: 'blackout', label: 'Blackout Mode', subtitle: 'Limited visibility simulation.' },
  { value: 'infinite-terrain', label: 'Infinite Terrain', subtitle: 'Extended patrol scaling.' },
  { value: 'sensor-failure', label: 'Sensor Failure', subtitle: 'Noisy telemetry stress test.' },
  { value: 'rl-arena', label: 'RL Arena', subtitle: 'Policy adaptation scenario.' },
  { value: 'adaptive-nightmare', label: 'Adaptive Nightmare', subtitle: 'Aggressive uncertainty regime.' },
]

export const DIFFICULTY_PRESETS: Record<
  Difficulty,
  { label: string; gridSize: number; defaultMcts: boolean; stepIntervalMs: number }
> = {
  easy: { label: 'Easy', gridSize: 8, defaultMcts: false, stepIntervalMs: 900 },
  tactical: { label: 'Tactical', gridSize: 9, defaultMcts: true, stepIntervalMs: 700 },
  veteran: { label: 'Veteran', gridSize: 11, defaultMcts: true, stepIntervalMs: 550 },
  impossible: { label: 'Impossible', gridSize: 13, defaultMcts: true, stepIntervalMs: 450 },
  'chaos-ai': { label: 'Chaos AI', gridSize: 15, defaultMcts: true, stepIntervalMs: 350 },
}

export const TILE_LABEL: Record<CellType, string> = {
  L: 'Safe Corridor',
  V: 'Lava Field',
  W: 'Flooded Zone',
  B: 'Reinforced Wall',
  S: 'Deployment',
  G: 'Extraction',
}

export const TILE_BRUSHES: Array<{ value: TileBrush; label: string }> = [
  { value: 'V', label: 'Lava' },
  { value: 'W', label: 'Flood' },
  { value: 'B', label: 'Wall' },
  { value: 'L', label: 'Safe' },
  { value: 'erase', label: 'Reset' },
]

export function cellKey(r: number, c: number): string {
  return `${r}:${c}`
}

export function resolveTile(
  grid: CellType[][],
  overrides: Record<string, CellType>,
  r: number,
  c: number,
): CellType {
  const key = cellKey(r, c)
  return overrides[key] ?? grid[r][c]
}

export function buildStepEvent(next: OracleStatePayload): MissionEvent | null {
  const latest = next.history[next.history.length - 1]
  if (!latest) {
    return null
  }

  if (latest.info?.scanned) {
    return makeEvent('SENSOR_SCAN', 'info', `Sensor sweep completed at tile (${latest.next_pos[0]}, ${latest.next_pos[1]}).`)
  }

  if (latest.info?.took_damage) {
    return makeEvent('HAZARD_CONTACT', 'critical', `Hazard impact registered. Hull integrity reduced to ${latest.lives}.`)
  }

  if (next.done && next.agent_pos[0] === next.goal[0] && next.agent_pos[1] === next.goal[1]) {
    return makeEvent('MISSION_SUCCESS', 'success', `Extraction secured in ${latest.step} turns. Tactical score ${latest.score.toFixed(2)}.`)
  }

  if (next.done) {
    return makeEvent('MISSION_FAILURE', 'critical', 'Unit lost. Simulation terminated.')
  }

  const actionLabel = latest.action.replace('_', ' ').toUpperCase()
  return makeEvent(
    'PATH_UPDATE',
    'info',
    `Action ${actionLabel} executed. Reward ${latest.reward.toFixed(1)}. Lives ${latest.lives}.`,
  )
}

export function makeEvent(code: string, level: MissionEvent['level'], message: string): MissionEvent {
  return {
    id: `${code}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    code,
    level,
    message,
    timestamp: Date.now(),
  }
}

export function averageMatrixValue(matrix: number[][] | null): number {
  if (!matrix || !matrix.length || !matrix[0].length) {
    return 0
  }

  let sum = 0
  let count = 0
  for (const row of matrix) {
    for (const val of row) {
      sum += val
      count += 1
    }
  }
  return count ? sum / count : 0
}
