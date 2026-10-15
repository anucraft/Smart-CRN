import api from './client'

const get = (url, params) => api.get(url, { params }).then((r) => r.data)

export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }).then((r) => r.data),
  me: () => get('/auth/me'),
}

export const customersApi = {
  list: (params) => get('/customers', params),
  get: (id) => get(`/customers/${id}`),
  timeline: (id) => get(`/customers/${id}/timeline`),
  notes: (id) => get(`/customers/${id}/notes`),
  addNote: (id, body) => api.post(`/customers/${id}/notes`, { body }).then((r) => r.data),
  deleteNote: (id, noteId) => api.delete(`/customers/${id}/notes/${noteId}`),
}

export const ordersApi = {
  list: (params) => get('/orders', params),
  get: (id) => get(`/orders/${id}`),
}

export const productsApi = { list: (params) => get('/products', params) }

export const analyticsApi = {
  summary: () => get('/analytics/summary'),
  monthlySales: (months = 12) => get('/analytics/monthly-sales', { months }),
  customerGrowth: (months = 12) => get('/analytics/customer-growth', { months }),
  topCustomers: (limit = 5) => get('/analytics/top-customers', { limit }),
  recentActivity: (limit = 10) => get('/analytics/recent-activity', { limit }),
}

export const wooApi = {
  status: () => get('/woocommerce/status'),
  test: () => api.post('/woocommerce/test-connection').then((r) => r.data),
  sync: (resource = 'all') => api.post(`/woocommerce/sync/${resource}`).then((r) => r.data),
}

export const settingsApi = {
  get: () => get('/settings'),
  update: (data) => api.put('/settings', data).then((r) => r.data),
}
