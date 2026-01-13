import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogIn, UserPlus, XCircle, Check } from 'lucide-react'
import { InputField } from '../../components/InputField'
import { Button } from '../../components/Button'
import { authService, AuthService } from '../../services/auth'
import { ok, Result } from 'neverthrow'
import { i18n } from '../../utils/i18n/i18n'
import { i18nKeys } from '../../utils/i18n/keys'
import { LoadingOverlay } from '../../components/Loading'
import { NotificationCard } from '../../components/NotificationCard'
import { useIsMounted } from '../../hooks/useIsMounted'
import { LocalStorage } from '../../services/storage/local'
import { authController } from '../../controllers/authController'
import { connectWebSocketAfterLogin } from '../../hooks/useWebSocketNotification'

export default function Login() {
  const navigate = useNavigate()
  // State management for form inputs
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<{
    email: Result<void, i18nKeys>
    password: Result<void, i18nKeys>
  }>({
    email: ok(),
    password: ok()
  })
  const [touched, setTouched] = useState<{
    email: boolean
    password: boolean
  }>({
    email: false,
    password: false
  })
  const [isLoading, setIsLoading] = useState(false)
  const [showPopup, setShowPopup] = useState({
    yes: false,
    title: '' as i18nKeys,
    message: ''
  })
  const isMounted = useIsMounted()

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setEmail(value)

    if (touched.email) {
      setErrors((prev) => ({
        ...prev,
        email: AuthService.validateEmailOrUsername(value)
      }))
    }
  }

  const handleEmailBlur = () => {
    setTouched((prev) => ({ ...prev, email: true }))
    setErrors((prev) => ({
      ...prev,
      email: AuthService.validateEmailOrUsername(email)
    }))
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setPassword(value)

    if (touched.password) {
      setErrors((prev) => ({
        ...prev,
        password: AuthService.validatePassword(value)
      }))
    }
  }

  const handlePasswordBlur = () => {
    setTouched((prev) => ({ ...prev, password: true }))
    setErrors((prev) => ({
      ...prev,
      password: AuthService.validatePassword(password)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    const emailError = AuthService.validateEmailOrUsername(email)
    const passwordError = AuthService.validatePassword(password)

    setErrors({
      email: emailError,
      password: passwordError
    })

    setTouched({
      email: true,
      password: true
    })

    if (emailError.isErr() || passwordError.isErr()) {
      return
    }
    console.info('Login attempt with:', email)
    setIsLoading(true)
    const response = await authService.logIn(email, password)
    if (!isMounted.current) {
      console.info(
        'Login component was unmounted before async request finishes'
      )
      return
    }
    response
      .map((body) => {
        authController.saveUserAuth(body.data)
        // Connect to WebSocket for real-time notifications
        connectWebSocketAfterLogin()
        setIsLoading(false)
        navigate('/main/profile')
      })
      .mapErr(async (e) => {
        setIsLoading(false)
        console.error('Login: ', e)
        switch (e.type) {
          case 'unverfified': {
            // TODO: email must be a real email
            const realEmail = AuthService.validateEmail(email).match(
              () => email,
              () => 'notAnEmail@gmail.com'
            )
            authService.sendOtpRequest('register', realEmail)
            LocalStorage.inst.emailRequestingOtp = realEmail
            navigate('/auth/login-authentication')
            break
          }
          case 'network-error':
            setShowPopup({
              title: 'network_error',
              message: e.desc ?? i18n.t('internal_error'),
              yes: true
            })
            break
          case 'incorrect-credentials':
            setShowPopup({
              title: 'incorrect_credentials',
              message: i18n.t('recheck_credentials'),
              yes: true
            })
            break
          default:
            setShowPopup({
              title: 'error_occured',
              message: i18n.t('internal_error'),
              yes: true
            })
        }
      })
  }

  return (
    <LoadingOverlay isLoading={isLoading}>
      <div className="flex flex-1 flex-col items-center ">
        {/* Logo & Header: ShopSense above Đăng nhập */}
        <div className="mb-6 text-center sm:mb-8">
          {/* ShopSense Text with precise S coloring */}
          <h1 className="mb-3 text-3xl font-bold sm:mb-4 sm:text-3xl md:text-4xl">
            <span className="text-[#C3485C]">S</span>
            <span className="text-[#f7b686]">hop</span>
            <span className="text-[#C3485C]">S</span>
            <span className="text-[#f7b686]">ense</span>
          </h1>

          {/* Đăng nhập Text */}
          <h2 className="text-2xl font-bold text-[#C3485C] sm:text-2xl md:text-3xl">
            Đăng nhập
          </h2>
        </div>

        {/* Login Form with max-width constraint */}
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-sm space-y-4 px-3 sm:space-y-5"
        >
          <div>
            <InputField
              id="email-username"
              label="Email"
              subLabel="Tên đăng nhập"
              placeholder="Nhập email hoặc tên đăng nhập"
              value={email}
              onChange={handleEmailChange}
              onBlur={handleEmailBlur}
              error={errors.email.isErr() ? i18n.t(errors.email.error) : null}
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
              error={
                errors.password.isErr() ? i18n.t(errors.password.error) : null
              }
            />
          </div>

          <div className="text-right">
            <Link
              to="/auth/forgot-password-email"
              className="text-xs font-bold text-[#C3485C] hover:underline sm:text-sm"
            >
              Quên mật khẩu?
            </Link>
          </div>

          <Button
            variant={isLoading ? 'disabled' : 'primary'}
            icon={LogIn}
            size="fit"
            type="submit"
          >
            Đăng nhập
          </Button>
        </form>

        {/* Divider */}
        <div className="relative mx-auto my-4 flex max-w-sm items-center text-sm sm:my-5">
          <div className="flex-1 border-t border-gray-300"></div>
          <span className="px-3 text-gray-400 sm:px-4">hoặc</span>
          <div className="flex-1 border-t border-gray-300"></div>
        </div>

        {/* Register Button */}
        <div className="mx-auto max-w-sm">
          <Button
            variant={isLoading ? 'disabled' : 'secondary'}
            icon={UserPlus}
            size="fit"
            onClick={() => navigate('/auth/register')}
          >
            Đăng ký tài khoản
          </Button>
        </div>

        {/* Bottom Spacer for scrolling over background */}
        <div className="h-16 sm:h-20"></div>
      </div>
      {showPopup.yes && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <NotificationCard
            message={showPopup.message}
            title={i18n.t(showPopup.title)}
            icon={XCircle}
            iconBgColor="bg-red-500"
            buttonText={i18n.t('confirm')}
            buttonIcon={Check}
            onButtonClick={() => {
              setShowPopup({
                ...showPopup,
                yes: false
              })
            }}
          ></NotificationCard>
        </div>
      )}
    </LoadingOverlay>
  )
}
