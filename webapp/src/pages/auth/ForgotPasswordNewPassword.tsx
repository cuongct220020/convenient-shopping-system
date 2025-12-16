import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, CheckCircle, LogIn, Home } from 'lucide-react'
import { InputField } from '../../components/InputField'
import { Button } from '../../components/Button'
import { NotificationCard } from '../../components/NotificationCard'

export default function ForgotPasswordNewPassword() {
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

  // State for popup
  const [showPopup, setShowPopup] = useState(false)

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
      setShowPopup(true)
    }
  }

  return (
    <>
      {/* Header: Đặt lại mật khẩu */}
      <div className="mb-6 sm:mb-8 text-center">
        {/* Đặt lại mật khẩu Text */}
        <h1 className="text-2xl sm:text-2xl md:text-3xl font-bold text-[#C3485C]">Đặt lại mật khẩu</h1>
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

      {/* Popup Overlay */}
      {showPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <NotificationCard
            title="Thay đổi mật khẩu thành công!"
            message="Mật khẩu của bạn đã được thay đổi thành công. Vui lòng đăng nhập bằng mật khẩu mới."
            icon={CheckCircle}
            iconBgColor="bg-green-500"
            buttonText="Trang chủ"
            buttonIcon={Home}
            onButtonClick={() => {
              setShowPopup(false)
              navigate('/auth/login')
            }}
            buttonVariant='secondary'
            button2Text="Đăng nhập"
            button2Icon={LogIn}
            onButton2Click={() => {
              setShowPopup(false)
              navigate('/auth/login')
            }}
            button2Variant='primary'
          />
        </div>
      )}
    </>
  )
}
