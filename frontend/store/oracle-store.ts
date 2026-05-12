'use client'

import { create } from 'zustand'
import { createSession, getSession, resetSession, stepSession } from '@/lib/oracle-api'
import {
  AgentType,
  CameraState,
  CellType,
  Difficulty,
  MissionEvent,
  MissionMode,
  OracleStatePayload,
  TileBrush,
} from '@/lib/oracle-types'
import { DIFFICULTY_PRESETS, buildStepEvent, makeEvent } from '@/lib/oracle-utils'

interface OracleStoreState {
  bootComplete: boolean
  loading: boolean
  error: string | null
  session: OracleStatePayload | null
  missionMode: MissionMode
  difficulty: Difficulty
  agentType: AgentType
  useMcts: boolean
  seedInput: string
  modelPath: string
  stepIntervalMs: number
  autoRun: boolean
  feed: MissionEvent[]
  selectedBrush: TileBrush
  tileOverrides: Record<string, CellType>
  hoverCell: [number, number] | null
  camera: CameraState
  replayCursor: number | null
  setBootComplete: (value: boolean) => void
  setMissionMode: (mode: MissionMode) => void
  setDifficulty: (difficulty: Difficulty) => void
  setAgentType: (agentType: AgentType) => void
  setUseMcts: (value: boolean) => void
  setSeedInput: (value: string) => void
  setModelPath: (value: string) => void
  setStepInterval: (value: number) => void
  setAutoRun: (value: boolean) => void
  toggleAutoRun: () => void
  setBrush: (brush: TileBrush) => void
  setHoverCell: (cell: [number, number] | null) => void
  setReplayCursor: (index: number | null) => void
  setCamera: (camera: Partial<CameraState>) => void
  applyTileOverride: (r: number, c: number) => void
  clearOverrides: () => void
  deployMission: () => Promise<void>
  refreshSession: () => Promise<void>
  stepOnce: (action?: string) => Promise<void>
  resetMission: () => Promise<void>
  clearError: () => void
}

function appendFeed(feed: MissionEvent[], event: MissionEvent): MissionEvent[] {
  return [event, ...feed].slice(0, 80)
}

