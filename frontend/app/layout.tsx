import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Oracle Agent | Cinematic AI Simulation',
  description: 'A futuristic AI command center for autonomous survival planning.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
