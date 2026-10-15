import { Link, useParams } from 'react-router-dom'
import { ordersApi } from '../api'
import { Badge, ErrorState, Loading } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import { formatDateTime, money } from '../utils/format'

function Address({ title, a }) {
  const lines = [[a.first_name, a.last_name].filter(Boolean).join(' '), a.company, a.address_1, a.address_2,
    [a.city, a.state, a.postcode].filter(Boolean).join(', '), a.country, a.email, a.phone].filter(Boolean)
  return (
    <section className="panel p-5">
      <h2 className="mb-2 text-lg font-bold">{title}</h2>
      {lines.length ? <address className="space-y-0.5 text-sm not-italic">{lines.map((l, i) => <p key={i}>{l}</p>)}</address> : <p className="text-sm text-muted">Not provided</p>}
    </section>
  )
}

export default function OrderDetail() {
  const { id } = useParams()
  const { data: o, loading, error, reload } = useFetch(() => ordersApi.get(id), [id])
  if (loading && !o) return <Loading />
  if (error) return <ErrorState message={error} onRetry={reload} />

  return (
    <>
      <Link to="/orders" className="text-sm text-muted hover:text-ink hover:underline">← All orders</Link>
      <div className="mb-6 mt-2 flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold">Order #{o.number}</h1>
        <Badge value={o.status} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <div className="space-y-6">
          <section className="panel">
            <h2 className="px-5 pt-5 text-lg font-bold">Items</h2>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full">
                <thead><tr><th className="th">Product</th><th className="th text-right">Price</th><th className="th text-right">Qty</th><th className="th text-right">Total</th></tr></thead>
                <tbody>
                  {o.items.map((i) => (
                    <tr key={i.id}>
                      <td className="td">{i.name}{i.sku && <span className="ml-2 text-xs text-muted">{i.sku}</span>}</td>
                      <td className="td text-right tabular-nums">{money(i.price, o.currency)}</td>
                      <td className="td text-right tabular-nums">{i.quantity}</td>
                      <td className="td text-right tabular-nums">{money(i.total, o.currency)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <dl className="ml-auto max-w-xs space-y-1 p-5 text-sm">
              <div className="flex justify-between"><dt className="text-muted">Shipping</dt><dd className="tabular-nums">{money(o.shipping_total, o.currency)}</dd></div>
              <div className="flex justify-between"><dt className="text-muted">Tax</dt><dd className="tabular-nums">{money(o.total_tax, o.currency)}</dd></div>
              {o.discount_total > 0 && <div className="flex justify-between"><dt className="text-muted">Discount</dt><dd className="tabular-nums">−{money(o.discount_total, o.currency)}</dd></div>}
              <div className="flex justify-between border-t border-line pt-2 font-display text-lg font-bold"><dt>Total</dt><dd className="tabular-nums">{money(o.total, o.currency)}</dd></div>
            </dl>
          </section>
          {o.customer_note && (
            <section className="panel p-5"><h2 className="mb-1 text-lg font-bold">Customer note</h2><p className="text-sm">{o.customer_note}</p></section>
          )}
        </div>

        <div className="space-y-6">
          <section className="panel p-5">
            <h2 className="mb-3 text-lg font-bold">Payment and shipping</h2>
            <dl className="space-y-2 text-sm">
              <div className="flex items-center justify-between"><dt className="text-muted">Payment</dt><dd><Badge value={o.payment_status} /></dd></div>
              <div className="flex items-center justify-between"><dt className="text-muted">Method</dt><dd>{o.payment_method || '—'}</dd></div>
              <div className="flex items-center justify-between"><dt className="text-muted">Shipping</dt><dd><Badge value={o.shipping_status} /></dd></div>
              <div className="flex items-center justify-between"><dt className="text-muted">Placed</dt><dd>{formatDateTime(o.date_created)}</dd></div>
              <div className="flex items-center justify-between"><dt className="text-muted">Paid</dt><dd>{formatDateTime(o.date_paid)}</dd></div>
              <div className="flex items-center justify-between"><dt className="text-muted">Completed</dt><dd>{formatDateTime(o.date_completed)}</dd></div>
            </dl>
          </section>
          <section className="panel p-5">
            <h2 className="mb-2 text-lg font-bold">Customer</h2>
            {o.customer ? (
              <p className="text-sm"><Link className="font-medium text-teal-dark hover:underline" to={`/customers/${o.customer.id}`}>{o.customer.name}</Link><br /><span className="text-muted">{o.customer.email}</span></p>
            ) : <p className="text-sm text-muted">Guest checkout with no email</p>}
          </section>
          <Address title="Billing address" a={o.billing} />
          <Address title="Shipping address" a={o.shipping} />
        </div>
      </div>
    </>
  )
}