export const useOracleStore = create<OracleStoreState>((set, get) => ({
  bootComplete: false,
  loading: false,
  error: null,
  session: null,
  missionMode: 'survival',
  difficulty: 'tactical',
  agentType: 'bayesian',
  useMcts: true,
  seedInput: '42',
  modelPath: 'models/q_table.json',
  stepIntervalMs: DIFFICULTY_PRESETS.tactical.stepIntervalMs,
  autoRun: false,
  feed: [makeEvent('SYS_READY', 'info', 'ORACLE GRID awaiting mission deployment.')],
  selectedBrush: 'V',
  tileOverrides: {},
  hoverCell: null,
  camera: {
    zoom: 1,
    panX: 0,
    panY: 0,
    followMode: true,
  },
  replayCursor: null,

  setBootComplete: (value) => {
    set((state) => ({
      bootComplete: value,
      feed: appendFeed(state.feed, makeEvent('BOOT', 'success', 'Command lattice synchronized. Awaiting deploy order.')),
    }))
  },

  setMissionMode: (mode) => set({ missionMode: mode }),

  setDifficulty: (difficulty) => {
    const preset = DIFFICULTY_PRESETS[difficulty]
    set((state) => ({
      difficulty,
      stepIntervalMs: preset.stepIntervalMs,
      useMcts: state.agentType === 'bayesian' ? preset.defaultMcts : state.useMcts,
    }))
  },

  setAgentType: (agentType) => set({ agentType }),
  setUseMcts: (value) => set({ useMcts: value }),
  setSeedInput: (value) => set({ seedInput: value }),
  setModelPath: (value) => set({ modelPath: value }),
  setStepInterval: (value) => set({ stepIntervalMs: value }),
  setAutoRun: (value) => set({ autoRun: value }),
  toggleAutoRun: () => set((state) => ({ autoRun: !state.autoRun })),
  setBrush: (brush) => set({ selectedBrush: brush }),
  setHoverCell: (cell) => set({ hoverCell: cell }),
  setReplayCursor: (index) => set({ replayCursor: index }),
  setCamera: (camera) => set((state) => ({ camera: { ...state.camera, ...camera } })),

  applyTileOverride: (r, c) => {
    const state = get()
    const session = state.session
    if (!session) {
      return
    }

    const current = session.grid[r][c]
    if (current === 'S' || current === 'G') {
      return
    }

    const key = `${r}:${c}`
    const overrides = { ...state.tileOverrides }

    if (state.selectedBrush === 'erase') {
      delete overrides[key]
    } else {
      overrides[key] = state.selectedBrush
    }

    set({ tileOverrides: overrides })
  },

  clearOverrides: () => set({ tileOverrides: {} }),

  deployMission: async () => {
    const state = get()
    const preset = DIFFICULTY_PRESETS[state.difficulty]
    const seed = state.seedInput.trim().length ? Number(state.seedInput) : undefined

    set({ loading: true, error: null, autoRun: false, replayCursor: null, tileOverrides: {} })
    try {
      const payload = await createSession({
        agent_type: state.agentType,
        use_mcts: state.agentType === 'bayesian' ? state.useMcts : false,
        grid_rows: preset.gridSize,
        grid_cols: preset.gridSize,
        seed: Number.isFinite(seed as number) ? seed : undefined,
        model_path: state.modelPath,
        mission_mode: state.missionMode,
        difficulty: state.difficulty,
      })

      set((curr) => ({
        session: payload,
        loading: false,
        feed: appendFeed(
          appendFeed(
            curr.feed,
            makeEvent(
              'DEPLOY',
              'success',
              `Mission ${state.missionMode.toUpperCase()} deployed at ${state.difficulty.toUpperCase()} profile.`,
            ),
          ),
          makeEvent('GRID_ONLINE', 'info', `Grid ${preset.gridSize}x${preset.gridSize} synchronized. Unit at deployment tile.`),
        ),
      }))
    } catch (error) {
      set((curr) => ({
        loading: false,
        error: error instanceof Error ? error.message : 'Mission deployment failed',
        feed: appendFeed(curr.feed, makeEvent('DEPLOY_FAIL', 'critical', 'Deployment handshake failed. Validate backend link.')),
      }))
    }
  },

  refreshSession: async () => {
    const state = get()
    if (!state.session) {
      return
    }

    try {
      const payload = await getSession(state.session.session.session_id)
      set({ session: payload })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Session refresh failed' })
    }
  },

  stepOnce: async (action) => {
    const state = get()
    if (!state.session || state.loading || state.session.done) {
      return
    }

    set({ loading: true, error: null })
    try {
      const payload = await stepSession(state.session.session.session_id, action)
      const nextEvent = buildStepEvent(payload)

      set((curr) => ({
        session: payload,
        loading: false,
        autoRun: payload.done ? false : curr.autoRun,
        feed: nextEvent ? appendFeed(curr.feed, nextEvent) : curr.feed,
      }))
    } catch (error) {
      set((curr) => ({
        loading: false,
        autoRun: false,
        error: error instanceof Error ? error.message : 'Step execution failed',
        feed: appendFeed(curr.feed, makeEvent('STEP_ABORT', 'warn', 'Step request aborted by backend safeguard.')),
      }))
    }
  },

  resetMission: async () => {
    const state = get()
    if (!state.session) {
      return
    }

    set({ loading: true, error: null, autoRun: false, replayCursor: null })
    try {
      const payload = await resetSession(state.session.session.session_id)
      set((curr) => ({
        session: payload,
        loading: false,
        feed: appendFeed(curr.feed, makeEvent('RESET', 'info', 'Mission state reset. Tactical clocks zeroed.')),
      }))
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : 'Reset failed',
      })
    }
  },

  clearError: () => set({ error: null }),
}))
