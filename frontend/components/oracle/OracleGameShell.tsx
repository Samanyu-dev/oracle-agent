'use client'

import { useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { BootSequence } from '@/components/oracle/BootSequence'
import { CommandConsole } from '@/components/oracle/CommandConsole'
import { TacticalGrid } from '@/components/oracle/TacticalGrid'
import { AIBrainPanel } from '@/components/oracle/AIBrainPanel'
import { MissionFeed } from '@/components/oracle/MissionFeed'
import { TILE_LABEL, resolveTile } from '@/lib/oracle-utils'
import { useOracleStore } from '@/store/oracle-store'

export function OracleGameShell() {
  const {
    bootComplete,
    loading,
    error,
    session,
    missionMode,
    difficulty,
    agentType,
    useMcts,
    seedInput,
    modelPath,
    stepIntervalMs,
    autoRun,
    feed,
    selectedBrush,
    tileOverrides,
    hoverCell,
    camera,
    replayCursor,
    setBootComplete,
    setMissionMode,
    setDifficulty,
    setAgentType,
    setUseMcts,
    setSeedInput,
    setModelPath,
    setStepInterval,
    setAutoRun,
    toggleAutoRun,
    setBrush,
    setHoverCell,
    setReplayCursor,
    setCamera,
    applyTileOverride,
    clearOverrides,
    deployMission,
    stepOnce,
    resetMission,
    clearError,
  } = useOracleStore()

  useEffect(() => {
    if (!bootComplete || session) {
      return
    }
    void deployMission()
  }, [bootComplete, deployMission, session])

  useEffect(() => {
    if (!autoRun || !session || loading || session.done) {
      return
    }

    const timer = window.setInterval(() => {
      void stepOnce()
    }, stepIntervalMs)

    return () => window.clearInterval(timer)
  }, [autoRun, loading, session, stepIntervalMs, stepOnce])

  const replayRecord = useMemo(() => {
    if (!session || replayCursor === null) {
      return null
    }
    return session.history[replayCursor] ?? null
  }, [replayCursor, session])

  const hoveredTileInfo = useMemo(() => {
    if (!session || !hoverCell) {
      return null
    }
    const [r, c] = hoverCell
    const tile = resolveTile(session.grid, tileOverrides, r, c)
    const risk = session.risk_map?.[r]?.[c] ?? 0
    const entropy = session.entropy_map?.[r]?.[c] ?? 0
    return {
      r,
      c,
      tile,
      label: TILE_LABEL[tile],
      risk,
      entropy,
    }
  }, [hoverCell, session, tileOverrides])

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#03060d] text-cyan-50">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_16%_20%,rgba(21,122,143,0.27),transparent_42%),radial-gradient(circle_at_82%_10%,rgba(19,95,133,0.24),transparent_34%),linear-gradient(180deg,#02040a,#030810_62%,#03050b)]" />
      <div className="absolute inset-0 opacity-35 [background-image:linear-gradient(rgba(91,233,255,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(91,233,255,0.08)_1px,transparent_1px)] [background-size:42px_42px]" />

      <BootSequence active={!bootComplete} onComplete={() => setBootComplete(true)} />

      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: bootComplete ? 1 : 0, y: bootComplete ? 0 : 18 }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        className="relative z-10 mx-auto flex min-h-screen max-w-[1800px] flex-col px-3 pb-3 pt-3 md:px-4 md:pb-4"
      >
        <header className="panel-shell mb-3 flex flex-col gap-3 p-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-heading text-xl uppercase tracking-[0.26em] text-cyan-100 md:text-2xl">ORACLE // Autonomous Tactical Intelligence System</p>
            <p className="mt-1 text-sm text-cyan-100/70">Command an adaptive survival unit through uncertain hostile terrain.</p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.13em] text-cyan-100/80">
            <span className="status-chip">Mode {missionMode}</span>
            <span className="status-chip">Difficulty {difficulty}</span>
            <span className="status-chip">Agent {agentType}</span>
            <span className={`status-chip ${session?.done ? 'status-chip-critical' : autoRun ? 'status-chip-live' : ''}`}>
              {session?.done ? 'Mission Complete' : autoRun ? 'Autopilot Active' : 'Manual Control'}
            </span>
          </div>
        </header>

        {error ? (
          <div className="mb-3 rounded-lg border border-red-500/60 bg-red-950/50 px-4 py-2 text-sm text-red-100" onClick={clearError} role="button" tabIndex={0}>
            {error}
          </div>
        ) : null}

        <section className="grid flex-1 grid-cols-1 gap-3 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
          <CommandConsole
            missionMode={missionMode}
            difficulty={difficulty}
            agentType={agentType}
            useMcts={useMcts}
            seedInput={seedInput}
            modelPath={modelPath}
            stepIntervalMs={stepIntervalMs}
            autoRun={autoRun}
            loading={loading}
            selectedBrush={selectedBrush}
            onMissionMode={setMissionMode}
            onDifficulty={setDifficulty}
            onAgentType={setAgentType}
            onUseMcts={setUseMcts}
            onSeed={setSeedInput}
            onModelPath={setModelPath}
            onStepInterval={setStepInterval}
            onToggleAuto={toggleAutoRun}
            onDeploy={() => void deployMission()}
            onStep={() => void stepOnce()}
            onReset={() => void resetMission()}
            onBrush={setBrush}
            onClearOverrides={clearOverrides}
          />

          <div className="flex min-h-[420px] flex-col gap-3">
            <TacticalGrid
              session={session}
              overrides={tileOverrides}
              hoverCell={hoverCell}
              camera={camera}
              onCamera={setCamera}
              onHoverCell={setHoverCell}
              onCellApply={applyTileOverride}
            />

            {session ? (
              <section className="panel-shell px-3 py-2">
                <div className="mb-2 flex items-center justify-between text-xs uppercase tracking-[0.12em] text-cyan-100/80">
                  <span>Replay / Spectate</span>
                  <button type="button" className="mini-button" onClick={() => setReplayCursor(null)}>
                    Live
                  </button>
                </div>

                <input
                  type="range"
                  min={0}
                  max={Math.max(0, session.history.length - 1)}
                  value={replayCursor ?? Math.max(0, session.history.length - 1)}
                  onChange={(event) => setReplayCursor(Number(event.target.value))}
                  className="w-full"
                />

                <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs uppercase tracking-[0.11em] text-cyan-100/70">
                  <span>
                    Step {replayRecord?.step ?? session.history.length} / {Math.max(0, session.history.length)}
                  </span>
                  <span>
                    {replayRecord ? `Action ${replayRecord.action}` : `Latest action ${session.last_action ?? 'N/A'}`}
                  </span>
                </div>
              </section>
            ) : null}
          </div>

          <div className="flex flex-col gap-3">
            <AIBrainPanel session={session} />
            <section className="panel-shell p-3">
              <p className="panel-title">Tile Inspection</p>
              {hoveredTileInfo ? (
                <div className="mt-2 space-y-1 text-xs uppercase tracking-[0.12em] text-cyan-100/75">
                  <p>
                    CELL {hoveredTileInfo.r},{hoveredTileInfo.c}
                  </p>
                  <p>{hoveredTileInfo.label}</p>
                  <p>RISK {(hoveredTileInfo.risk * 100).toFixed(0)}%</p>
                  <p>ENTROPY {hoveredTileInfo.entropy.toFixed(2)}</p>
                </div>
              ) : (
                <p className="mt-2 text-xs uppercase tracking-[0.12em] text-cyan-100/55">Hover a tile for telemetry readout.</p>
              )}
            </section>
          </div>
        </section>

        <MissionFeed feed={feed} loading={loading} />
      </motion.div>
    </main>
  )
}
