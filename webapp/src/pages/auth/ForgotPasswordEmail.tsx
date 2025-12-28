import { useState } from 'react'
import { Send } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { InputField } from '../../components/InputField'
import { Button } from '../../components/Button'
import { ok, Result } from 'neverthrow'
import { i18nKeys } from '../../utils/i18n/keys'
import { authService, AuthService } from '../../services/auth'
import { LocalStorage } from '../../services/storage/local'
import { i18n } from '../../utils/i18n/i18n'

export default function ForgotPasswordEmail() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [errors, setErrors] = useState<Result<void, i18nKeys>>(ok())
  const [touched, setTouched] = useState(false)

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setEmail(value)
    if (touched) {
      setErrors(AuthService.validateEmail(value))
    }
  }

  const handleEmailBlur = () => {
    setTouched(true)
    setErrors(AuthService.validateEmail(email))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrors(AuthService.validateEmail(email))
    setTouched(true)
    if (errors.isErr()) return
    console.info('Password reset request for:', email)
    authService.sendOtpRequest('reset_password', email)
    LocalStorage.inst.emailRequestingOtp = email
    navigate('/auth/forgot-password-authentication')
  }

  return (
    <>
      {/* Header: Đặt lại mật khẩu */}
      <div className="mb-6 text-center sm:mb-8">
        {/* Đặt lại mật khẩu Text */}
        <h1 className="text-2xl font-bold text-[#C3485C] sm:text-2xl md:text-3xl">
          Đặt lại mật khẩu
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Nhập email hoặc tên tài khoản của bạn.
        </p>
      </div>

      {/* Form with max-width constraint */}
      <form
        onSubmit={handleSubmit}
        className="mx-auto w-full max-w-sm space-y-4 sm:space-y-5"
      >
        <div>
          <InputField
            id="email"
            label="Email"
            placeholder="email@gmail.com"
            value={email}
            onChange={handleEmailChange}
            onBlur={handleEmailBlur}
            error={errors.isErr() ? i18n.t(errors.error) : undefined}
          />
        </div>

        <Button
          variant={AuthService.validateEmail(email).match(
            () => 'primary',
            () => 'disabled'
          )}
          icon={Send}
          size="fit"
          type="submit"
        >
          Xác nhận
        </Button>
      </form>

      {/* Bottom Spacer for scrolling over background */}
      <div className="h-16 sm:h-20"></div>
    </>
  )
}
