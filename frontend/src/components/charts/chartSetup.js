import {
  BarElement, CategoryScale, Chart as ChartJS, Filler, Legend, LineElement, LinearScale, PointElement, Tooltip,
} from 'chart.js'

// Chart.js is tree-shakeable: register only what we draw.
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend, Filler)
ChartJS.defaults.font.family = '"Public Sans", system-ui, sans-serif'
ChartJS.defaults.color = '#5b6874'

export const COLORS = { teal: '#0e7c6b', tealSoft: 'rgba(14,124,107,0.12)', amber: '#b7791f', sky: '#2d6a9f' }

export const baseOptions = (yFormatter) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, grid: { color: '#e6eaed' }, ticks: yFormatter ? { callback: yFormatter } : {} },
  },
})
