import { createBrowserRouter } from 'react-router-dom'
import { AuthRoutes } from './AuthRoutes'
import { AdminRoutes, AdminLoginRoute } from './AdminRoutes'
import { MainRoutes } from './MainRoutes'

export const router = createBrowserRouter([
  AuthRoutes,
  AdminRoutes,
  AdminLoginRoute,
  MainRoutes,
])
