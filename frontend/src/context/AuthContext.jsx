import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authApi } from '../api'
import { TOKEN_KEY } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [admin, setAdmin] = useState(null)
  // "checking" while we validate a stored token on first load, so we don't flash the login page.
  const [checking, setChecking] = useState(Boolean(localStorage.getItem(TOKEN_KEY)))

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setAdmin(null)
  }, [])

  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) return
    authApi.me().then((d) => setAdmin(d.admin)).catch(() => logout()).finally(() => setChecking(false))
  }, [logout])

  useEffect(() => {
    window.addEventListener('smartcrm:logout', logout)
    return () => window.removeEventListener('smartcrm:logout', logout)
  }, [logout])

  const login = useCallback(async (email, password) => {
    const data = await authApi.login(email, password)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setAdmin(data.admin)
  }, [])

  const value = useMemo(() => ({ admin, checking, login, logout }), [admin, checking, login, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
