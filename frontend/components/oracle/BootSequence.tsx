'use client'

import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface BootSequenceProps {
  active: boolean
  onComplete: () => void
}

const BOOT_LINES = [
  'ORACLE // AUTONOMOUS TACTICAL INTELLIGENCE SYSTEM',
  'INIT BIOS ... OK',
  'MESH LINK ... ESTABLISHED',
  'SENSOR ARRAY ... CALIBRATED',
  'BAYESIAN CORE ... ONLINE',
  'MCTS ENGINE ... STANDBY',
  'MISSION GRID ... SYNCED',
  'COMMAND AUTHORIZATION ... GRANTED',
]

export function BootSequence({ active, onComplete }: BootSequenceProps) {
  const [lineIndex, setLineIndex] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!active) {
      return
    }

    const lineTimer = window.setInterval(() => {
      setLineIndex((prev) => Math.min(prev + 1, BOOT_LINES.length))
    }, 420)

    const progressTimer = window.setInterval(() => {
      setProgress((prev) => Math.min(100, prev + 4 + Math.random() * 8))
    }, 180)

    return () => {
      window.clearInterval(lineTimer)
      window.clearInterval(progressTimer)
    }
  }, [active])

  useEffect(() => {
    if (!active) {
      return
    }
    if (lineIndex < BOOT_LINES.length || progress < 100) {
      return
    }

    const timer = window.setTimeout(() => {
      onComplete()
    }, 600)

    return () => window.clearTimeout(timer)
  }, [active, lineIndex, onComplete, progress])

  const linesToRender = useMemo(() => BOOT_LINES.slice(0, lineIndex), [lineIndex])

  return (
    <AnimatePresence>
      {active ? (
        <motion.div
          key="boot-overlay"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.7 }}
          className="absolute inset-0 z-[80] flex flex-col bg-[#05070f]/95 backdrop-blur-sm"
        >
          <div className="boot-grid-overlay" />
          <div className="relative mx-auto mt-24 w-[min(940px,92vw)] rounded-2xl border border-cyan-400/40 bg-black/65 p-6 shadow-[0_0_60px_rgba(45,220,255,0.2)]">
            <p className="font-mono text-xs uppercase tracking-[0.34em] text-cyan-300">System Boot Sequence</p>
            <div className="mt-5 h-72 overflow-hidden rounded-xl border border-cyan-500/30 bg-[#040814] p-4 font-mono text-sm leading-6 text-[#7ff4ff]">
              {linesToRender.map((line, index) => (
                <div key={`${line}-${index}`} className="animate-typewriter whitespace-pre">
                  <span className="text-cyan-200">&gt; </span>
                  {line}
                </div>
              ))}
              {lineIndex < BOOT_LINES.length ? <span className="terminal-cursor">_</span> : null}
            </div>

            <div className="mt-5 rounded-xl border border-cyan-400/20 bg-[#03111f] p-4">
              <div className="mb-2 flex items-center justify-between font-mono text-xs uppercase tracking-[0.2em] text-cyan-200/80">
                <span>Neural Runtime Load</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-cyan-400/15">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-emerald-300 to-cyan-500"
                  animate={{ width: `${progress}%` }}
                  transition={{ ease: 'easeOut', duration: 0.2 }}
                />
              </div>
            </div>
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}
