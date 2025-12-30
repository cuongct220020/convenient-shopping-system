import AuthLayout from '../layouts/AuthLayout'
import Login from '../pages/auth/Login'
import Register from '../pages/auth/Register'
import ForgotPasswordEmail from '../pages/auth/ForgotPasswordEmail'
import ForgotPasswordNewPassword from '../pages/auth/ForgotPasswordNewPassword'
import LoginAuthentication from '../pages/auth/LoginAuthentication'
import ForgotPasswordAuthentication from '../pages/auth/ForgotPasswordAuthentication'

export const AuthRoutes = {
  path: '/auth',
  element: <AuthLayout />,
  children: [
    {
      index: true,
      element: <Login />,
      handle: { backTo: '/', backText: 'Trang chủ' }
    },
    {
      path: 'login',
      element: <Login />,
      handle: { backTo: '/', backText: 'Trang chủ' }
    },
    {
      path: 'register',
      element: <Register />,
      handle: { backTo: '/auth/login', backText: 'Đăng nhập' }
    },
    {
      path: 'forgot-password-email',
      element: <ForgotPasswordEmail />,
      handle: { backTo: '/auth/login', backText: 'Đăng nhập' }
    },
    {
      path: 'forgot-password-new-password',
      element: <ForgotPasswordNewPassword />,
      handle: { backTo: '/auth/forgot-password-email', backText: 'Quay lại' }
    },
    {
      path: 'login-authentication',
      element: <LoginAuthentication />,
      handle: { backTo: '/auth/login', backText: 'Quay lại' }
    },
    {
      path: 'forgot-password-authentication',
      element: <ForgotPasswordAuthentication />,
      handle: { backTo: '/auth/forgot-password-email', backText: 'Quay lại' }
    }
  ]
}
