import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RefreshCcw } from 'lucide-react'
import { Button } from '../../components/Button'
import { OPTInput } from '../../components/OPTInput'

export default function ForgotPasswordAuthentication() {
  const navigate = useNavigate()
  const [otpCode, setOtpCode] = useState('')

  const handleOtpComplete = (code: string) => {
    setOtpCode(code)
    console.log('OTP Entered:', code)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (otpCode.length === 6) {
      console.log('Submitting OTP:', otpCode)
      // Add actual verification logic here
      navigate('/auth/forgot-password-new-password')
    } else {
      alert('Vui lòng nhập đủ 6 số.')
    }
  }

  return (
    <>
      {/* Header: Xác thực email */}
      <div className="mb-6 sm:mb-8 text-center">
        {/* Xác thực email Text */}
        <h1 className="text-2xl sm:text-2xl md:text-3xl font-bold text-[#C3485C]">Xác thực email</h1>
      </div>

      <form onSubmit={handleSubmit} className="max-w-sm mx-auto">
        {/* Description Text */}
        <p className="mb-6 text-justify text-sm leading-relaxed text-gray-700">
          Chúng tôi vừa gửi mã xác nhận 6 chữ số đến email của bạn (nếu
          email đã được đăng ký). Bạn vui lòng nhập mã để tiếp tục
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
