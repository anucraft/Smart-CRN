import { Link, useOutletContext } from 'react-router-dom'
import { analyticsApi, wooApi } from '../api'
import { RevenueBars } from '../components/charts/Charts'
import SyncButton from '../components/SyncButton'
import { EmptyState, ErrorState, Loading, PageHeader } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import { formatDateTime, money } from '../utils/format'

function StatStrip({ s }) {
  const items = [
    { label: 'Customers', value: s.total_customers.toLocaleString() },
    { label: 'Orders', value: s.total_orders.toLocaleString() },
    { label: 'Revenue', value: money(s.revenue) },
    { label: 'Pending orders', value: s.pending_orders.toLocaleString(), note: 'Awaiting payment or fulfilment' },
    { label: 'Average order', value: money(s.average_order_value) },
  ]
  return (
    <dl className="panel grid grid-cols-2 divide-line sm:grid-cols-3 lg:grid-cols-5 lg:divide-x">
      {items.map((i) => (
        <div key={i.label} className="border-b border-line p-5 last:border-b-0 lg:border-b-0">
          <dt className="text-sm text-muted">{i.label}</dt>
          <dd className="mt-1 font-display text-2xl font-bold text-ink">{i.value}</dd>
          {i.note && <p className="mt-0.5 text-xs text-muted">{i.note}</p>}
        </div>
      ))}
    </dl>
  )
}

export default function Dashboard() {
  const { syncVersion } = useOutletContext()
  const summary = useFetch(analyticsApi.summary, [syncVersion])
  const sales = useFetch(() => analyticsApi.monthlySales(12), [syncVersion])
  const activity = useFetch(() => analyticsApi.recentActivity(10), [syncVersion])
  const status = useFetch(wooApi.status, [syncVersion])

  const empty = summary.data && summary.data.total_orders === 0 && summary.data.total_customers === 0

  return (
    <>
      <PageHeader title="Dashboard" subtitle={status.data?.last_sync ? `Last synced ${formatDateTime(status.data.last_sync.finished_at)}` : 'Not synced yet'} />

      {summary.loading && <Loading />}
      {summary.error && <ErrorState message={summary.error} onRetry={summary.reload} />}

      {empty && (
        <div className="panel">
          <EmptyState
            title="Your CRM is empty"
            hint={status.data?.configured ? 'Run your first sync to pull customers, products and orders from WooCommerce.' : 'Connect your WooCommerce store in Settings, then run a sync.'}
            action={status.data?.configured ? <SyncButton /> : <Link className="btn-primary" to="/settings">Connect store</Link>}
          />
        </div>
      )}

      {summary.data && !empty && (
        <div className="space-y-6">
          <StatStrip s={summary.data} />
          <div className="grid gap-6 xl:grid-cols-[1.7fr_1fr]">
            <section className="panel p-5">
              <h2 className="mb-4 text-lg font-bold">Monthly sales</h2>
              {sales.loading ? <Loading /> : sales.error ? <ErrorState message={sales.error} /> : <RevenueBars items={sales.data.items} />}
            </section>

            <section className="panel">
              <h2 className="px-5 pt-5 text-lg font-bold">Recent activity</h2>
              {activity.loading ? <Loading /> : activity.error ? <ErrorState message={activity.error} /> : (
                <ul className="mt-3 divide-y divide-line/70">
                  {activity.data.items.length === 0 && <li className="p-5 text-sm text-muted">Nothing has happened yet.</li>}
                  {activity.data.items.map((a) => (
                    <li key={a.id} className="px-5 py-3 text-sm">
                      <p>
                        {a.customer_id ? <Link className="font-medium text-teal-dark hover:underline" to={`/customers/${a.customer_id}`}>{a.customer_name}</Link> : null}
                        {a.customer_id ? ' · ' : ''}{a.description}
                      </p>
                      <p className="mt-0.5 text-xs text-muted">{formatDateTime(a.created_at)}</p>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        </div>
      )}
    </>
  )
}
