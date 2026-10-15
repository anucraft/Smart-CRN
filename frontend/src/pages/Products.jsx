import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { productsApi } from '../api'
import { Badge, EmptyState, ErrorState, Loading, PageHeader, Pagination } from '../components/ui'
import { useDebounce } from '../hooks/useDebounce'
import { useFetch } from '../hooks/useFetch'
import { money } from '../utils/format'

export default function Products() {
  const { syncVersion } = useOutletContext()
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const search = useDebounce(q)
  const { data, loading, error, reload } = useFetch(() => productsApi.list({ q: search || undefined, page, per_page: 12 }), [search, page, syncVersion])

  return (
    <>
      <PageHeader title="Products" subtitle="Your WooCommerce catalogue. Edit products in WooCommerce; changes appear here after a sync or webhook." />
      <div className="panel">
        <div className="border-b border-line p-4">
          <label htmlFor="q" className="sr-only">Search products</label>
          <input id="q" className="input max-w-md" placeholder="Search by name or SKU" value={q} onChange={(e) => { setQ(e.target.value); setPage(1) }} />
        </div>
        {loading && !data && <Loading />}
        {error && <div className="p-4"><ErrorState message={error} onRetry={reload} /></div>}
        {data && data.items.length === 0 && <EmptyState title="No products" hint="Run a sync to import your catalogue." />}
        {data && data.items.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead><tr><th className="th">Product</th><th className="th">SKU</th><th className="th">Categories</th><th className="th">Stock</th><th className="th text-right">Price</th></tr></thead>
              <tbody>
                {data.items.map((p) => (
                  <tr key={p.id}>
                    <td className="td">
                      <div className="flex items-center gap-3">
                        {p.image_url ? <img src={p.image_url} alt="" className="h-10 w-10 rounded object-cover" loading="lazy" /> : <div className="h-10 w-10 rounded bg-paper" aria-hidden="true" />}
                        <span className="font-medium">{p.name}</span>
                      </div>
                    </td>
                    <td className="td text-muted">{p.sku || '—'}</td>
                    <td className="td text-muted">{p.categories.join(', ') || '—'}</td>
                    <td className="td"><Badge value={p.stock_status} label={p.stock_quantity != null ? `${p.stock_quantity} in stock` : undefined} /></td>
                    <td className="td text-right tabular-nums">{money(p.price)}</td>
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
