import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserPlus, LogIn } from 'lucide-react'
import loginBg from '../assets/login-bg.png'
import { Button } from '../components/Button'
import { InputField } from '../components/InputField'
import { BackButton } from '../components/BackButton'

export default function Register() {
  const navigate = useNavigate()
  // State for form fields
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })

  const [errors, setErrors] = useState<{
    email: string | null
    username: string | null
    password: string | null
    confirmPassword: string | null
  }>({
    email: null,
    username: null,
    password: null,
    confirmPassword: null
  })

  const [touched, setTouched] = useState<{
    email: boolean
    username: boolean
    password: boolean
    confirmPassword: boolean
  }>({
    email: false,
    username: false,
    password: false,
    confirmPassword: false
  })

  // Validation functions
  const validateEmail = (email: string): string | null => {
    if (!email.trim()) {
      return 'Email không được để trống'
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return 'Email không hợp lệ'
    }

    return null
  }

  const validateUsername = (username: string): string | null => {
    if (!username.trim()) {
      return 'Tên đăng nhập không được để trống'
    }

    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
    if (!usernameRegex.test(username)) {
      return 'Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới (3-20 ký tự)'
    }

    return null
  }

  const validatePassword = (password: string): string | null => {
    if (!password.trim()) {
      return 'Mật khẩu không được để trống'
    }
    if (password.length < 6) {
      return 'Mật khẩu phải có ít nhất 6 ký tự'
    }
    return null
  }

  const validateConfirmPassword = (
    confirmPassword: string,
    password: string
  ): string | null => {
    if (!confirmPassword.trim()) {
      return 'Xác nhận mật khẩu không được để trống'
    }
    if (confirmPassword !== password) {
      return 'Mật khẩu xác nhận không khớp'
    }
    return null
  }

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))

    if (touched[field as keyof typeof touched]) {
      let error: string | null = null
      switch (field) {
        case 'email':
          error = validateEmail(value)
          break
        case 'username':
          error = validateUsername(value)
          break
        case 'password':
          error = validatePassword(value)
          break
        case 'confirmPassword':
          error = validateConfirmPassword(value, formData.password)
          break
        default:
          break
      }
      setErrors((prev) => ({ ...prev, [field]: error }))
    }
  }

  const handleBlur = (field: string) => {
    setTouched((prev) => ({ ...prev, [field]: true }))

    let error: string | null = null
    switch (field) {
      case 'email':
        error = validateEmail(formData.email)
        break
      case 'username':
        error = validateUsername(formData.username)
        break
      case 'password':
        error = validatePassword(formData.password)
        break
      case 'confirmPassword':
        error = validateConfirmPassword(
          formData.confirmPassword,
          formData.password
        )
        break
      default:
        break
    }
    setErrors((prev) => ({ ...prev, [field]: error }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    const emailError = validateEmail(formData.email)
    const usernameError = validateUsername(formData.username)
    const passwordError = validatePassword(formData.password)
    const confirmPasswordError = validateConfirmPassword(
      formData.confirmPassword,
      formData.password
    )

    setErrors({
      email: emailError,
      username: usernameError,
      password: passwordError,
      confirmPassword: confirmPasswordError
    })

    setTouched({
      email: true,
      username: true,
      password: true,
      confirmPassword: true
    })

    // If no errors, proceed with registration
    if (
      !emailError &&
      !usernameError &&
      !passwordError &&
      !confirmPasswordError
    ) {
      console.log('Registration attempt with:', formData)
      navigate('/auth/register-notification')
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
            {/* Title */}
            <h1 className="mb-8 text-center text-3xl font-bold text-[#c93045]">
              Đăng ký tài khoản
            </h1>

            {/* Form */}
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <InputField
                  id="email"
                  label="Email"
                  required={true}
                  placeholder="Nhập email"
                  value={formData.email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    handleChange('email', e.target.value)
                  }
                  onBlur={() => handleBlur('email')}
                  error={errors.email}
                />
              </div>

              <div className="mb-4">
                <InputField
                  id="username"
                  label="Tên đăng nhập"
                  required={true}
                  placeholder="Nhập tên đăng nhập"
                  value={formData.username}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    handleChange('username', e.target.value)
                  }
                  onBlur={() => handleBlur('username')}
                  error={errors.username}
                />
              </div>

              <div className="mb-4">
                <InputField
                  id="password"
                  type="password"
                  label="Mật khẩu"
                  required={true}
                  placeholder="Nhập mật khẩu"
                  value={formData.password}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    handleChange('password', e.target.value)
                  }
                  onBlur={() => handleBlur('password')}
                  error={errors.password}
                />
              </div>

              <div className="mb-4">
                <InputField
                  id="confirmPassword"
                  type="password"
                  label="Xác nhận mật khẩu"
                  required={true}
                  placeholder="Nhập lại mật khẩu"
                  value={formData.confirmPassword}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    handleChange('confirmPassword', e.target.value)
                  }
                  onBlur={() => handleBlur('confirmPassword')}
                  error={errors.confirmPassword}
                />
              </div>

              {/* Register Button */}
              <div className="mt-6">
                <Button
                  variant="primary"
                  icon={UserPlus}
                  size="fit"
                  type="submit"
                >
                  Đăng ký tài khoản
                </Button>
              </div>
            </form>

            {/* Divider */}
            <div className="relative my-4 flex items-center text-sm">
              <div className="flex-1 border-t border-gray-300"></div>
              <span className="px-4 text-gray-400">hoặc</span>
              <div className="flex-1 border-t border-gray-300"></div>
            </div>

            {/* Login Button */}
            <div>
              <Button
                variant="secondary"
                icon={LogIn}
                size="fit"
                onClick={() => navigate('/auth/login')}
              >
                Đăng nhập
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
