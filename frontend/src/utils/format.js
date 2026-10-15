export const money = (n, currency = 'USD') =>
  new Intl.NumberFormat(undefined, { style: 'currency', currency, maximumFractionDigits: 2 }).format(n || 0)

export const compactMoney = (n) =>
  new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 1 }).format(n || 0)

// Backend sends naive UTC timestamps; append Z so the browser converts to local time.
const toDate = (iso) => (iso ? new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : iso + 'Z') : null)

export const formatDate = (iso) => {
  const d = toDate(iso)
  return d ? d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}

export const formatDateTime = (iso) => {
  const d = toDate(iso)
  return d ? d.toLocaleString(undefined, { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
}

export const monthLabel = (ym) => {
  const [y, m] = ym.split('-').map(Number)
  return new Date(y, m - 1, 1).toLocaleDateString(undefined, { month: 'short', year: '2-digit' })
}

export const humanize = (s) => (s || '').replace(/[_-]/g, ' ').replace(/^\w/, (c) => c.toUpperCase())
