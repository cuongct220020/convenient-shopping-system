import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RefreshCw, XCircle } from 'lucide-react'
import { Button } from '../../components/Button'
import { OPTInput } from '../../components/OPTInput'
import { LocalStorage } from '../../services/storage/local'
import { Time } from '../../utils/time'
import { AuthService, authService } from '../../services/auth'
import { useIsMounted } from '../../hooks/useIsMounted'
import { NotificationCard } from '../../components/NotificationCard'
import { i18n } from '../../utils/i18n/i18n'
import { LoadingOverlay } from '../../components/Loading'
import { SessionStorage } from '../../services/storage/session'

function initializeOtpTimer(): number {
  if (LocalStorage.inst.otpCanRequest) {
    return LocalStorage.inst.otpStartCountdown()
  }
  return LocalStorage.inst.otpTimeToNextRequest
}

export default function ForgotPasswordAuthentication() {
  const navigate = useNavigate()
  const [otpCode, setOtpCode] = useState('')
  const [timeToOtpReq, setTimeToOtpReq] = useState(initializeOtpTimer())
  const [isAskingNewOtp, setIsAskingNewOtp] = useState(false)
  const [popup, setPopup] = useState({
    show: false,
    type: 'error' as 'error' | 'not-match'
  })
  const [isLoading, setIsLoading] = useState(false)
  const email = LocalStorage.inst.emailRequestingOtp
  const isMounted = useIsMounted()
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeToOtpReq((prev) => Math.max(0, prev - 1))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const handleOtpChanged = (code: string) => {
    setOtpCode(code)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) {
      console.error('Expect to find email in local storage')
      navigate('/auth/forgot-password-email')
      return
    }
    if (!AuthService.validateOtpFormat(otpCode)) {
      return
    }
    setIsLoading(true)
    const response = await authService.verifyOtp({
      identification: email,
      otp: otpCode,
      type: 'reset_password'
    })
    if (!isMounted.current) return
    setIsLoading(false)
    response
      .andTee(() => {
        SessionStorage.inst.resetPasswordOtp = otpCode
        navigate('/auth/forgot-password-new-password')
      })
      .mapErr((e) => {
        // TODO: once updated with new API, also check for 404 aka 'user-not-found'
        if (e.type === 'incorrect-otp') {
          setPopup({ show: true, type: 'not-match' })
        } else {
          setPopup({ show: true, type: 'error' })
        }
      })
  }

  const handleOtpResendClick = async () => {
    if (!email) return
    if (timeToOtpReq > 0) return
    setIsAskingNewOtp(true)
    const response = await authService.sendOtpRequest('reset_password', email)
    if (!isMounted.current) return
    setIsAskingNewOtp(false)
    response.match(
      () => {
        setTimeToOtpReq(initializeOtpTimer())
      },
      () => setPopup({ show: true, type: 'error' })
    )
  }

  return (
    <LoadingOverlay isLoading={isLoading}>
      <div className="flex flex-1 flex-col">
        {/* Header: Xác thực email */}
        <div className="mb-6 text-center sm:mb-8">
          {/* Xác thực email Text */}
          <h1 className="text-2xl font-bold text-[#C3485C] sm:text-2xl md:text-3xl">
            Xác thực email
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="mx-auto max-w-sm">
          {/* Description Text */}
          <p className="mb-6 text-justify text-sm leading-relaxed text-gray-700">
            Chúng tôi vừa gửi mã xác nhận 6 chữ số đến email của bạn (nếu email
            đã được đăng ký). Bạn vui lòng nhập mã để tiếp tục
          </p>

          {/* OTP Input Component */}
          <div className="mb-8 px-2">
            <OPTInput length={6} onChange={handleOtpChanged} />
          </div>

          {/* Submit Button */}
          <div className="mb-6">
            <Button
              type="submit"
              variant={
                AuthService.validateOtpFormat(otpCode) ? 'primary' : 'disabled'
              }
              size="fit"
            >
              Xác nhận
            </Button>
          </div>

          {/* Resend Timer */}
          <button
            type="button"
            className={`flex w-full items-center justify-center text-sm transition-colors ${
              timeToOtpReq > 0
                ? 'cursor-not-allowed text-gray-400'
                : 'text-gray-500 hover:text-[#C3485C]'
            }`}
            disabled={timeToOtpReq > 0}
            onClick={handleOtpResendClick}
          >
            <RefreshCw
              size={16}
              className={`mr-2 ${isAskingNewOtp ? 'animate-spin' : ''}`}
            />
            <span>
              Gửi lại mã {timeToOtpReq <= 0 ? '' : Time.MM_SS(timeToOtpReq)}
            </span>
          </button>

          {/* Bottom Spacer */}
          <div className="h-16 sm:h-20"></div>
        </form>
        {popup.show && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
            <NotificationCard
              title={
                popup.type === 'not-match'
                  ? i18n.t('auth_failed')
                  : i18n.t('error_occured')
              }
              message={
                popup.type === 'not-match'
                  ? i18n.t('otp_unverified')
                  : i18n.t('internal_error')
              }
              icon={XCircle}
              iconBgColor="bg-red-500"
              buttonText={i18n.t('confirm')}
              onButtonClick={() =>
                setPopup((prev) => ({ ...prev, show: false }))
              }
            ></NotificationCard>
          </div>
        )}
      </div>
    </LoadingOverlay>
  )
}
