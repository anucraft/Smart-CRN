import { Bar, Line } from 'react-chartjs-2'
import { baseOptions, COLORS } from './chartSetup'
import { compactMoney, monthLabel } from '../../utils/format'

export function RevenueBars({ items, height = 280 }) {
  const data = {
    labels: items.map((i) => monthLabel(i.month)),
    datasets: [{ label: 'Revenue', data: items.map((i) => i.revenue), backgroundColor: COLORS.teal, borderRadius: 3 }],
  }
  return (
    <div style={{ height }} role="img" aria-label="Monthly revenue bar chart">
      <Bar data={data} options={baseOptions((v) => compactMoney(v))} />
    </div>
  )
}

export function OrdersLine({ items, height = 240 }) {
  const data = {
    labels: items.map((i) => monthLabel(i.month)),
    datasets: [{ label: 'Orders', data: items.map((i) => i.orders), borderColor: COLORS.sky, backgroundColor: 'rgba(45,106,159,0.1)', fill: true, tension: 0.3, pointRadius: 3 }],
  }
  return (
    <div style={{ height }} role="img" aria-label="Monthly orders line chart">
      <Line data={data} options={baseOptions()} />
    </div>
  )
}

export function GrowthLine({ items, height = 240 }) {
  const data = {
    labels: items.map((i) => monthLabel(i.month)),
    datasets: [{ label: 'Customers', data: items.map((i) => i.total_customers), borderColor: COLORS.amber, backgroundColor: 'rgba(183,121,31,0.1)', fill: true, tension: 0.3, pointRadius: 3 }],
  }
  return (
    <div style={{ height }} role="img" aria-label="Customer growth line chart">
      <Line data={data} options={baseOptions()} />
    </div>
  )
}

export function TopCustomersBars({ items, height = 240 }) {
  const data = {
    labels: items.map((i) => i.name),
    datasets: [{ label: 'Spent', data: items.map((i) => i.total_spent), backgroundColor: COLORS.teal, borderRadius: 3 }],
  }
  const options = { ...baseOptions((v) => compactMoney(v)), indexAxis: 'y' }
  options.scales = { x: { beginAtZero: true, grid: { color: '#e6eaed' }, ticks: { callback: (v) => compactMoney(v) } }, y: { grid: { display: false } } }
  return (
    <div style={{ height }} role="img" aria-label="Top customers by spend bar chart">
      <Bar data={data} options={options} />
    </div>
  )
}
