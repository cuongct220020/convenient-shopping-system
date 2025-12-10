import { Routes, Route } from 'react-router-dom'
import AdminLayout from '../layouts/AdminLayout'
import IngredientList from '../admin-pages/IngredientList'
import AddIngredient from '../admin-pages/AddIngredient'
import ModifyIngredient from '../admin-pages/ModifyIngredient'
import ViewIngredient from '../admin-pages/ViewIngredient'
import DishList from '../admin-pages/DishList'
import AddDish from '../admin-pages/AddDish'
import ModifyDish from '../admin-pages/ModifyDish'
import ViewDish from '../admin-pages/ViewDish'

export default function AdminRoutes() {
  return (
    <AdminLayout>
      <Routes>
        <Route path="ingredient-list" element={<IngredientList />} />
        <Route path="add-ingredient" element={<AddIngredient />} />
        <Route path="modify-ingredient" element={<ModifyIngredient />} />
        <Route path="view-ingredient" element={<ViewIngredient />} />
        <Route path="dish-list" element={<DishList />} />
        <Route path="add-dish" element={<AddDish />} />
        <Route path="modify-dish" element={<ModifyDish />} />
        <Route path="view-dish" element={<ViewDish />} />
      </Routes>
    </AdminLayout>
  )
}