import { createBrowserRouter } from 'react-router-dom'
import AdminLayout from '../layouts/AdminLayout'
import IngredientMenu from '../admin-pages/IngredientMenu'
import DishMenu from '../admin-pages/DishMenu'
import UserManagement from '../admin-pages/UserManagement'

export const AdminRoutes = {
  path: "/admin",
  element: <AdminLayout />,
  children: [
    {
      index: true,
      element: <IngredientMenu />,
    },
    {
      path: "ingredient-menu",
      element: <IngredientMenu />,
    },
    {
      path: "dish-menu",
      element: <DishMenu />,
    },
    {
      path: "user-management",
      element: <UserManagement />,
    },
  ],
}