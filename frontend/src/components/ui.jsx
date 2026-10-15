import { humanize } from '../utils/format'

export function PageHeader({ title, subtitle, children }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-bold">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
      </div>
      {children && <div className="flex flex-wrap items-center gap-2">{children}</div>}
    </div>
  )
}

export function Loading({ label = 'Loading…' }) {
  return (
    <div role="status" className="flex items-center gap-3 p-6 text-sm text-muted">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-line border-t-teal" />
      {label}
    </div>
  )
}

export function ErrorState({ message, onRetry }) {
  return (
    <div role="alert" className="panel border-rose/40 p-5 text-sm">
      <p className="font-medium text-rose">{message}</p>
      {onRetry && <button className="btn-secondary mt-3" onClick={onRetry}>Try again</button>}
    </div>
  )
}

export function EmptyState({ title, hint, action }) {
  return (
    <div className="p-10 text-center">
      <p className="font-display text-lg font-medium text-ink">{title}</p>
      {hint && <p className="mx-auto mt-1 max-w-md text-sm text-muted">{hint}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

const TONES = {
  green: 'bg-teal/10 text-teal-dark',
  amber: 'bg-amber/10 text-amber',
  rose: 'bg-rose/10 text-rose',
  sky: 'bg-sky/10 text-sky',
  grey: 'bg-ink/5 text-muted',
}

const STATUS_TONE = {
  completed: 'green', paid: 'green', delivered: 'green', vip: 'green', publish: 'green', instock: 'green',
  processing: 'sky', to_ship: 'sky', returning: 'sky', new: 'sky',
  pending: 'amber', 'on-hold': 'amber', on_hold: 'amber', awaiting_payment: 'amber', onbackorder: 'amber',
  failed: 'rose', refunded: 'rose', cancelled: 'rose', outofstock: 'rose',
  prospect: 'grey', not_applicable: 'grey', draft: 'grey',
}

export function Badge({ value, label }) {
  const tone = TONES[STATUS_TONE[value] || 'grey']
  return (
    <span className={`inline-block whitespace-nowrap rounded px-2 py-0.5 text-xs font-medium ${tone}`}>
      {label || humanize(value)}
    </span>
  )
}

export function Pagination({ page, pages, total, onChange }) {
  if (!pages || pages <= 1) return total ? <p className="px-4 py-3 text-xs text-muted">{total} total</p> : null
  return (
    <div className="flex items-center justify-between border-t border-line px-4 py-3 text-sm">
      <span className="text-muted">Page {page} of {pages} · {total} total</span>
      <div className="flex gap-2">
        <button className="btn-secondary" disabled={page <= 1} onClick={() => onChange(page - 1)}>Previous</button>
        <button className="btn-secondary" disabled={page >= pages} onClick={() => onChange(page + 1)}>Next</button>
      </div>
    </div>
  )
}
