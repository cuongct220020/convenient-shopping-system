import { useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'
import { Button } from '../components/Button'

export default function RegisterNotification() {
  const navigate = useNavigate()

  const handleClose = () => {
    navigate('/login')
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gray-100 font-sans">
      {/* Mobile Container */}
      <div className="relative flex h-[812px] w-[375px] items-center justify-center bg-gray-700 px-6">
        {/* Success Card */}
        <div className="w-full max-w-sm rounded-2xl bg-white p-8 text-center shadow-2xl">
          {/* Title */}
          <h2 className="mb-6 text-xl font-bold text-gray-800">
            Đăng ký thành công
          </h2>

          {/* Success Icon */}
          <div className="mb-6 flex justify-center">
            <div className="flex size-20 items-center justify-center rounded-full bg-green-500">
              <CheckCircle size={48} className="text-white" strokeWidth={2.5} />
            </div>
          </div>

          {/* Message */}
          <p className="mb-8 text-sm leading-relaxed text-gray-600">
            Xin chào <span className="font-semibold">Username</span>, bạn đã
            đăng ký thành công, vui lòng đăng nhập để tiếp tục.
          </p>

          {/* Close Button */}
          <Button variant="primary" size="fit" onClick={handleClose}>
            Đóng
          </Button>
        </div>
      </div>
    </div>
  )
}
