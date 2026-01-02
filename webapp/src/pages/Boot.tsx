import { useNavigate } from 'react-router-dom'
import { authController } from '../controllers/authController'
import { useEffect, useRef } from 'react'

export function BootPage() {
  const navigate = useNavigate()
  const wasNavigated = useRef(false)
  useEffect(() => {
    if (wasNavigated.current) return
    wasNavigated.current = true
    const goalPath = authController.isLoggedIn ? '/main/profile' : '/auth/login'
    navigate(goalPath)
  }, [navigate])
  return <>Loading...</>
}
