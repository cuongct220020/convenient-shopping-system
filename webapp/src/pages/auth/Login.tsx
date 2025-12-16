import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogIn, UserPlus } from 'lucide-react'
import { InputField } from '../../components/InputField'
import { Button } from '../../components/Button'

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
    <>
      {/* Logo & Header: ShopSense above Đăng nhập */}
      <div className="mb-6 sm:mb-8 text-center">
        {/* ShopSense Text with precise S coloring */}
        <h1 className="mb-3 sm:mb-4 text-3xl sm:text-3xl md:text-4xl font-bold">
          <span className="text-[#C3485C]">S</span>
          <span className="text-[#f7b686]">hop</span>
          <span className="text-[#C3485C]">S</span>
          <span className="text-[#f7b686]">ense</span>
        </h1>

        {/* Đăng nhập Text */}
        <h2 className="text-2xl sm:text-2xl md:text-3xl font-bold text-[#C3485C]">Đăng nhập</h2>
      </div>

      {/* Login Form with max-width constraint */}
      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5 max-w-sm mx-auto">
        <div>
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

        <div>
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

        <div className="text-right">
          <Link
            to="/auth/forgot-password-email"
            className="text-xs sm:text-sm font-bold text-[#C3485C] hover:underline"
          >
            Quên mật khẩu?
          </Link>
        </div>

        <Button variant="primary" icon={LogIn} size="fit" type="submit">
          Đăng nhập
        </Button>
      </form>

      {/* Divider */}
      <div className="relative my-4 sm:my-5 flex items-center text-sm max-w-sm mx-auto">
        <div className="flex-1 border-t border-gray-300"></div>
        <span className="px-3 sm:px-4 text-gray-400">hoặc</span>
        <div className="flex-1 border-t border-gray-300"></div>
      </div>

      {/* Register Button */}
      <div className="max-w-sm mx-auto">
        <Button
          variant="secondary"
          icon={UserPlus}
          size="fit"
          onClick={() => navigate('/auth/register')}
          >
          Đăng ký tài khoản
        </Button>
      </div>

      {/* Bottom Spacer for scrolling over background */}
      <div className="h-16 sm:h-20"></div>
    </>
  )
}
