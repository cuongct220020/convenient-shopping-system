import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/Button'

// Demo component showing the styled error page
export default function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-6 text-center">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">Lỗi</h1>
          <p className="text-xl text-gray-600">
            Hệ thống không tìm thấy địa chỉ bạn muốn truy cập. Vui lòng quay lại
            trang chủ hoặc thử lại sau.
          </p>
        </div>

        <Button
          variant="secondary"
          type="button"
          size="fit"
          onClick={() => navigate('/auth/login')}
        >
          Về trang chủ
        </Button>
      </div>
    </div>
  )
}
