'use client'

import { averageMatrixValue } from '@/lib/oracle-utils'
import { OracleStatePayload } from '@/lib/oracle-types'

interface AIBrainPanelProps {
  session: OracleStatePayload | null
}

function heatColor(value: number): string {
  const hue = 190 - Math.min(160, value * 160)
  const light = 22 + value * 35
  return `hsl(${hue}deg 82% ${light}%)`
}

export function AIBrainPanel({ session }: AIBrainPanelProps) {
  if (!session) {
    return (
      <aside className="panel-shell flex h-full min-h-[420px] items-center justify-center p-5">
        <div className="text-center">
          <p className="panel-title">AI Brain</p>
          <p className="panel-subtitle">Deploy mission to stream cognition telemetry.</p>
        </div>
      </aside>
    )
  }

  const [row, col] = session.agent_pos
  const localRisk = session.risk_map?.[row]?.[col] ?? 0
  const localEntropy = session.entropy_map?.[row]?.[col] ?? 0
  const localConfidence = session.confidence_map?.[row]?.[col] ?? 0
  const avgRisk = averageMatrixValue(session.risk_map)
  const avgEntropy = averageMatrixValue(session.entropy_map)

  const actionValues = session.cognition?.last_mcts_stats?.action_values ?? {}
  const rankedActions = Object.entries(actionValues).sort((a, b) => b[1] - a[1])
  const topAction = rankedActions[0]
  const secondAction = rankedActions[1]
  const policyConfidence = topAction && secondAction ? Math.max(0, Math.min(1, (topAction[1] - secondAction[1] + 1) / 2)) : 0.45

  return (
    <aside className="panel-shell flex h-full min-h-[420px] flex-col gap-4 p-4">
      <div>
        <p className="panel-title">AI Brain</p>
        <p className="panel-subtitle">Belief propagation, uncertainty pressure, and policy arbitration.</p>
      </div>

      <div className="brain-stat-grid">
        <div className="brain-stat">
          <p>Local Risk</p>
          <strong>{(localRisk * 100).toFixed(0)}%</strong>
        </div>
        <div className="brain-stat">
          <p>Entropy</p>
          <strong>{localEntropy.toFixed(2)}</strong>
        </div>
        <div className="brain-stat">
          <p>Certainty</p>
          <strong>{(localConfidence * 100).toFixed(0)}%</strong>
        </div>
        <div className="brain-stat">
          <p>Avg Grid Risk</p>
          <strong>{(avgRisk * 100).toFixed(0)}%</strong>
        </div>
      </div>

      <div className="brain-card">
        <p className="control-label">Belief Heatmap</p>
        <div className="mt-2 grid gap-[2px]" style={{ gridTemplateColumns: `repeat(${session.grid[0].length}, minmax(0, 1fr))` }}>
          {(session.risk_map ?? []).flatMap((riskRow, r) =>
            riskRow.map((risk, c) => {
              const entropy = session.entropy_map?.[r]?.[c] ?? 0
              const intensity = Math.min(1, (risk + entropy / 2.2) / 1.8)
              return (
                <div
                  key={`${r}:${c}`}
                  className={`h-4 rounded-[2px] ${session.agent_pos[0] === r && session.agent_pos[1] === c ? 'ring-1 ring-cyan-200' : ''}`}
                  style={{ background: heatColor(intensity) }}
                />
              )
            }),
          )}
        </div>
      </div>

      <div className="brain-card">
        <p className="control-label">MCTS Decision Fan</p>
        <svg viewBox="0 0 360 170" className="h-[170px] w-full rounded-lg bg-[#030d1a]">
          <circle cx="180" cy="36" r="12" fill="rgba(40,220,240,0.9)" />
          {rankedActions.slice(0, 5).map(([action, value], index, arr) => {
            const spread = arr.length > 1 ? index / (arr.length - 1) : 0.5
            const x = 40 + spread * 280
            const y = 130
            const normalized = Math.max(0, Math.min(1, (value + 12) / 25))
            const radius = 9 + normalized * 13
            return (
              <g key={action}>
                <line x1="180" y1="42" x2={x} y2={y - 14} stroke="rgba(73,198,255,0.35)" strokeWidth={1.5 + normalized * 2} />
                <circle cx={x} cy={y} r={radius} fill={`hsla(${165 - normalized * 100}, 92%, 58%, 0.82)`} />
                <text x={x} y={y + 3} textAnchor="middle" className="fill-[#01060c] text-[8px] font-bold uppercase">
                  {action.replace('walk_', '').replace('jump_', 'J')}
                </text>
              </g>
            )
          })}
        </svg>
        <p className="mt-2 text-xs uppercase tracking-[0.12em] text-cyan-100/70">
          Preferred Action: {topAction ? `${topAction[0]} (${topAction[1].toFixed(2)})` : 'insufficient rollout data'}
        </p>
      </div>

      <div className="brain-card">
        <p className="control-label">Policy Signal</p>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-cyan-300/15">
          <div className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-emerald-300 to-lime-300" style={{ width: `${policyConfidence * 100}%` }} />
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] uppercase tracking-[0.12em] text-cyan-100/75">
          <span>Exploration: {(100 - policyConfidence * 100).toFixed(0)}%</span>
          <span className="text-right">Exploitation: {(policyConfidence * 100).toFixed(0)}%</span>
        </div>
      </div>
    </aside>
  )
}
