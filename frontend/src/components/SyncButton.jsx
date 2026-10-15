import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { wooApi } from '../api'
import { errorMessage } from '../api/client'

/** Runs a full WooCommerce sync and reports the outcome in a small popover. */
export default function SyncButton({ onDone }) {
  const [state, setState] = useState({ busy: false, message: null, ok: true })

  async function run() {
    setState({ busy: true, message: null, ok: true })
    try {
      const res = await wooApi.sync('all')
      const r = res.results
      setState({ busy: false, ok: true, message: `Synced ${r.products.total} products, ${r.customers.total} customers, ${r.orders.total} orders.` })
      onDone?.()
    } catch (err) {
      setState({ busy: false, ok: false, message: errorMessage(err) })
    }
  }

  return (
    <div className="relative">
      <button className="btn-primary" onClick={run} disabled={state.busy}>
        <svg className={`h-4 w-4 ${state.busy ? 'animate-spin' : ''}`} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
          <path d="M16 10a6 6 0 1 1-1.8-4.3M16 3v4h-4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        {state.busy ? 'Syncing…' : 'Sync WooCommerce'}
      </button>
      <AnimatePresence>
        {state.message && (
          <motion.div
            role={state.ok ? 'status' : 'alert'}
            initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className={`absolute right-0 top-full z-20 mt-2 w-72 rounded-md border bg-white p-3 text-sm shadow-lg ${state.ok ? 'border-teal/40' : 'border-rose/40 text-rose'}`}
          >
            {state.message}
            <button className="ml-2 text-xs text-muted underline" onClick={() => setState((s) => ({ ...s, message: null }))}>Dismiss</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
