import { useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'
import loginBg from '../assets/login-bg.png'
import { Button } from '../components/Button'

export default function ForgotPasswordNotification() {
  const navigate = useNavigate()

  const handleClose = () => {
    navigate('/user/login')
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
          {/* Header: No Back Button - this is a notification page */}

          {/* Content Area - Centered */}
          <div className="no-scrollbar relative z-10 flex-1 overflow-y-auto flex items-center justify-center">
            <div className="px-4 sm:px-6 md:px-8 w-full max-w-sm">
              {/* Header: Mật khẩu đã thay đổi */}
              <div className="mb-6 sm:mb-8 text-center">
                {/* Mật khẩu đã thay đổi Text */}
                <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-[#c93045]">Mật khẩu đã thay đổi</h1>
              </div>

              {/* Success Card */}
              <div className="rounded-2xl bg-white p-8 text-center shadow-lg border border-gray-100">
                {/* Success Icon */}
                <div className="mb-6 flex justify-center">
                  <div className="flex size-20 items-center justify-center rounded-full bg-green-500">
                    <CheckCircle size={48} className="text-white" strokeWidth={2.5} />
                  </div>
                </div>

                {/* Message */}
                <p className="mb-8 text-sm leading-relaxed text-gray-600">
                  Mật khẩu đặt lại thành công, bạn vui lòng đăng nhập bằng mật khẩu
                  mới
                </p>

                {/* Close Button */}
                <Button variant="primary" size="fit" onClick={handleClose}>
                  Đóng
                </Button>
              </div>

              {/* Bottom Spacer */}
              <div className="h-16 sm:h-20"></div>
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
