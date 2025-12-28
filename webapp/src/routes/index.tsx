import { createBrowserRouter, Outlet } from 'react-router-dom'
import { AuthRoutes } from './AuthRoutes'
import { AdminRoutes } from './AdminRoutes'
import { MainRoutes } from './MainRoutes'
import NotFoundPage from '../pages/error/NotFound'
import RouterErrorPage from '../pages/error/RouterError'

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
        element: <NotFoundPage />
      }
    ]
  }
])
