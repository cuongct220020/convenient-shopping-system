import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserPlus, LogIn, CheckCircle, XCircle } from 'lucide-react'
import { Button } from '../../components/Button'
import { InputField } from '../../components/InputField'
import { NotificationCard } from '../../components/NotificationCard'
import { ok, err, Result } from 'neverthrow'
import { i18nKeys } from '../../utils/i18n/keys'
import { authService, AuthService } from '../../services/auth'
import { i18n } from '../../utils/i18n/i18n'
import { LoadingOverlay } from '../../components/Loading'

const FormFields = [
  'name',
  'email',
  'username',
  'password',
  'confirmPassword'
] as const
type FormField = (typeof FormFields)[number]
type FormData = Record<FormField, string>
type FormErrors = Record<FormField, Result<void, i18nKeys>>
type SelectedFields = Record<FormField, boolean>

function validateConfirmPassword(
  pass: string,
  confirm: string
): Result<void, i18nKeys> {
  if (!confirm.trim()) {
    return err('empty_confirm_password')
  }
  if (pass !== confirm) {
    return err('invalid_confirm_password')
  }
  return ok()
}

function validateField(
  field: FormField,
  form: FormData
): Result<void, i18nKeys> {
  switch (field) {
    case 'name':
      return AuthService.validateFullName(form.name).map(() => {})
    case 'email':
      return AuthService.validateEmail(form.email)
    case 'username':
      return AuthService.validateUsername(form.username)
    case 'password':
      return AuthService.validatePassword(form.password)
    case 'confirmPassword':
      return validateConfirmPassword(form.password, form.confirmPassword)
    default:
      throw new Error(`Unknown field: ${field}`)
  }
}

export default function Register() {
  const navigate = useNavigate()
  // State for form fields
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })

  const [errors, setErrors] = useState<FormErrors>({
    name: ok(),
    email: ok(),
    username: ok(),
    password: ok(),
    confirmPassword: ok()
  })

  const [selected, setSelected] = useState<SelectedFields>({
    name: false,
    confirmPassword: false,
    email: false,
    password: false,
    username: false
  })
  const [loading, setLoading] = useState(false)
  const [showPopup, setShowPopup] = useState({
    yes: false,
    title: '' as i18nKeys,
    message: ''
  })

  const handleChange = (field: FormField, value: string) => {
    const newFormData = { ...formData, [field]: value }
    setFormData(newFormData)
    if (selected[field]) {
      setErrors({ ...errors, [field]: validateField(field, newFormData) })
    }
  }

  const handleBlur = (field: FormField) => {
    setSelected({ ...selected, [field]: true })
    setErrors({ ...errors, [field]: validateField(field, formData) })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    let errorOccured = false
    const newError = { ...errors }
    const newSelected = { ...selected }
    for (const field of FormFields) {
      const validation = validateField(field, formData)
      errorOccured ||= validation.isErr()
      newError[field] = validation
      newSelected[field] = true
    }
    setErrors(newError)
    setSelected(newSelected)

    if (errorOccured) {
      return
    }
    console.log('Registration attempt with:', formData)
    setLoading(true)
    const registered = authService.register({
      email: formData.email,
      username: formData.username,
      password: formData.password,
      ...AuthService.validateFullName(formData.name).unwrapOr({
        firstName: '',
        lastName: ''
      })
    })
    registered.match(
      () => {
        setLoading(false)
        setShowPopup({
          yes: true,
          message: i18n.t('register_login_to_continue'),
          title: 'register_success_title'
        })
      },
      (err) => {
        setLoading(false)
        switch (err.type) {
          default:
            setShowPopup({
              yes: true,
              message: i18n.t('internal_error'),
              title: 'error_occured'
            })
        }
      }
    )
  }

  return (
    <LoadingOverlay isLoading={loading}>
      <div className="flex flex-1 flex-col items-center ">
        {/* Header: Đăng ký */}
        <div className="mb-6 text-center sm:mb-8">
          {/* Đăng ký Text */}
          <h1 className="text-2xl font-bold text-[#C3485C] sm:text-2xl md:text-3xl">
            Đăng ký tài khoản
          </h1>
        </div>

        {/* Form with max-width constraint */}
        <form
          onSubmit={handleSubmit}
          className="mx-auto w-full max-w-sm space-y-4 sm:space-y-5"
        >
          <div>
            <InputField
              id="fullname"
              label="Họ và tên"
              required={true}
              placeholder="Nhập họ và tên"
              value={formData.name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                handleChange('name', e.target.value)
              }
              onBlur={() => handleBlur('name')}
              error={errors.name.isErr() ? i18n.t(errors.name.error) : null}
            />
          </div>
          <div>
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
              error={errors.email.isErr() ? i18n.t(errors.email.error) : null}
            />
          </div>

          <div>
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
              error={
                errors.username.isErr() ? i18n.t(errors.username.error) : null
              }
            />
          </div>

          <div>
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
              error={
                errors.password.isErr() ? i18n.t(errors.password.error) : null
              }
            />
          </div>

          <div>
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
              error={
                errors.confirmPassword.isErr()
                  ? i18n.t(errors.confirmPassword.error)
                  : null
              }
            />
          </div>

          {/* Register Button */}
          <Button variant="primary" icon={UserPlus} size="fit" type="submit">
            Đăng ký tài khoản
          </Button>
        </form>

        {/* Divider */}
        <div className="relative mx-auto my-4 flex max-w-sm items-center text-sm sm:my-5">
          <div className="flex-1 border-t border-gray-300"></div>
          <span className="px-3 text-gray-400 sm:px-4">hoặc</span>
          <div className="flex-1 border-t border-gray-300"></div>
        </div>

        {/* Login Button */}
        <div className="mx-auto max-w-sm">
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
        <div className="h-16 sm:h-20"></div>

        {/* Popup Overlay */}
        {showPopup.yes &&
          (showPopup.title === 'register_success_title' ? (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
              <NotificationCard
                title={i18n.t(showPopup.title)}
                message={showPopup.message}
                icon={CheckCircle}
                iconBgColor="bg-green-500"
                buttonText="Đăng nhập"
                buttonIcon={LogIn}
                onButtonClick={() => {
                  navigate('/auth/login')
                  setShowPopup((prev) => ({ ...prev, yes: false }))
                }}
              />
            </div>
          ) : (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
              <NotificationCard
                title={i18n.t(showPopup.title)}
                message={showPopup.message}
                icon={XCircle}
                iconBgColor="bg-red-500"
                buttonText={i18n.t('confirm')}
                onButtonClick={() => {
                  setShowPopup((prev) => ({ ...prev, yes: false }))
                }}
              />
            </div>
          ))}
      </div>
    </LoadingOverlay>
  )
}
