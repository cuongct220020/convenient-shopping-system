import { createBrowserRouter, Outlet } from 'react-router-dom'
import { AuthRoutes } from './AuthRoutes'
import { AdminRoutes } from './AdminRoutes'
import { MainRoutes } from './MainRoutes'
import RouterErrorPage from '../pages/error/RouterError'
import { BootPage } from '../pages/Boot'

export const router = createBrowserRouter([
  {
    path: '/',
    errorElement: <RouterErrorPage />,
    element: <Outlet />,
    children: [
      AuthRoutes,
      AdminRoutes,
      MainRoutes,
      {
        index: true,
        element: <BootPage />
      }
    ]
  }
])
