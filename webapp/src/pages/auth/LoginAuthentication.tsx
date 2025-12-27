import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { RefreshCcw } from 'lucide-react'
import { Button } from '../../components/Button'
import { OPTInput } from '../../components/OPTInput'

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
      navigate('/auth/login')
    } else {
      alert('Vui lòng nhập đủ 6 số.')
    }
  }

  return (
    <>
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
          Xin chào <span className="font-bold text-[#C3485C]">{username}</span>,
          bạn đã đăng nhập thành công. Bạn cần xác nhận tài khoản để tiếp tục sử
          dụng ứng dụng. Vui lòng nhập mã 6 chữ số được gửi đến email của bạn.
        </p>

        {/* OTP Input Component */}
        <div className="mb-8 px-2">
          <OPTInput length={6} onComplete={handleOtpComplete} />
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
          className="flex w-full items-center justify-center text-sm text-gray-500 transition-colors hover:text-[#C3485C]"
        >
          <RefreshCcw size={16} className="mr-2" />
          <span>Gửi lại mã 00:59</span>
        </button>

        {/* Bottom Spacer */}
        <div className="h-16 sm:h-20"></div>
      </form>
    </>
  )
}
