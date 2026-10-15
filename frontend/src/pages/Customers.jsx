import { useState } from 'react'
import { Link, useOutletContext } from 'react-router-dom'
import { customersApi } from '../api'
import { Badge, EmptyState, ErrorState, Loading, PageHeader, Pagination } from '../components/ui'
import { useDebounce } from '../hooks/useDebounce'
import { useFetch } from '../hooks/useFetch'
import { formatDate, money } from '../utils/format'

const SEGMENTS = [
  ['', 'All customers'], ['vip', 'VIP'], ['returning', 'Returning'], ['new', 'New (1 order)'], ['prospect', 'No orders yet'],
]
const SORTS = [['newest', 'Newest first'], ['spent', 'Highest spend'], ['orders', 'Most orders'], ['name', 'Name A–Z']]

export default function Customers() {
  const { syncVersion } = useOutletContext()
  const [q, setQ] = useState('')
  const [segment, setSegment] = useState('')
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(1)
  const search = useDebounce(q)

  const { data, loading, error, reload } = useFetch(
    () => customersApi.list({ q: search || undefined, segment: segment || undefined, sort, page, per_page: 10 }),
    [search, segment, sort, page, syncVersion],
  )

  return (
    <>
      <PageHeader title="Customers" subtitle="Everyone who has shopped or registered at your store." />
      <div className="panel">
        <div className="flex flex-wrap gap-3 border-b border-line p-4">
          <div className="min-w-56 flex-1">
            <label htmlFor="q" className="sr-only">Search customers</label>
            <input id="q" className="input" placeholder="Search by name, email, phone or city" value={q} onChange={(e) => { setQ(e.target.value); setPage(1) }} />
          </div>
          <label className="sr-only" htmlFor="segment">Segment</label>
          <select id="segment" className="input w-auto" value={segment} onChange={(e) => { setSegment(e.target.value); setPage(1) }}>
            {SEGMENTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <label className="sr-only" htmlFor="sort">Sort</label>
          <select id="sort" className="input w-auto" value={sort} onChange={(e) => { setSort(e.target.value); setPage(1) }}>
            {SORTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </div>

        {loading && !data && <Loading />}
        {error && <div className="p-4"><ErrorState message={error} onRetry={reload} /></div>}
        {data && data.items.length === 0 && (
          <EmptyState title="No customers match" hint={q || segment ? 'Try a different search or clear the filter.' : 'Run a sync to import customers from WooCommerce.'} />
        )}
        {data && data.items.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead><tr>
                <th className="th">Customer</th><th className="th">Location</th><th className="th">Segment</th>
                <th className="th text-right">Orders</th><th className="th text-right">Total spent</th><th className="th">Joined</th>
              </tr></thead>
              <tbody>
                {data.items.map((c) => (
                  <tr key={c.id} className="hover:bg-paper/60">
                    <td className="td">
                      <Link to={`/customers/${c.id}`} className="font-medium text-ink hover:text-teal-dark hover:underline">{c.name}</Link>
                      <p className="text-xs text-muted">{c.email}</p>
                    </td>
                    <td className="td text-muted">{[c.city, c.country].filter(Boolean).join(', ') || '—'}</td>
                    <td className="td"><Badge value={c.segment} /></td>
                    <td className="td text-right tabular-nums">{c.orders_count}</td>
                    <td className="td text-right tabular-nums">{money(c.total_spent)}</td>
                    <td className="td text-muted">{formatDate(c.created_at)}</td>
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
