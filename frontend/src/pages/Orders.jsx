import { useState } from 'react'
import { Link, useOutletContext } from 'react-router-dom'
import { ordersApi } from '../api'
import { Badge, EmptyState, ErrorState, Loading, PageHeader, Pagination } from '../components/ui'
import { useDebounce } from '../hooks/useDebounce'
import { useFetch } from '../hooks/useFetch'
import { formatDate, money } from '../utils/format'

const STATUSES = ['pending', 'processing', 'on-hold', 'completed', 'cancelled', 'refunded', 'failed']

export default function Orders() {
  const { syncVersion } = useOutletContext()
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const search = useDebounce(q)

  const { data, loading, error, reload } = useFetch(
    () => ordersApi.list({ q: search || undefined, status: status || undefined, page, per_page: 10 }),
    [search, status, page, syncVersion],
  )

  return (
    <>
      <PageHeader title="Orders" subtitle="Payment and shipping status are worked out from each order's WooCommerce status." />
      <div className="panel">
        <div className="flex flex-wrap gap-3 border-b border-line p-4">
          <div className="min-w-56 flex-1">
            <label htmlFor="q" className="sr-only">Search orders</label>
            <input id="q" className="input" placeholder="Search by order number, customer name or email" value={q} onChange={(e) => { setQ(e.target.value); setPage(1) }} />
          </div>
          <label htmlFor="status" className="sr-only">Status</label>
          <select id="status" className="input w-auto" value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }}>
            <option value="">All statuses</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s[0].toUpperCase() + s.slice(1)}</option>)}
          </select>
        </div>

        {loading && !data && <Loading />}
        {error && <div className="p-4"><ErrorState message={error} onRetry={reload} /></div>}
        {data && data.items.length === 0 && <EmptyState title="No orders found" hint={q || status ? 'Try a different search or status.' : 'Run a sync to import orders from WooCommerce.'} />}
        {data && data.items.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead><tr>
                <th className="th">Order</th><th className="th">Date</th><th className="th">Customer</th><th className="th">Status</th>
                <th className="th">Payment</th><th className="th">Shipping</th><th className="th text-right">Total</th>
              </tr></thead>
              <tbody>
                {data.items.map((o) => (
                  <tr key={o.id} className="hover:bg-paper/60">
                    <td className="td"><Link className="font-medium text-teal-dark hover:underline" to={`/orders/${o.id}`}>#{o.number}</Link></td>
                    <td className="td text-muted">{formatDate(o.date_created)}</td>
                    <td className="td">{o.customer ? <Link className="hover:underline" to={`/customers/${o.customer.id}`}>{o.customer.name}</Link> : <span className="text-muted">Guest</span>}</td>
                    <td className="td"><Badge value={o.status} /></td>
                    <td className="td"><Badge value={o.payment_status} /></td>
                    <td className="td"><Badge value={o.shipping_status} /></td>
                    <td className="td text-right tabular-nums">{money(o.total, o.currency)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {data && <Pagination page={data.page} pages={data.pages} total={data.total} onChange={setPage} />}
      </div>
    </>
  )
}
