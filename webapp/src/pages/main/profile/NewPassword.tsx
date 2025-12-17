import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { NotificationCard } from 'components/NotificationCard';
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { InputField } from '../../../components/InputField';
import { Send, CheckCircle, LogIn, Home } from 'lucide-react'

const OldPassword = () => {
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
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full">
      {/* Back Navigation */}
      {/* Assumes the previous route was LoginInformation */}
      <BackButton to="/main/profile/authentication" text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-2">
        Đổi mật khẩu
      </h1>

      {/* Description */}
      <p className="text-base text-gray-800 mb-8">
        Vui lòng nhập mật khẩu mới của bạn.
      </p>

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

      {/* Popup Overlay */}
      {showPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <NotificationCard
            title="Mật khẩu đã thay đổi!"
            message=''
            icon={CheckCircle}
            iconBgColor="bg-green-500"
            buttonText="Trang chủ"
            buttonIcon={Home}
            onButtonClick={() => {
              setShowPopup(false)
              navigate('/main/profile')
            }}
          />
        </div>
      )}
    </div>
  );
};

export default OldPassword;