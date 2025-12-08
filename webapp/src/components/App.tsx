import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Login from '../pages/Login'
import Register from '../pages/Register'
import ForgotPassword1 from '../pages/ForgotPassword1'
import ForgotPassword2 from '../pages/ForgotPassword2'
import RegisterNotification from '../pages/RegisterNotification'
import ForgotPasswordNotification from '../pages/ForgotPasswordNotification'
import LoginAuthentication from '../pages/LoginAuthentication'
import ForgotPasswordAuthentication from '../pages/ForgotPasswordAuthentication'
import IngredientList from '../pages/IngredientList'
import AddIngredient from '../pages/AddIngredient'
import ModifyIngredient from '../pages/ModifyIngredient'
import ViewIngredient from '../pages/ViewIngredient'
import DishList from '../pages/DishList'
import AddDish from '../pages/AddDish'
import ModifyDish from '../pages/ModifyDish'
import ViewDish from '../pages/ViewDish'
import { Sidebar } from './Sidebar'

export default function App() {
  return (
    <Router>
      <div className="flex bg-white font-sans text-gray-800" style={{ width: '1440px', height: '1024px' }}>
        <Sidebar />
        <Routes>
          <Route path="/" element={<IngredientList />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password-1" element={<ForgotPassword1 />} />
          <Route path="/forgot-password-2" element={<ForgotPassword2 />} />
          <Route
            path="/register-notification"
            element={<RegisterNotification />}
          />
          <Route
            path="/forgot-password-notification"
            element={<ForgotPasswordNotification />}
          />
          <Route path="/login-authentication" element={<LoginAuthentication />} />
          <Route
            path="/forgot-password-authentication"
            element={<ForgotPasswordAuthentication />}
          />
          <Route path="/ingredient-list" element={<IngredientList />} />
          <Route path="/add-ingredient" element={<AddIngredient />} />
          <Route path="/modify-ingredient" element={<ModifyIngredient />} />
          <Route path="/view-ingredient" element={<ViewIngredient />} />
          <Route path="/dish-list" element={<DishList />} />
          <Route path="/add-dish" element={<AddDish />} />
          <Route path="/modify-dish" element={<ModifyDish />} />
          <Route path="/view-dish" element={<ViewDish />} />
        </Routes>
      </div>
    </Router>
  )
}
