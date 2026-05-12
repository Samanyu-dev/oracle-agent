export type CellType = 'L' | 'V' | 'W' | 'B' | 'S' | 'G'

export type AgentType = 'deterministic' | 'bayesian' | 'rl'

export type Difficulty = 'easy' | 'tactical' | 'veteran' | 'impossible' | 'chaos-ai'

export type MissionMode =
  | 'survival'
  | 'extraction'
  | 'recon'
  | 'escape'
  | 'hazard-sweep'
  | 'blackout'
  | 'infinite-terrain'
  | 'sensor-failure'
  | 'rl-arena'
  | 'adaptive-nightmare'

export type TileBrush = CellType | 'erase'

export interface SessionMeta {
  session_id: string
  agent_type: AgentType
  use_mcts: boolean
  grid_rows: number
  grid_cols: number
  seed: number
  mission_mode: MissionMode
  difficulty: Difficulty
}

export interface StepInfo {
  action: string
  took_damage?: boolean
  scanned?: boolean
}

export interface StepRecord {
  step: number
  action: string
  next_pos: [number, number]
  reward: number
  done: boolean
  info: StepInfo
  lives: number
  turns: number
  time_units: number
  scan_count: Record<string, number>
  score: number
}

export interface MctsStats {
  visits?: number
  value?: number
  action_values?: Record<string, number>
}

export interface RuntimeInsights {
  path_preview?: number[][]
  path_index?: number
  next_waypoint?: number[] | null
  last_mcts_stats?: MctsStats
  last_decision?: Record<string, unknown>
  scan_events?: Array<Record<string, unknown>>
  epsilon?: number
}

export interface OracleStatePayload {
  session: SessionMeta
  grid: CellType[][]
  agent_pos: [number, number]
  goal: [number, number]
  lives: number
  turns: number
  time_units: number
  done: boolean
  last_action: string | null
  last_info: StepInfo | null
  history: StepRecord[]
  history_tail: StepRecord[]
  belief: Array<Array<Record<string, number>>> | null
  risk_map: number[][] | null
  entropy_map: number[][] | null
  confidence_map: number[][] | null
  scan_heatmap: number[][] | null
  agent_stats: Record<string, unknown>
  cognition: RuntimeInsights
  actions: string[]
}

export interface CreateSessionPayload {
  agent_type: AgentType
  use_mcts: boolean
  grid_rows: number
  grid_cols: number
  seed?: number
  model_path: string
  mission_mode: MissionMode
  difficulty: Difficulty
}

export interface MissionEvent {
  id: string
  code: string
  level: 'info' | 'warn' | 'critical' | 'success'
  message: string
  timestamp: number
}

export interface CameraState {
  zoom: number
  panX: number
  panY: number
  followMode: boolean
}
