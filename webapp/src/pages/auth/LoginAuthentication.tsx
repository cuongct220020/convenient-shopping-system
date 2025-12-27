import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle, RefreshCw, XCircle } from 'lucide-react'
import { Button } from '../../components/Button'
import { OPTInput } from '../../components/OPTInput'
import { LocalStorage } from '../../services/storage/local'
import { Time } from '../../utils/time'
import { authService, AuthService } from '../../services/auth'
import { useIsMounted } from '../../hooks/useIsMounted'
import { LoadingOverlay } from '../../components/Loading'
import { NotificationCard } from '../../components/NotificationCard'
import { i18n } from '../../utils/i18n/i18n'

function initializeOtpCountdown(): number {
  if (LocalStorage.inst.otpCanRequest) {
    return LocalStorage.inst.otpStartCountdown()
  }
  return LocalStorage.inst.otpTimeToNextRequest
}

export default function LoginAuthentication() {
  const navigate = useNavigate()
  const [otpCode, setOtpCode] = useState('')
  const [timeToRequestOtp, setTimeToRequestOtp] = useState(
    initializeOtpCountdown()
  )
  const [isLoading, setIsLoading] = useState(false)
  const [isAskingNewOtp, setIsAskingNewOtp] = useState(false)
  const [popup, setPopup] = useState({
    show: false,
    type: 'error' as 'error' | 'succeed' | 'incorrect'
  })
  const isMounted = useIsMounted()
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeToRequestOtp((prev) => Math.max(0, prev - 1))
    }, 1000)
    return () => clearInterval(interval)
  }, [])
  const username = 'User'
  const identification = LocalStorage.inst.unverifiedUserIdentification

  const handleOtpChanged = (code: string) => {
    setOtpCode(code)
  }
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!AuthService.validateOtpFormat(otpCode)) return
    if (!identification) {
      console.error('We should not be in login auth page')
      navigate('/auth/login')
      return
    }
    setIsLoading(true)
    const response = await authService.verifyUser({
      identification,
      otp: otpCode
    })
    if (!isMounted.current) return
    setIsLoading(false)
    response.match(
      () => {
        LocalStorage.inst.unverifiedUserIdentification = null
        setPopup({ show: true, type: 'succeed' })
      },
      (e) => {
        console.error(e)
        if (e.type === 'incorrect-otp') {
          setPopup({ show: true, type: 'incorrect' })
        } else {
          setPopup({ show: true, type: 'error' })
        }
      }
    )
  }
  const handleOtpResendClick = async () => {
    console.log(identification, timeToRequestOtp)
    if (!identification) return
    if (timeToRequestOtp > 0) return
    setIsAskingNewOtp(true)
    const response = await authService.sendVerifyUserRequest(identification)
    if (!isMounted.current) return
    setIsAskingNewOtp(false)
    response.match(
      () => {
        setTimeToRequestOtp(initializeOtpCountdown())
      },
      () => setPopup({ show: true, type: 'error' })
    )
  }
  const handlePopupClick = async () => {
    if (popup.type === 'succeed') {
      navigate('/auth/login')
    } else {
      setPopup((prev) => ({ ...prev, show: false }))
    }
  }

  return (
    <LoadingOverlay isLoading={isLoading}>
      <div className="flex flex-1 flex-col">
        {/* Header: Xác thực tài khoản */}
        <div className="mb-6 text-center sm:mb-8">
          {/* Xác thực tài khoản Text */}
          <h1 className="text-2xl font-bold text-[#C3485C] sm:text-2xl md:text-3xl">
            Xác thực tài khoản
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="mx-auto max-w-sm">
          {/* Description Text */}
          <p className="mb-6 text-justify text-sm leading-relaxed text-gray-700">
            Xin chào{' '}
            <span className="font-bold text-[#C3485C]">{username}</span>, bạn đã
            đăng nhập thành công. Bạn cần xác nhận tài khoản để tiếp tục sử dụng
            ứng dụng. Vui lòng nhập mã 6 chữ số được gửi đến email của bạn.
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
              timeToRequestOtp > 0
                ? 'cursor-not-allowed text-gray-400'
                : 'text-gray-500 hover:text-[#C3485C]'
            }`}
            disabled={timeToRequestOtp > 0}
            onClick={handleOtpResendClick}
          >
            <RefreshCw
              size={16}
              className={`mr-2 ${isAskingNewOtp ? 'animate-spin' : ''}`}
            />
            <span>
              Gửi lại mã{' '}
              {timeToRequestOtp <= 0 ? '' : Time.MM_SS(timeToRequestOtp)}
            </span>
          </button>

          {/* Bottom Spacer */}
          <div className="h-16 sm:h-20"></div>
        </form>
        {popup.show && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
            <NotificationCard
              message={
                popup.type === 'succeed'
                  ? i18n.t('register_otp_verfied')
                  : popup.type === 'error'
                    ? i18n.t('internal_error')
                    : i18n.t('register_otp_unverified')
              }
              title={
                popup.type === 'succeed'
                  ? i18n.t('auth_succeeded')
                  : popup.type === 'incorrect'
                    ? i18n.t('auth_failed')
                    : i18n.t('error_occured')
              }
              icon={popup.type === 'succeed' ? CheckCircle : XCircle}
              iconBgColor={
                popup.type === 'succeed' ? 'bg-green-500' : 'bg-red-500'
              }
              buttonText={i18n.t('confirm')}
              onButtonClick={handlePopupClick}
            ></NotificationCard>
          </div>
        )}
      </div>
    </LoadingOverlay>
  )
}
