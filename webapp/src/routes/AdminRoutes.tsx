import { createBrowserRouter } from 'react-router-dom'
import AdminLayout from '../layouts/AdminLayout'
import Login from '../admin-pages/Login'
import IngredientMenu from '../admin-pages/IngredientMenu'
import DishMenu from '../admin-pages/DishMenu'
import UserManagement from '../admin-pages/UserManagement'

export const AdminRoutes = {
  path: "/admin",
  element: <AdminLayout />,
  children: [
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

export const AdminLoginRoute = {
  path: "/admin/login",
  element: <Login />,
}