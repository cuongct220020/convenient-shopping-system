import { createBrowserRouter } from 'react-router-dom'
import { AuthRoutes } from './AuthRoutes'
import { AdminRoutes } from './AdminRoutes'

export const router = createBrowserRouter([
  AuthRoutes,
  AdminRoutes,
])
