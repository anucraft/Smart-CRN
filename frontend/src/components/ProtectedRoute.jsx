import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Loading } from './ui'

/** Wrap any element that needs a logged-in admin. */
export default function ProtectedRoute({ children }) {
  const { admin, checking } = useAuth()
  const location = useLocation()
  if (checking) return <Loading label="Checking your session…" />
  if (!admin) return <Navigate to="/login" replace state={{ from: location }} />
  return children
}
