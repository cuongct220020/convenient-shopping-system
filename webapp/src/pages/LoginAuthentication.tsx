import { useState } from 'react'
import { useLocation } from 'react-router-dom' // Removed useNavigate
import { RefreshCcw } from 'lucide-react' // Importing an icon for the resend button
import loginBg from '../assets/login-bg.png'
import { Button } from '../components/Button'
import { BackButton } from '../components/BackButton'
import { OtpInput } from '../components/OtpInput'

export default function LoginAuthentication() {
  // const navigate = useNavigate() // Removed this line
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
      // navigate('/dashboard');
    } else {
      alert('Vui lòng nhập đủ 6 số.')
    }
  }

  return (
    // Reusing the main container styling from Login.tsx for consistency
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-100 font-sans">
      {/* Mobile Container */}
      <div className="relative flex h-[812px] w-[375px] flex-col overflow-hidden bg-white shadow-2xl">
        {/* Header: Back Button */}
        <div className="my-4">
          {/* Using existing BackButton component */}
          <BackButton to="/login" text="Quay lại" />
        </div>

        {/* Scrollable Content Area */}
        <div className="no-scrollbar relative z-10 flex-1 overflow-y-auto">
          <div className="px-6 pb-8 pt-4">
            <form onSubmit={handleSubmit}>
              {/* Title */}
              <h2 className="mb-6 text-center text-3xl font-bold text-[#c93045]">
                Xác thực tài khoản
              </h2>

              {/* Description Text */}
              {/* Using text-justify to match the block text look in image_0.png */}
              <p className="mb-4 text-justify text-sm leading-relaxed text-gray-700">
                Xin chào{' '}
                <span className="font-bold text-[#c93045]">username</span>, bạn
                đã đăng nhập thành công. Bạn cần xác nhận tài khoản để tiếp tục
                sử dụng ứng dụng. Vui lòng nhập mã 6 chữ số được gửi đến email
                của bạn.
              </p>

              {/* New OTP Input Component */}
              <div className="mb-8 px-2">
                <OtpInput length={6} onComplete={handleOtpComplete} />
              </div>

              {/* Submit Button */}
              {/* Using existing Button component with fit size */}
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
              <div className="h-20"></div>
            </form>
          </div>
        </div>

        {/* Background Image Decoration (Bottom) - Same as Login page */}
        <div className="pointer-events-none absolute inset-x-0 bottom-0 z-0 h-80">
          <div className="absolute inset-0 z-10 bg-gradient-to-t from-white/10 via-white/40 to-white"></div>
          <img
            src={loginBg}
            alt="Food Background"
            className="size-full object-cover opacity-70"
          />
        </div>
      </div>
    </div>
  )
}
