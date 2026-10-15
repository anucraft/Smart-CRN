import { useState } from 'react'
import { Link, useOutletContext, useParams } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { customersApi } from '../api'
import { errorMessage } from '../api/client'
import { Badge, EmptyState, ErrorState, Loading } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import { formatDate, formatDateTime, humanize, money } from '../utils/format'

function Notes({ customerId, onChange }) {
  const notes = useFetch(() => customersApi.notes(customerId), [customerId])
  const [body, setBody] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function add(e) {
    e.preventDefault()
    if (!body.trim()) return
    setBusy(true)
    setError('')
    try {
      await customersApi.addNote(customerId, body)
      setBody('')
      notes.reload()
      onChange()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  async function remove(id) {
    try {
      await customersApi.deleteNote(customerId, id)
      notes.reload()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <section className="panel p-5">
      <h2 className="text-lg font-bold">Notes</h2>
      <p className="mb-3 text-sm text-muted">Private to your team. Never sent to WooCommerce.</p>
      <form onSubmit={add}>
        <label htmlFor="note" className="sr-only">New note</label>
        <textarea id="note" rows={3} maxLength={2000} className="input" placeholder="e.g. Prefers email over phone. Asked about bulk pricing." value={body} onChange={(e) => setBody(e.target.value)} />
        <div className="mt-2 flex items-center justify-between">
          <span className="text-xs text-rose" role="alert">{error}</span>
          <button className="btn-primary" disabled={busy || !body.trim()}>{busy ? 'Saving…' : 'Add note'}</button>
        </div>
      </form>
      {notes.loading && !notes.data && <Loading />}
      <ul className="mt-4 space-y-3">
        <AnimatePresence initial={false}>
          {notes.data?.items.map((n) => (
            <motion.li key={n.id} layout initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
              <div className="rounded-md border border-line bg-paper/50 p-3 text-sm">
                <p className="whitespace-pre-wrap">{n.body}</p>
                <div className="mt-2 flex items-center justify-between text-xs text-muted">
                  <span>{n.author} · {formatDateTime(n.created_at)}</span>
                  <button className="btn-danger !px-2 !py-1 text-xs" onClick={() => remove(n.id)}>Delete</button>
                </div>
              </div>
            </motion.li>
          ))}
        </AnimatePresence>
      </ul>
    </section>
  )
}

export default function CustomerDetail() {
  const { id } = useParams()
  const { syncVersion } = useOutletContext()
  const customer = useFetch(() => customersApi.get(id), [id, syncVersion])
  const timeline = useFetch(() => customersApi.timeline(id), [id, syncVersion])

  if (customer.loading && !customer.data) return <Loading />
  if (customer.error) return <ErrorState message={customer.error} onRetry={customer.reload} />
  const c = customer.data

  return (
    <>
      <Link to="/customers" className="text-sm text-muted hover:text-ink hover:underline">← All customers</Link>
      <div className="mb-6 mt-2 flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold">{c.name}</h1>
        <Badge value={c.segment} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <div className="space-y-6">
          <dl className="panel grid grid-cols-2 gap-px bg-line sm:grid-cols-4 [&>div]:bg-white [&>div]:p-4">
            <div><dt className="text-sm text-muted">Total spent</dt><dd className="font-display text-xl font-bold">{money(c.total_spent)}</dd></div>
            <div><dt className="text-sm text-muted">Orders</dt><dd className="font-display text-xl font-bold">{c.orders_count}</dd></div>
            <div><dt className="text-sm text-muted">Last order</dt><dd className="font-medium">{formatDate(c.last_order_at)}</dd></div>
            <div><dt className="text-sm text-muted">Customer since</dt><dd className="font-medium">{formatDate(c.created_at)}</dd></div>
          </dl>

          <section className="panel p-5">
            <h2 className="mb-3 text-lg font-bold">Contact</h2>
            <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
              <div><dt className="text-muted">Email</dt><dd>{c.email || '—'}</dd></div>
              <div><dt className="text-muted">Phone</dt><dd>{c.phone || '—'}</dd></div>
              <div className="sm:col-span-2"><dt className="text-muted">Address</dt><dd>{[c.address, c.city, c.state, c.country].filter(Boolean).join(', ') || '—'}</dd></div>
            </dl>
          </section>

          <section className="panel">
            <h2 className="px-5 pt-5 text-lg font-bold">Recent orders</h2>
            {c.recent_orders.length === 0 ? <EmptyState title="No orders yet" hint="This customer hasn't placed an order." /> : (
              <div className="mt-3 overflow-x-auto">
                <table className="w-full">
                  <thead><tr><th className="th">Order</th><th className="th">Date</th><th className="th">Status</th><th className="th text-right">Total</th></tr></thead>
                  <tbody>
                    {c.recent_orders.map((o) => (
                      <tr key={o.id} className="hover:bg-paper/60">
                        <td className="td"><Link className="font-medium text-teal-dark hover:underline" to={`/orders/${o.id}`}>#{o.number}</Link></td>
                        <td className="td text-muted">{formatDate(o.date_created)}</td>
                        <td className="td"><Badge value={o.status} /></td>
                        <td className="td text-right tabular-nums">{money(o.total, o.currency)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <Notes customerId={id} onChange={timeline.reload} />
        </div>

        <section className="panel h-fit p-5">
          <h2 className="mb-4 text-lg font-bold">Timeline</h2>
          {timeline.loading && !timeline.data && <Loading />}
          {timeline.error && <ErrorState message={timeline.error} />}
          {timeline.data?.items.length === 0 && <p className="text-sm text-muted">No activity recorded yet.</p>}
          <ol className="relative ml-2 space-y-5 border-l border-line pl-5">
            {timeline.data?.items.map((a) => (
              <li key={a.id} className="relative text-sm">
                <span className="absolute -left-[26px] top-1.5 h-2 w-2 rounded-full bg-teal" aria-hidden="true" />
                <p>{a.description}</p>
                <p className="text-xs text-muted">{humanize(a.type.split('.')[0])} · {formatDateTime(a.created_at)}</p>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </>
  )
}
