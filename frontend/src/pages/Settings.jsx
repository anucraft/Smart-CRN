import { useState } from 'react'
import { useOutletContext } from 'react-router-dom'
import { settingsApi, wooApi } from '../api'
import { errorMessage } from '../api/client'
import { ErrorState, Loading, PageHeader } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import { formatDateTime, humanize } from '../utils/format'

function Message({ m }) {
  if (!m) return null
  return <p role={m.ok ? 'status' : 'alert'} className={`mt-3 rounded-md border px-3 py-2 text-sm ${m.ok ? 'border-teal/40 bg-teal/5 text-teal-dark' : 'border-rose/40 bg-rose/5 text-rose'}`}>{m.text}</p>
}

export default function Settings() {
  const outlet = useOutletContext()
  const settings = useFetch(settingsApi.get, [])
  const status = useFetch(wooApi.status, [outlet.syncVersion])
  const [form, setForm] = useState({ store_url: null, consumer_key: '', consumer_secret: '', webhook_secret: '' })
  const [saveMsg, setSaveMsg] = useState(null)
  const [testMsg, setTestMsg] = useState(null)
  const [syncMsg, setSyncMsg] = useState(null)
  const [busy, setBusy] = useState('')
  const [copied, setCopied] = useState(false)

  if (settings.loading && !settings.data) return <Loading />
  if (settings.error) return <ErrorState message={settings.error} onRetry={settings.reload} />
  const s = settings.data
  // store_url is null until the user edits it, so the saved value shows without copying it into state
  const storeUrl = form.store_url ?? s.store_url
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  async function save(e) {
    e.preventDefault()
    setBusy('save'); setSaveMsg(null)
    try {
      await settingsApi.update({ ...form, store_url: storeUrl })
      settings.reload(); status.reload()
      setForm({ store_url: null, consumer_key: '', consumer_secret: '', webhook_secret: '' })
      setSaveMsg({ ok: true, text: 'Settings saved.' })
    } catch (err) { setSaveMsg({ ok: false, text: errorMessage(err) }) } finally { setBusy('') }
  }

  async function test() {
    setBusy('test'); setTestMsg(null)
    try { setTestMsg({ ok: true, text: (await wooApi.test()).message }) }
    catch (err) { setTestMsg({ ok: false, text: errorMessage(err) }) } finally { setBusy('') }
  }

  async function sync(resource) {
    setBusy(resource); setSyncMsg(null)
    try {
      const res = await wooApi.sync(resource)
      const parts = Object.entries(res.results).map(([k, v]) => `${v.total} ${k} (${v.created} new, ${v.updated} updated)`)
      setSyncMsg({ ok: true, text: `Synced ${parts.join(', ')}.` })
      status.reload()
      outlet.refresh()
    } catch (err) { setSyncMsg({ ok: false, text: errorMessage(err) }) } finally { setBusy('') }
  }

  async function copy() {
    await navigator.clipboard.writeText(s.webhook_url)
    setCopied(true); setTimeout(() => setCopied(false), 1500)
  }

  return (
    <>
      <PageHeader title="Settings" subtitle="Connect your WooCommerce store and keep it in sync." />
      <div className="grid gap-6 xl:grid-cols-2">
        <form onSubmit={save} className="panel p-5">
          <h2 className="text-lg font-bold">WooCommerce connection</h2>
          <p className="mb-4 mt-1 text-sm text-muted">In WooCommerce go to Settings → Advanced → REST API → Add key, with Read permission.</p>

          <label htmlFor="store_url" className="label">Store URL</label>
          <input id="store_url" className="input mb-4" placeholder="https://yourstore.com" value={storeUrl} onChange={set('store_url')} />

          <label htmlFor="ck" className="label">Consumer key</label>
          <input id="ck" className="input mb-4" autoComplete="off" placeholder={s.consumer_key || 'ck_…'} value={form.consumer_key} onChange={set('consumer_key')} />

          <label htmlFor="cs" className="label">Consumer secret</label>
          <input id="cs" type="password" className="input mb-4" autoComplete="new-password" placeholder={s.has_consumer_secret ? 'Saved. Type to replace.' : 'cs_…'} value={form.consumer_secret} onChange={set('consumer_secret')} />

          <label htmlFor="ws" className="label">Webhook secret</label>
          <input id="ws" type="password" className="input" autoComplete="new-password" placeholder={s.has_webhook_secret ? 'Saved. Type to replace.' : 'Any long random string'} value={form.webhook_secret} onChange={set('webhook_secret')} />
          <p className="mb-4 mt-1 text-xs text-muted">Use the same secret when you create the webhooks in WooCommerce.</p>

          <div className="flex flex-wrap gap-2">
            <button className="btn-primary" disabled={busy === 'save'}>{busy === 'save' ? 'Saving…' : 'Save changes'}</button>
            <button type="button" className="btn-secondary" onClick={test} disabled={busy === 'test' || !s.configured}>{busy === 'test' ? 'Testing…' : 'Test connection'}</button>
          </div>
          <Message m={saveMsg} /><Message m={testMsg} />
        </form>

        <div className="space-y-6">
          <section className="panel p-5">
            <h2 className="text-lg font-bold">Manual sync</h2>
            <p className="mb-4 mt-1 text-sm text-muted">
              {status.data?.last_sync ? `Last sync ${formatDateTime(status.data.last_sync.finished_at)}.` : 'No sync yet.'} Webhooks keep things current; use this for first-time import or to catch up.
            </p>
            <div className="flex flex-wrap gap-2">
              {['all', 'products', 'customers', 'orders'].map((r) => (
                <button key={r} className={r === 'all' ? 'btn-primary' : 'btn-secondary'} onClick={() => sync(r)} disabled={!!busy || !s.configured}>
                  {busy === r ? 'Syncing…' : r === 'all' ? 'Sync everything' : `Sync ${humanize(r).toLowerCase()}`}
                </button>
              ))}
            </div>
            {!s.configured && <p className="mt-3 text-sm text-amber">Save your store URL and API keys first.</p>}
            <Message m={syncMsg} />
            {status.data && <p className="mt-4 text-xs text-muted">In this CRM: {status.data.counts.customers} customers · {status.data.counts.orders} orders · {status.data.counts.products} products</p>}
          </section>

          <section className="panel p-5">
            <h2 className="text-lg font-bold">Webhooks</h2>
            <p className="mb-3 mt-1 text-sm text-muted">In WooCommerce go to Settings → Advanced → Webhooks. Create one webhook each for these topics, with this delivery URL and your webhook secret:</p>
            <div className="flex gap-2">
              <input readOnly aria-label="Webhook delivery URL" className="input font-mono text-xs" value={s.webhook_url} onFocus={(e) => e.target.select()} />
              <button className="btn-secondary" onClick={copy}>{copied ? 'Copied' : 'Copy'}</button>
            </div>
            <p className="mt-3 text-sm text-muted">Order created, Order updated, Customer created, Customer updated, Product created, Product updated.</p>
            <p className="mt-2 text-xs text-muted">WooCommerce can't reach localhost. For local testing use a tunnel such as ngrok.</p>
          </section>
        </div>
      </div>
    </>
  )
}
