import { createBrowserRouter } from 'react-router-dom'
import { AuthRoutes } from './AuthRoutes'
import { AdminRoutes } from './AdminRoutes'
import { MainRoutes } from './MainRoutes'
import { BootPage } from '../pages/Boot'

export const router = createBrowserRouter([
  {
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
