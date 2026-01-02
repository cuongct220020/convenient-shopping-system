import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, CheckCircle, LogIn, XCircle } from 'lucide-react'
import { InputField } from '../../components/InputField'
import { Button } from '../../components/Button'
import { NotificationCard } from '../../components/NotificationCard'
import { LoadingOverlay } from '../../components/Loading'
import { err, ok, Result } from 'neverthrow'
import { i18nKeys } from '../../utils/i18n/keys'
import { authService, AuthService } from '../../services/auth'
import { i18n } from '../../utils/i18n/i18n'
import { SessionStorage } from '../../services/storage/session'
import { LocalStorage } from '../../services/storage/local'
import { useIsMounted } from '../../hooks/useIsMounted'

const FormFields = ['pwd', 'cfPwd']
type FormField = (typeof FormFields)[number]
type FormData = Record<FormField, string>
type FormError = Record<FormField, Result<void, i18nKeys>>
type SelectedFields = Record<FormField, boolean>
type PopupState = {
  show: boolean
  type: 'error' | 'succeed' | 'expired-otp'
}
type PopupProps = {
  onConfirmed?: () => unknown
  onLogin?: () => unknown
} & PopupState

function validateCfPwd(cfPwd: string, pwd: string): Result<void, i18nKeys> {
  if (!cfPwd.trim()) {
    return err('empty_confirm_password')
  }
  if (cfPwd !== pwd) {
    return err('invalid_confirm_password')
  }
  return ok()
}

function validateField(
  field: FormField,
  form: FormData
): Result<void, i18nKeys> {
  switch (field) {
    case 'pwd':
      return AuthService.validatePassword(form[field])
    case 'cfPwd':
      return validateCfPwd(form.cfPwd, form.pwd)
    default:
      throw new Error('Unimplemented')
  }
}

function Popup({ type, show, onConfirmed, onLogin }: PopupProps): JSX.Element {
  if (!show) return <></>
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      {type === 'error' ? (
        <NotificationCard
          title={i18n.t('error_occured')}
          message={i18n.t('internal_error')}
          icon={XCircle}
          iconBgColor={'bg-red-500'}
          buttonText={i18n.t('confirm')}
          onButtonClick={onConfirmed}
          buttonVariant="primary"
        />
      ) : type === 'expired-otp' ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <NotificationCard
            title={i18n.t('auth_failed')}
            message={i18n.t('otp_expired')}
            icon={XCircle}
            iconBgColor={'bg-red-500'}
            buttonText={i18n.t('confirm')}
            onButtonClick={onConfirmed}
            buttonVariant="primary"
          />
        </div>
      ) : (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <NotificationCard
            title={i18n.t('reset_password_success_title')}
            message={i18n.t('reset_password_login_to_continue')}
            icon={CheckCircle}
            iconBgColor={'bg-green-500'}
            buttonText={i18n.t('confirm')}
            onButtonClick={onConfirmed}
            buttonVariant="secondary"
            button2Icon={LogIn}
            button2Text={'Đăng nhập'}
            onButton2Click={onLogin}
            button2Variant="primary"
          />
        </div>
      )}
    </div>
  )
}

export default function ForgotPasswordNewPassword() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<FormData>({
    pwd: '',
    cfPwd: ''
  })
  const [errors, setErrors] = useState<FormError>({
    pwd: ok(),
    cfPwd: ok()
  })
  const [selected, setSelected] = useState<SelectedFields>({
    pwd: false,
    cfPwd: false
  })
  const [showPopup, setShowPopup] = useState<PopupState>({
    show: false,
    type: 'error'
  })
  const [isLoading, setIsLoading] = useState(false)
  const isMounted = useIsMounted()
  const sessionOtp = SessionStorage.inst.resetPasswordOtp
  const email = LocalStorage.inst.emailRequestingOtp

  const handleFormChange = (
    field: FormField,
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value
    const newFormData = { ...formData, [field]: value }
    setFormData(newFormData)
    if (selected[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: validateField(field, newFormData)
      }))
    }
  }

  const handleFieldBlur = (field: FormField) => {
    setSelected((prev) => ({ ...prev, [field]: true }))
    setErrors((prev) => ({
      ...prev,
      [field]: validateField(field, formData)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    if (!email || !sessionOtp) {
      console.error(
        'We should not be in this page because email or otp is not saved yet'
      )
      navigate('/auth/login')
      return
    }
    e.preventDefault()

    let hasErr = false
    for (const field of FormFields) {
      const validation = validateField(field, formData)
      hasErr ||= validation.isErr()
      setErrors((prev) => ({ ...prev, [field]: validation }))
      setSelected((prev) => ({ ...prev, [field]: true }))
    }
    if (hasErr) return
    setIsLoading(true)

    const response = await authService.resetPassword({
      email,
      newPassword: formData.pwd,
      otpCode: sessionOtp
    })
    if (!isMounted.current) return
    setIsLoading(false)
    response
      .andTee(() => {
        LocalStorage.inst.emailRequestingOtp = null
        SessionStorage.inst.resetPasswordOtp = null
        setShowPopup({ show: true, type: 'succeed' })
      })
      .mapErr((e) => {
        switch (e.type) {
          case 'incorrect-or-expired-otp':
            setShowPopup({
              show: true,
              type: 'expired-otp'
            })
            break
          default:
            setShowPopup({
              show: true,
              type: 'error'
            })
        }
      })
  }

  return (
    <LoadingOverlay isLoading={isLoading}>
      <div className="flex flex-1 flex-col">
        {/* Header: Đặt lại mật khẩu */}
        <div className="mb-6 text-center sm:mb-8">
          {/* Đặt lại mật khẩu Text */}
          <h1 className="text-2xl font-bold text-[#C3485C] sm:text-2xl md:text-3xl">
            Đặt lại mật khẩu
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Xin chào <span className="font-semibold">Username</span>, vui lòng
            nhập mật khẩu bạn muốn thay đổi.
          </p>
        </div>

        {/* Form with max-width constraint */}
        <form
          onSubmit={handleSubmit}
          className="mx-auto w-full max-w-sm space-y-4 sm:space-y-5"
        >
          <div>
            <InputField
              id="password"
              type="password"
              label="Mật khẩu mới"
              placeholder="Nhập mật khẩu"
              value={formData.pwd}
              onChange={(e) => handleFormChange('pwd', e)}
              onBlur={() => handleFieldBlur('pwd')}
              error={errors.pwd.isErr() ? i18n.t(errors.pwd.error) : null}
            />
          </div>

          <div>
            <InputField
              id="confirm-password"
              type="password"
              label="Xác nhận mật khẩu mới"
              placeholder="Nhập lại mật khẩu"
              value={formData.cfPwd}
              onChange={(e) => handleFormChange('cfPwd', e)}
              onBlur={() => handleFieldBlur('cfPwd')}
              error={errors.cfPwd.isErr() ? i18n.t(errors.cfPwd.error) : null}
            />
          </div>

          <Button
            variant={
              FormFields.every((e) => validateField(e, formData).isOk())
                ? 'primary'
                : 'disabled'
            }
            icon={Send}
            size="fit"
            type="submit"
          >
            Xác nhận
          </Button>
        </form>

        {/* Bottom Spacer for scrolling over background */}
        <div className="h-16 sm:h-20"></div>

        {/* Popup Overlay */}
        <Popup
          {...showPopup}
          onConfirmed={() => setShowPopup({ show: false, type: 'error' })}
          onLogin={() => {
            navigate('/auth/login')
          }}
        ></Popup>
      </div>
    </LoadingOverlay>
  )
}
