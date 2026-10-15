import { useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import SyncButton from './SyncButton'

const NAV = [
  { to: '/', label: 'Dashboard', end: true, d: 'M3 10.5 10 4l7 6.5V17a1 1 0 0 1-1 1h-3.5v-5h-5v5H4a1 1 0 0 1-1-1v-6.5Z' },
  { to: '/customers', label: 'Customers', d: 'M10 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm-6 8a6 6 0 0 1 12 0' },
  { to: '/orders', label: 'Orders', d: 'M4 5h12l-1 9H5L4 5Zm0 0-.5-2H2m5 14.5h.01M13 17.5h.01' },
  { to: '/products', label: 'Products', d: 'M3 6.5 10 3l7 3.5v7L10 17l-7-3.5v-7Zm7 3.5 7-3.5M10 10v7M10 10 3 6.5' },
  { to: '/analytics', label: 'Analytics', d: 'M4 16V9m4 7V4m4 12v-5m4 5V7' },
  { to: '/settings', label: 'Settings', d: 'M10 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Zm0-9.5 1 2 2.2-.6.8 2.1 2 1-.9 2 .9 2-2 1-.8 2.1-2.2-.6-1 2-1-2-2.2.6-.8-2.1-2-1 .9-2-.9-2 2-1 .8-2.1L9 5l1-2Z' },
]

function Icon({ d }) {
  return (
    <svg className="h-[18px] w-[18px] shrink-0" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  )
}

export default function Layout() {
  const { admin, logout } = useAuth()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  // Bumped after every sync so pages can refetch their data.
  const [syncVersion, setSyncVersion] = useState(0)

  return (
    <div className="flex min-h-full">
      {/* Navigation rail */}
      <aside className={`fixed inset-y-0 left-0 z-30 flex w-60 flex-col bg-ink text-white transition-transform lg:static lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center gap-2.5 px-5 py-5">
          <img src="/favicon.svg" alt="" className="h-8 w-8" />
          <span className="font-display text-lg font-bold">SmartCRM</span>
        </div>
        <nav className="flex-1 space-y-0.5 px-3" aria-label="Main">
          {NAV.map((item) => (
            <NavLink
              key={item.to} to={item.to} end={item.end} onClick={() => setOpen(false)}
              className={({ isActive }) => `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${isActive ? 'bg-ink-soft text-mint font-medium' : 'text-white/70 hover:bg-ink-soft hover:text-white'}`}
            >
              <Icon d={item.d} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-white/10 p-4 text-sm">
          <p className="truncate font-medium">{admin?.name}</p>
          <p className="truncate text-xs text-white/60">{admin?.email}</p>
          <button onClick={logout} className="mt-3 text-xs text-white/70 underline hover:text-white">Log out</button>
        </div>
      </aside>
      {open && <div className="fixed inset-0 z-20 bg-ink/50 lg:hidden" onClick={() => setOpen(false)} aria-hidden="true" />}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-3 border-b border-line bg-white px-4 py-3 sm:px-8">
          <button className="btn-secondary lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu">Menu</button>
          <p className="hidden text-sm text-muted lg:block">Customers and orders mirrored from your WooCommerce store</p>
          <SyncButton onDone={() => setSyncVersion((v) => v + 1)} />
        </header>
        <main className="flex-1 px-4 py-6 sm:px-8">
          {/* Soft fade between pages (the only page-level motion) */}
          <motion.div key={location.pathname} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.18 }}>
            <Outlet context={{ syncVersion, refresh: () => setSyncVersion((v) => v + 1) }} />
          </motion.div>
        </main>
      </div>
    </div>
  )
}
