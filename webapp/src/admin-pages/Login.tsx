import React, { useState } from 'react'
import { Eye, EyeOff, LogIn } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../components/Button'
import { InputField } from '../components/InputField'
import { authService, AuthService } from '../services/auth'
import { LocalStorage } from '../services/storage/local'
import { connectWebSocketAfterLogin } from '../hooks/useWebSocketNotification'

const Login: React.FC = () => {
  const navigate = useNavigate()
  // State for form inputs and password visibility toggle
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Specific colors from the design
  const cardBg = '#F9F3DA' // The light beige background of the card
  const cardBorder = '#E8E0C5' // The slightly darker border of the card

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate inputs
    const usernameValidation = AuthService.validateEmailOrUsername(username)
    if (usernameValidation.isErr()) {
      setError('Tên đăng nhập không hợp lệ')
      return
    }

    // Admin password does not seem to have these constraints
    // const passwordValidation = AuthService.validatePassword(password)
    // if (passwordValidation.isErr()) {
    //   setError('Mật khẩu không hợp lệ')
    //   return
    // }

    setIsLoading(true)

    const result = await authService.logIn(username, password)

    setIsLoading(false)

    if (result.isOk()) {
      // Store auth data
      LocalStorage.inst.auth = result.value.data
      // Connect to WebSocket for real-time notifications
      connectWebSocketAfterLogin()
      // Navigate to admin dashboard or home
      navigate('/admin')
    } else {
      // Handle error
      switch (result.error.type) {
        case 'incorrect-credentials':
          setError('Tên đăng nhập hoặc mật khẩu không đúng')
          break
        case 'network-error':
          setError('Lỗi kết nối mạng')
          break
        default:
          setError('Đăng nhập thất bại')
      }
    }
  }

  return (
    <div className="flex min-h-screen bg-white font-sans text-gray-800">
      {/* Left Side - Image Background */}
      {/* Note: On small screens (mobile), this side is hidden to focus on the form. */}
      <div className="hidden md:block md:w-1/2 relative overflow-hidden bg-orange-100">
        {/* Since I don't have the exact image file, I'm using an Unsplash placeholder 
          that closely matches the theme and color palette (healthy food on orange bg).
          Replace 'src' with your actual image path.
        */}
        <img
          src="https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?q=80&w=2070&auto=format&fit=crop"
          alt="Healthy food background"
          className="absolute inset-0 h-full w-full object-cover"
        />
      </div>

      {/* Right Side - Login Form Container */}
      <main className="w-full md:w-1/2 flex items-center justify-center p-4">
        {/* The Login Card */}
        <div
          className="w-full max-w-[450px] rounded-lg shadow-[0_4px_10px_rgba(0,0,0,0.1)] p-8 md:p-10"
          style={{ backgroundColor: cardBg, border: `1px solid ${cardBorder}` }}
        >
          {/* Logo / Brand Title */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold">
              <span className="text-[#C3485C]">S</span>
              <span className="text-[#f7b686]">hop</span>
              <span className="text-[#C3485C]">S</span>
              <span className="text-[#f7b686]">ense</span> Admin
            </h1>
          </div>

          {/* "Đăng nhập" Heading */}
          <h2 className="text-xl font-bold text-center mb-8 text-[#C3485C]">
            Đăng nhập
          </h2>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-3 bg-red-100 border border-red-300 rounded text-red-700 text-sm text-center">
              {error}
            </div>
          )}

          {/* Form Fields */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username Field */}
            <InputField
              id="username"
              type="text"
              label="Tên đăng nhập"
              placeholder="Nhập tên đăng nhập"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

            {/* Password Field with Visibility Toggle */}
            <div className="relative">
              <InputField
                id="password"
                type={showPassword ? 'text' : 'password'}
                label="Mật khẩu"
                placeholder="Nhập mật khẩu"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                inputClassName="pr-12"
              />
              {/* Eye Icon Toggle Button */}
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 flex items-center px-4 text-gray-400 hover:text-gray-600 focus:outline-none"
                style={{ top: '30px' }}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant={isLoading ? 'disabled' : 'primary'}
              size="fit"
              icon={isLoading ? undefined : LogIn}
              className="mt-8"
            >
              {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
            </Button>
          </form>
        </div>
      </main>
    </div>
  )
}

export default Login
