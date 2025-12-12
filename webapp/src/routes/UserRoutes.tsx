import { Routes, Route } from 'react-router-dom'
import Login from '../pages/Login'
import Register from '../pages/Register'
import ForgotPasswordEmail from '../pages/ForgotPasswordEmail'
import ForgotPasswordNewPassword from '../pages/ForgotPasswordNewPassword'
import LoginAuthentication from '../pages/LoginAuthentication'
import ForgotPasswordAuthentication from '../pages/ForgotPasswordAuthentication'

export default function UserRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password-email" element={<ForgotPasswordEmail />} />
      <Route path="/forgot-password-new-password" element={<ForgotPasswordNewPassword />} />
      <Route path="/login-authentication" element={<LoginAuthentication />} />
      <Route path="/forgot-password-authentication" element={<ForgotPasswordAuthentication />} />
    </Routes>
  )
}