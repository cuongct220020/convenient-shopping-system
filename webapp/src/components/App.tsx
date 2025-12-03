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

export default function App() {
  return (
    <Router>
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
      </Routes>
    </Router>
  )
}
