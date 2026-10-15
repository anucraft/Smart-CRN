import { Link, useOutletContext } from 'react-router-dom'
import { analyticsApi } from '../api'
import { GrowthLine, OrdersLine, RevenueBars, TopCustomersBars } from '../components/charts/Charts'
import { ErrorState, Loading, PageHeader } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import { money } from '../utils/format'

function Panel({ title, note, state, children, className = '' }) {
  return (
    <section className={`panel p-5 ${className}`}>
      <h2 className="text-lg font-bold">{title}</h2>
      {note && <p className="mb-4 text-sm text-muted">{note}</p>}
      {state.loading && !state.data ? <Loading /> : state.error ? <ErrorState message={state.error} onRetry={state.reload} /> : children(state.data.items)}
    </section>
  )
}

export default function Analytics() {
  const { syncVersion } = useOutletContext()
  const sales = useFetch(() => analyticsApi.monthlySales(12), [syncVersion])
  const growth = useFetch(() => analyticsApi.customerGrowth(12), [syncVersion])
  const top = useFetch(() => analyticsApi.topCustomers(8), [syncVersion])

  return (
    <>
      <PageHeader title="Analytics" subtitle="The last 12 months. Revenue counts completed and processing orders." />
      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Revenue by month" state={sales} className="lg:col-span-2">{(items) => <RevenueBars items={items} height={300} />}</Panel>
        <Panel title="Orders per month" note="All orders placed, whatever their status." state={sales}>{(items) => <OrdersLine items={items} />}</Panel>
        <Panel title="Customer growth" note="Total customers at the end of each month." state={growth}>{(items) => <GrowthLine items={items} />}</Panel>
        <Panel title="Top customers" note="Ranked by money spent on completed and processing orders." state={top} className="lg:col-span-2">
          {(items) => items.length === 0 ? <p className="text-sm text-muted">No orders yet.</p> : (
            <div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
              <TopCustomersBars items={items} height={Math.max(200, items.length * 38)} />
              <table className="w-full self-start">
                <thead><tr><th className="th">Customer</th><th className="th text-right">Orders</th><th className="th text-right">Spent</th></tr></thead>
                <tbody>
                  {items.map((c) => (
                    <tr key={c.id}>
                      <td className="td"><Link className="font-medium hover:text-teal-dark hover:underline" to={`/customers/${c.id}`}>{c.name}</Link></td>
                      <td className="td text-right tabular-nums">{c.orders_count}</td>
                      <td className="td text-right tabular-nums">{money(c.total_spent)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>
      </div>
    </>
  )
}
