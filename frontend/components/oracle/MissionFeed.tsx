'use client'

import { MissionEvent } from '@/lib/oracle-types'

interface MissionFeedProps {
  feed: MissionEvent[]
  loading: boolean
}

function levelClass(level: MissionEvent['level']): string {
  if (level === 'critical') {
    return 'feed-critical'
  }
  if (level === 'warn') {
    return 'feed-warn'
  }
  if (level === 'success') {
    return 'feed-success'
  }
  return 'feed-info'
}

function formatTime(timestamp: number): string {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function MissionFeed({ feed, loading }: MissionFeedProps) {
  return (
    <section className="panel-shell relative mt-3 flex h-[210px] flex-col overflow-hidden p-3 md:h-[230px]">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="panel-title">Mission Feed</p>
          <p className="panel-subtitle">Live command log with tactical signal events.</p>
        </div>
        {loading ? <span className="text-xs uppercase tracking-[0.14em] text-cyan-300/70">Syncing...</span> : null}
      </div>

      <div className="feed-scanline" />

      <div className="relative flex-1 overflow-auto pr-1">
        <div className="flex flex-col gap-2">
          {feed.map((event, index) => (
            <article
              key={event.id}
              className={`feed-entry ${levelClass(event.level)} ${index === 0 ? 'feed-entry-new' : ''}`}
            >
              <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-cyan-100/60">
                <span>{event.code}</span>
                <span>{formatTime(event.timestamp)}</span>
              </div>
              <p className="mt-1 text-xs leading-5 text-cyan-50/85">{event.message}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
