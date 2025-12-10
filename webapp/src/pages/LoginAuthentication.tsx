import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { RefreshCcw } from 'lucide-react' // Importing an icon for the resend button
import loginBg from '../assets/login-bg.png'
import { Button } from '../components/Button'
import { BackButton } from '../components/BackButton'
import { OtpInput } from '../components/OtpInput'

export default function LoginAuthentication() {
  const navigate = useNavigate()
  const location = useLocation()
  const [otpCode, setOtpCode] = useState('')

  // Retrieve username passed from the Login page state, or use a placeholder
  // In a real app, ensure you handle the case where state is undefined safely.
  const username = location.state?.username || 'User'

  const handleOtpComplete = (code: string) => {
    setOtpCode(code)
    console.log('OTP Entered:', code)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (otpCode.length === 6) {
      console.log('Submitting OTP:', otpCode)
      // Add actual verification logic here
      alert(`Xác thực thành công cho tài khoản: ${username}`)
      navigate('/admin')
    } else {
      alert('Vui lòng nhập đủ 6 số.')
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
              {/* Header: Xác thực tài khoản */}
              <div className="mb-6 sm:mb-8 text-center">
                {/* Xác thực tài khoản Text */}
                <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-[#c93045]">Xác thực tài khoản</h1>
              </div>

              <form onSubmit={handleSubmit} className="max-w-sm mx-auto">
                {/* Description Text */}
                <p className="mb-6 text-justify text-sm leading-relaxed text-gray-700">
                  Xin chào{' '}
                  <span className="font-bold text-[#c93045]">username</span>, bạn
                  đã đăng nhập thành công. Bạn cần xác nhận tài khoản để tiếp tục
                  sử dụng ứng dụng. Vui lòng nhập mã 6 chữ số được gửi đến email
                  của bạn.
                </p>

                {/* OTP Input Component */}
                <div className="mb-8 px-2">
                  <OtpInput length={6} onComplete={handleOtpComplete} />
                </div>

                {/* Submit Button */}
                <div className="mb-6">
                  <Button type="submit" variant="primary" size="fit">
                    Xác nhận
                  </Button>
                </div>

                {/* Resend Timer */}
                <button
                  type="button"
                  className="flex w-full items-center justify-center text-sm text-gray-500 transition-colors hover:text-[#c93045]"
                >
                  <RefreshCcw size={16} className="mr-2" />
                  <span>Gửi lại mã 00:59</span>
                </button>

                {/* Bottom Spacer */}
                <div className="h-16 sm:h-20"></div>
              </form>
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
