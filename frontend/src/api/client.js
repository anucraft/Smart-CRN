import axios from 'axios'

export const TOKEN_KEY = 'smartcrm_token'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 120000, // a first full WooCommerce sync can take a while
})

// Attach the JWT to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Expired/invalid token -> tell the app to log out (AuthContext listens).
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const isLogin = err.config?.url?.includes('/auth/login')
    if (err.response?.status === 401 && !isLogin) {
      localStorage.removeItem(TOKEN_KEY)
      window.dispatchEvent(new Event('smartcrm:logout'))
    }
    return Promise.reject(err)
  },
)

export function errorMessage(err) {
  if (err.response?.data?.error) return err.response.data.error
  if (err.code === 'ERR_NETWORK') return 'Cannot reach the server. Check that the backend is running.'
  return err.message || 'Something went wrong.'
}

export default api
