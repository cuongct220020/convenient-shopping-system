import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogIn, UserPlus } from 'lucide-react'
import loginBg from '../assets/login-bg.png'
import { InputField } from '../components/InputField'
import { Button } from '../components/Button'
import { BackButton } from '../components/BackButton'

export default function Login() {
  const navigate = useNavigate()
  // State management for form inputs
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<{
    email: string | null
    password: string | null
  }>({
    email: null,
    password: null
  })
  const [touched, setTouched] = useState<{
    email: boolean
    password: boolean
  }>({
    email: false,
    password: false
  })

  // Validation functions
  const validateEmailOrUsername = (input: string): string | null => {
    if (!input.trim()) {
      return 'Email hoặc tên đăng nhập không được để trống'
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/

    const isEmail = emailRegex.test(input)
    const isUsername = usernameRegex.test(input)

    if (!isEmail && !isUsername) {
      return 'Email hoặc tên đăng nhập không hợp lệ'
    }

    return null
  }

  const validatePassword = (password: string): string | null => {
    if (!password.trim()) {
      return 'Mật khẩu không được để trống'
    }
    return null
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setEmail(value)

    if (touched.email) {
      setErrors((prev) => ({
        ...prev,
        email: validateEmailOrUsername(value)
      }))
    }
  }

  const handleEmailBlur = () => {
    setTouched((prev) => ({ ...prev, email: true }))
    setErrors((prev) => ({
      ...prev,
      email: validateEmailOrUsername(email)
    }))
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword(value)

    if (touched.password) {
      setErrors((prev) => ({
        ...prev,
        password: validatePassword(value)
      }))
    }
  }

  const handlePasswordBlur = () => {
    setTouched((prev) => ({ ...prev, password: true }))
    setErrors((prev) => ({
      ...prev,
      password: validatePassword(password)
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    const emailError = validateEmailOrUsername(email)
    const passwordError = validatePassword(password)

    setErrors({
      email: emailError,
      password: passwordError
    })

    setTouched({
      email: true,
      password: true
    })

    // If no errors, proceed with login
    if (!emailError && !passwordError) {
      console.log('Login attempt with:', email)
      // Add actual login logic here
      navigate('/auth/login-authentication')
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-100 font-sans">
      {/* Mobile Container */}
      <div className="relative flex h-[812px] w-[375px] flex-col overflow-hidden bg-white shadow-2xl">
        {/* Header: Back Button */}
        <div className="my-4">
          <BackButton to="/" text="Trang chủ" />
        </div>

        {/* Scrollable Content Area */}
        <div className="no-scrollbar relative z-10 flex-1 overflow-y-auto">
          <div className="px-6 pb-8 pt-2">
            {/* Logo & Header: ShopSense above Đăng nhập */}
            <div className="mb-8 text-center">
              {/* ShopSense Text with precise S coloring */}
              <h1 className="mb-4 text-4xl font-bold">
                <span className="text-[#c93045]">S</span>
                <span className="text-[#f7b686]">hop</span>
                <span className="text-[#c93045]">S</span>
                <span className="text-[#f7b686]">ense</span>
              </h1>

              {/* Đăng nhập Text */}
              <h2 className="text-3xl font-bold text-[#c93045]">Đăng nhập</h2>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <InputField
                  id="email-username"
                  label="Email"
                  subLabel="Tên đăng nhập"
                  placeholder="Nhập email hoặc tên đăng nhập"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={handleEmailBlur}
                  error={errors.email}
                />
              </div>

              <div className="mb-1">
                <InputField
                  id="password"
                  type="password"
                  label="Mật khẩu"
                  placeholder="Nhập mật khẩu"
                  value={password}
                  onChange={handlePasswordChange}
                  onBlur={handlePasswordBlur}
                  error={errors.password}
                />
              </div>

              <div className="mb-4 text-right">
                <Link
                  to="/forgot-password-1"
                  className="text-xs font-bold text-[#c93045] hover:underline"
                >
                  Quên mật khẩu?
                </Link>
              </div>

              <Button variant="primary" icon={LogIn} size="fit" type="submit">
                Đăng nhập
              </Button>
            </form>

            {/* Divider */}
            <div className="relative my-4 flex items-center text-sm">
              <div className="flex-1 border-t border-gray-300"></div>
              <span className="px-4 text-gray-400">hoặc</span>
              <div className="flex-1 border-t border-gray-300"></div>
            </div>

            {/* Register Button */}
            <div>
              <Button
                variant="secondary"
                icon={UserPlus}
                size="fit"
                onClick={() => navigate('/register')}
              >
                Đăng ký tài khoản
              </Button>
            </div>

            {/* Bottom Spacer for scrolling over background */}
            <div className="h-20"></div>
          </div>
        </div>

        {/* Background Image Decoration (Bottom) */}
        <div className="pointer-events-none absolute inset-x-0 bottom-0 z-0 h-80">
          {/* Using a gradient overlay to fade image into white */}
          <div className="absolute inset-0 z-10 bg-gradient-to-t from-white/10 via-white/40 to-white"></div>
          {/* Food background placeholder */}
          <img
            src={loginBg}
            alt="Food Background"
            className="size-full object-cover opacity-70"
          />
        </div>
      </div>
    </div>
  )
}
