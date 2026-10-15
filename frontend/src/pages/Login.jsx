import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { errorMessage } from '../api/client'

export default function Login() {
  const { admin, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (admin) return <Navigate to={location.state?.from?.pathname || '/'} replace />

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await login(form.email, form.password)
      navigate(location.state?.from?.pathname || '/', { replace: true })
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid min-h-full lg:grid-cols-[1.1fr_1fr]">
      <section className="hidden flex-col justify-between bg-ink p-12 text-white lg:flex">
        <div className="flex items-center gap-2.5">
          <img src="/favicon.svg" alt="" className="h-9 w-9" />
          <span className="font-display text-xl font-bold">SmartCRM</span>
        </div>
        <div>
          <h1 className="max-w-md font-display text-4xl font-bold leading-tight !text-white">
            Every customer and order from your WooCommerce store, on one desk.
          </h1>
          <p className="mt-4 max-w-md text-white/70">
            Orders arrive by webhook as they happen. Look up a shopper, see their history, and leave notes for next time.
          </p>
        </div>
        <p className="text-xs text-white/50">Admin access only</p>
      </section>

      <section className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-sm" noValidate>
          <h2 className="text-2xl font-bold">Log in</h2>
          <p className="mb-6 mt-1 text-sm text-muted">Use the admin account created with the backend CLI.</p>

          {error && <p role="alert" className="mb-4 rounded-md border border-rose/40 bg-rose/5 px-3 py-2 text-sm text-rose">{error}</p>}

          <label htmlFor="email" className="label">Email</label>
          <input id="email" type="email" autoComplete="username" required className="input mb-4" value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })} />

          <label htmlFor="password" className="label">Password</label>
          <input id="password" type="password" autoComplete="current-password" required className="input mb-6" value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })} />

          <button className="btn-primary w-full" disabled={busy || !form.email || !form.password}>
            {busy ? 'Logging in…' : 'Log in'}
          </button>
        </form>
      </section>
    </div>
  )
}
