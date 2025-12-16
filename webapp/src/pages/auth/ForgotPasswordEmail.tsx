import { useState } from 'react'
import { Send } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import loginBg from '../../assets/login-bg.png'
import { InputField } from '../../components/InputField'
import { Button } from '../../components/Button'
import { BackButton } from '../../components/BackButton'

export default function ForgotPassword() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [errors, setErrors] = useState<{
    email: string | null
  }>({
    email: null
  })
  const [touched, setTouched] = useState<{
    email: boolean
  }>({
    email: false
  })

  // Validation function
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate email field
    const emailError = validateEmailOrUsername(email)

    setErrors({
      email: emailError
    })

    setTouched({
      email: true
    })

    // If no errors, proceed with password reset
    if (!emailError) {
      console.log('Password reset request for:', email)
      // Add actual password reset logic here
      navigate('/user/forgot-password-authentication')
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
            <BackButton to="/user/login" text="Đăng nhập" />
          </div>

          {/* Scrollable Content Area */}
          <div className="no-scrollbar relative z-10 flex-1 overflow-y-auto">
            <div className="px-4 sm:px-6 md:px-8 pb-8 pt-2">
              {/* Header: Đặt lại mật khẩu */}
              <div className="mb-6 sm:mb-8 text-center">
                {/* Đặt lại mật khẩu Text */}
                <h1 className="text-2xl sm:text-2xl md:text-3xl font-bold text-[#C3485C]">Đặt lại mật khẩu</h1>
                <p className="mt-2 text-sm text-gray-600">
                  Nhập email hoặc tên tài khoản của bạn.
                </p>
              </div>

              {/* Form with max-width constraint */}
              <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5 max-w-sm mx-auto">
                <div>
                  <InputField
                    id="email"
                    label="Email"
                    subLabel="Tên đăng nhập"
                    placeholder="email@gmail.com"
                    value={email}
                    onChange={handleEmailChange}
                    onBlur={handleEmailBlur}
                    error={errors.email}
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
