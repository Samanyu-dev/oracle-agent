import { motion } from 'framer-motion'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#050816] text-white">
      <section className="relative overflow-hidden px-6 py-20 md:px-16">
        <div className="mx-auto max-w-6xl">
          <div className="mb-14 space-y-6">
            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl font-semibold tracking-tight text-white md:text-6xl"
            >
              Oracle Agent
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.8 }}
              className="max-w-2xl text-xl text-slate-300"
            >
              A cinematic AI simulation platform for autonomous survival planning,
              belief-driven decision making, and hazard navigation.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="flex flex-col gap-4 sm:flex-row"
            >
              <a
                href="#experience"
                className="inline-flex rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500 px-8 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/30 transition hover:scale-[1.02]"
              >
                Launch Simulation
              </a>
              <a
                href="#research"
                className="inline-flex items-center rounded-full border border-slate-700 px-8 py-3 text-sm font-semibold text-slate-200 transition hover:border-slate-500"
              >
                Research Playground
              </a>
            </motion.div>
          </div>

          <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/20"
            >
              <div className="space-y-4">
                <div className="rounded-3xl bg-gradient-to-r from-indigo-600 via-sky-500 to-emerald-400 p-1">
                  <div className="rounded-3xl bg-[#040b1f] p-6">
                    <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Command Console</p>
                    <div className="mt-6 grid gap-4 text-slate-300 sm:grid-cols-2">
                      <div className="rounded-2xl bg-slate-900/80 p-4">
                        <p className="text-xs uppercase text-slate-500">Mission</p>
                        <p className="mt-2 font-semibold text-white">Probe Hazard Grid</p>
                      </div>
                      <div className="rounded-2xl bg-slate-900/80 p-4">
                        <p className="text-xs uppercase text-slate-500">Agent</p>
                        <p className="mt-2 font-semibold text-white">Probabilistic Oracle</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-2xl shadow-slate-950/20"
            >
              <div className="space-y-4">
                <div className="rounded-3xl border border-slate-800 bg-[#020615] p-5">
                  <h2 className="text-xl font-semibold text-white">Live AI Metrics</h2>
                  <div className="mt-6 grid gap-4 sm:grid-cols-2">
                    <div className="rounded-2xl bg-slate-900/80 p-4">
                      <p className="text-sm uppercase text-slate-500">Success</p>
                      <p className="mt-2 text-3xl font-semibold text-cyan-300">98%</p>
                    </div>
                    <div className="rounded-2xl bg-slate-900/80 p-4">
                      <p className="text-sm uppercase text-slate-500">Entropy</p>
                      <p className="mt-2 text-3xl font-semibold text-violet-300">1.24</p>
                    </div>
                  </div>
                </div>
                <div className="rounded-3xl border border-slate-800 bg-[#020615] p-5">
                  <p className="text-sm uppercase tracking-[0.24em] text-slate-500">AI Brain Viewer</p>
                  <div className="mt-5 h-56 rounded-3xl bg-gradient-to-br from-slate-900 via-slate-950 to-slate-800 p-4 text-slate-400">
                    <p className="text-sm">Belief map, hazard heatmap, and MCTS planning layers will render here.</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <section id="experience" className="border-t border-slate-800 bg-[#050816] px-6 py-20 md:px-16">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-semibold text-white">Cinematic Experience</h2>
          <div className="mt-10 grid gap-6 lg:grid-cols-3">
            {[
              { title: 'Fog of War', description: 'Hidden terrain, uncertainty reveal, and tactical scanning.' },
              { title: 'AI Brain Viewer', description: 'Bayesian confidence, entropy, and belief overlay in real time.' },
              { title: 'MCTS Theater', description: 'Rollout futures, search branches, and decision timelines.' },
            ].map((item) => (
              <motion.div
                key={item.title}
                whileHover={{ y: -8 }}
                className="rounded-3xl border border-slate-800 bg-slate-950/85 p-6 shadow-xl shadow-slate-950/10"
              >
                <h3 className="text-xl font-semibold text-white">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-400">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="research" className="px-6 py-20 text-white md:px-16">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-semibold">Research Playground</h2>
          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6">
              <p className="text-lg font-semibold text-cyan-300">Hugging Face Space</p>
              <ul className="mt-4 space-y-3 text-slate-300">
                <li>• Parameter tuning and environment editing</li>
                <li>• Algorithm comparison and benchmark playback</li>
                <li>• Reproducible simulation controls</li>
              </ul>
            </div>
            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6">
              <p className="text-lg font-semibold text-violet-300">Backend API</p>
              <ul className="mt-4 space-y-3 text-slate-300">
                <li>• Live simulation sessions</li>
                <li>• Manual action control</li>
                <li>• Belief state and metrics serialization</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
