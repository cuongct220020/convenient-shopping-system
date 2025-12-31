import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'
import { BackButton } from '../../../components/BackButton';
import { Button } from '../../../components/Button';
import { OPTInput } from '../../../components/OPTInput';
import { RefreshCcw } from 'lucide-react';

const OldPassword = () => {
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
      navigate('/main/profile/new-password')
    } else {
      alert('Vui lòng nhập đủ 6 số.')
    }
  }

  return (
    <div className="flex-1 p-5 bg-white overflow-y-auto max-w-sm mx-auto w-full">
      {/* Back Navigation */}
      {/* Assumes the previous route was LoginInformation */}
      <BackButton to="/main/profile/old-password" text="Quay lại" className="mb-6" />

      {/* Screen Title */}
      <h1 className="text-2xl font-bold text-black mb-2">
        Đổi mật khẩu
      </h1>

      {/* Description */}
      <form onSubmit={handleSubmit} className="max-w-sm mx-auto">
        {/* Description Text */}
        <p className="mb-6 text-justify text-sm leading-relaxed text-gray-700">
          Vui lòng nhập mã xác nhận 6 chữ số vừa được gửi đến email của bạn để đặt lại mật khẩu.
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
    </div>
  );
};

export default OldPassword;