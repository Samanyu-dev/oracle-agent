'use client'

import { PointerEventHandler, WheelEventHandler, useMemo, useRef } from 'react'
import { motion } from 'framer-motion'
import { CameraState, CellType, OracleStatePayload } from '@/lib/oracle-types'
import { TILE_LABEL, cellKey, resolveTile } from '@/lib/oracle-utils'

interface TacticalGridProps {
  session: OracleStatePayload | null
  overrides: Record<string, CellType>
  hoverCell: [number, number] | null
  camera: CameraState
  onCamera: (camera: Partial<CameraState>) => void
  onHoverCell: (cell: [number, number] | null) => void
  onCellApply: (r: number, c: number) => void
}

function terrainClass(tile: CellType): string {
  switch (tile) {
    case 'S':
      return 'tile-start'
    case 'G':
      return 'tile-goal'
    case 'V':
      return 'tile-volcano'
    case 'W':
      return 'tile-water'
    case 'B':
      return 'tile-brick'
    default:
      return 'tile-land'
  }
}

export function TacticalGrid({ session, overrides, hoverCell, camera, onCamera, onHoverCell, onCellApply }: TacticalGridProps) {
  const dragRef = useRef<{ x: number; y: number; panX: number; panY: number } | null>(null)

  const rows = session?.grid.length ?? 0
  const cols = session?.grid[0]?.length ?? 0

  const pathSet = useMemo(() => {
    const cells = session?.cognition?.path_preview ?? []
    return new Set(cells.map((cell) => cellKey(cell[0], cell[1])))
  }, [session?.cognition?.path_preview])

  if (!session) {
    return (
      <section className="panel-shell flex h-full min-h-[420px] items-center justify-center p-6">
        <div className="text-center">
          <p className="font-heading text-2xl uppercase tracking-[0.2em] text-cyan-200">Awaiting Deployment</p>
          <p className="mt-3 text-sm text-cyan-100/70">Initialize a mission profile from Command Terminal to activate world renderer.</p>
        </div>
      </section>
    )
  }

  const [agentRow, agentCol] = session.agent_pos
  const transformOrigin = `${((agentCol + 0.5) / cols) * 100}% ${((agentRow + 0.5) / rows) * 100}%`

  const onWheel: WheelEventHandler<HTMLDivElement> = (event) => {
    event.preventDefault()
    const delta = -event.deltaY * 0.001
    const nextZoom = Math.max(0.65, Math.min(2.4, camera.zoom + delta))
    onCamera({ zoom: nextZoom })
  }

  const onPointerDown: PointerEventHandler<HTMLDivElement> = (event) => {
    if (camera.followMode) {
      return
    }
    dragRef.current = {
      x: event.clientX,
      y: event.clientY,
      panX: camera.panX,
      panY: camera.panY,
    }
  }

  const onPointerMove: PointerEventHandler<HTMLDivElement> = (event) => {
    if (!dragRef.current || camera.followMode) {
      return
    }
    const dx = event.clientX - dragRef.current.x
    const dy = event.clientY - dragRef.current.y
    onCamera({ panX: dragRef.current.panX + dx, panY: dragRef.current.panY + dy })
  }

  const onPointerUp: PointerEventHandler<HTMLDivElement> = () => {
    dragRef.current = null
  }

  const effectivePanX = camera.followMode ? 0 : camera.panX
  const effectivePanY = camera.followMode ? 0 : camera.panY

  return (
    <section className="panel-shell relative flex h-full min-h-[420px] flex-col overflow-hidden p-3">
      <div className="mb-3 flex items-center justify-between px-1">
        <div>
          <p className="panel-title">Live Grid World</p>
          <p className="panel-subtitle">Terrain + cognition overlays rendered in real time.</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="mini-button"
            onClick={() => onCamera({ followMode: !camera.followMode, panX: 0, panY: 0 })}
          >
            {camera.followMode ? 'Follow' : 'Free Cam'}
          </button>
          <button type="button" className="mini-button" onClick={() => onCamera({ zoom: 1, panX: 0, panY: 0 })}>
            Recenter
          </button>
        </div>
      </div>

      <div
        className="relative flex-1 overflow-hidden rounded-xl border border-cyan-300/20 bg-[#01070d]"
        onWheel={onWheel}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
        <div className="world-noise" />
        <div
          className="absolute inset-0"
          style={{
            transform: `translate(${effectivePanX}px, ${effectivePanY}px) scale(${camera.zoom})`,
            transformOrigin: camera.followMode ? transformOrigin : '50% 50%',
            transition: camera.followMode ? 'transform 220ms ease-out' : 'none',
          }}
        >
          <div
            className="grid h-full w-full gap-[2px] bg-cyan-400/15 p-[2px]"
            style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
          >
            {session.grid.map((row, r) =>
              row.map((_, c) => {
                const tile = resolveTile(session.grid, overrides, r, c)
                const key = cellKey(r, c)
                const risk = session.risk_map?.[r]?.[c] ?? 0
                const entropy = session.entropy_map?.[r]?.[c] ?? 0
                const scanCount = session.scan_heatmap?.[r]?.[c] ?? 0
                const isPath = pathSet.has(key)
                const isHover = hoverCell?.[0] === r && hoverCell?.[1] === c

                return (
                  <button
                    type="button"
                    key={key}
                    onMouseEnter={() => onHoverCell([r, c])}
                    onMouseLeave={() => onHoverCell(null)}
                    onClick={() => onCellApply(r, c)}
                    className={`tile-cell ${terrainClass(tile)} ${isHover ? 'tile-hover' : ''}`}
                    title={`${TILE_LABEL[tile]} | Risk ${(risk * 100).toFixed(0)}% | Entropy ${entropy.toFixed(2)}`}
                  >
                    <span
                      className="tile-risk-overlay"
                      style={{ opacity: Math.min(0.7, risk * 0.85), boxShadow: `0 0 ${18 + risk * 38}px rgba(255, 94, 73, ${risk * 0.38})` }}
                    />
                    {scanCount > 0 ? (
                      <span className="tile-scan-count">
                        {scanCount}
                      </span>
                    ) : null}
                    {isPath ? <span className="tile-path-dot" /> : null}
                  </button>
                )
              }),
            )}
          </div>

          <motion.div
            className="agent-token"
            animate={{
              top: `calc(${((agentRow + 0.5) / rows) * 100}% - 14px)`,
              left: `calc(${((agentCol + 0.5) / cols) * 100}% - 14px)`,
              rotate: session.last_action?.endsWith('_n')
                ? -90
                : session.last_action?.endsWith('_s')
                  ? 90
                  : session.last_action?.endsWith('_w')
                    ? 180
                    : 0,
            }}
            transition={{ type: 'spring', stiffness: 200, damping: 22 }}
          >
            <span className="agent-core" />
            {session.last_action === 'scan' ? <span className="agent-scan-pulse" /> : null}
          </motion.div>
        </div>
      </div>

      <div className="mt-2 flex items-center justify-between text-xs uppercase tracking-[0.12em] text-cyan-100/70">
        <span>
          CAM {camera.followMode ? 'FOLLOW' : 'FREE'} | ZOOM {camera.zoom.toFixed(2)}x
        </span>
        <span>
          POS {session.agent_pos[0]},{session.agent_pos[1]} | LIVES {session.lives}
        </span>
      </div>
    </section>
  )
}
