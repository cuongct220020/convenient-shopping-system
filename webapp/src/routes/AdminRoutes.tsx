import { Routes, Route } from 'react-router-dom'
import IngredientMenu from '../admin-pages/IngredientMenu'
import DishMenu from '../admin-pages/DishMenu'
import AdminLayout from '../layouts/AdminLayout'
import UserManagement from 'admin-pages/UserManagement'

export default function AdminRoutes() {
  return (
    <AdminLayout>
      <Routes>
        <Route path="/" element={<IngredientMenu />} />
        <Route path="ingredient-menu" element={<IngredientMenu />} />
        <Route path="dish-menu" element={<DishMenu />} />
        <Route path="user-management" element={<UserManagement />} />
      </Routes>
    </AdminLayout>
  )
}