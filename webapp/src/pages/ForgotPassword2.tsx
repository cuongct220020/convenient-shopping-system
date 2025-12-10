import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send } from 'lucide-react'
import loginBg from '../assets/login-bg.png'
import { InputField } from '../components/InputField'
import { Button } from '../components/Button'
import { BackButton } from '../components/BackButton'

export default function ForgotPassword2() {
  const navigate = useNavigate()

  const [password1, setPassword1] = useState('')
  const [password2, setPassword2] = useState('')
  const [errors, setErrors] = useState<{
    password1: string | null
    password2: string | null
  }>({
    password1: null,
    password2: null
  })
  const [touched, setTouched] = useState<{
    password1: boolean
    password2: boolean
  }>({
    password1: false,
    password2: false
  })

  // Validation functions
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

  const handlePassword1Change = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword1(value)

    if (touched.password1) {
      setErrors((prev) => ({
        ...prev,
        password1: validatePassword(value)
      }))
    }

    // Also validate confirm password if it has been touched
    if (touched.password2) {
      setErrors((prev) => ({
        ...prev,
        password2: validateConfirmPassword(password2, value)
      }))
    }
  }

  const handlePassword1Blur = () => {
    setTouched((prev) => ({ ...prev, password1: true }))
    setErrors((prev) => ({
      ...prev,
      password1: validatePassword(password1)
    }))
  }

  const handlePassword2Change = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword2(value)

    if (touched.password2) {
      setErrors((prev) => ({
        ...prev,
        password2: validateConfirmPassword(value, password1)
      }))
    }
  }

  const handlePassword2Blur = () => {
    setTouched((prev) => ({ ...prev, password2: true }))
    setErrors((prev) => ({
      ...prev,
      password2: validateConfirmPassword(password2, password1)
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    const password1Error = validatePassword(password1)
    const password2Error = validateConfirmPassword(password2, password1)

    setErrors({
      password1: password1Error,
      password2: password2Error
    })

    setTouched({
      password1: true,
      password2: true
    })

    // If no errors, proceed with password reset
    if (!password1Error && !password2Error) {
      console.log('Password reset confirmed')
      // Add actual password reset logic here
      navigate('/user/forgot-password-notification')
    }
  }

  return (
    <div className="relative min-h-screen w-screen overflow-hidden bg-gray-100 font-sans">
      {/* Background gradient/image full screen */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="absolute inset-0 bg-black/5"></div>
      </div>

      {/* Main Content Container */}
      <div className="relative flex min-h-screen w-full">
        <div className="relative flex w-full h-screen flex-col overflow-hidden bg-white">
          {/* Header: Back Button */}
          <div className="my-4">
            <BackButton to="/user/forgot-password-authentication" text="Quay lại" />
          </div>

          {/* Scrollable Content Area */}
          <div className="no-scrollbar relative z-10 flex-1 overflow-y-auto">
            <div className="px-4 sm:px-6 md:px-8 pb-8 pt-2">
              {/* Header: Đặt lại mật khẩu */}
              <div className="mb-6 sm:mb-8 text-center">
                {/* Đặt lại mật khẩu Text */}
                <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-[#c93045]">Đặt lại mật khẩu</h1>
                <p className="mt-2 text-sm text-gray-600">
                  Xin chào <span className="font-semibold">Username</span>, vui
                  lòng nhập mật khẩu bạn muốn thay đổi.
                </p>
              </div>

              {/* Form with max-width constraint */}
              <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5 max-w-sm mx-auto">
                <div>
                  <InputField
                    id="password"
                    type="password"
                    label="Mật khẩu mới"
                    placeholder="Nhập mật khẩu"
                    value={password1}
                    onChange={handlePassword1Change}
                    onBlur={handlePassword1Blur}
                    error={errors.password1}
                  />
                </div>

                <div>
                  <InputField
                    id="confirm-password"
                    type="password"
                    label="Xác nhận mật khẩu mới"
                    placeholder="Nhập lại mật khẩu"
                    value={password2}
                    onChange={handlePassword2Change}
                    onBlur={handlePassword2Blur}
                    error={errors.password2}
                  />
                </div>

                <Button variant="primary" icon={Send} size="fit" type="submit">
                  Xác nhận
                </Button>
              </form>

              {/* Bottom Spacer for scrolling over background */}
              <div className="h-16 sm:h-20"></div>
            </div>
          </div>

          {/* Background Image Decoration (Bottom) */}
          <div className="pointer-events-none absolute inset-x-0 bottom-0 z-0 h-64 sm:h-80 md:h-96">
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
    </div>
  )
}
