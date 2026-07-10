import {
  isRouteErrorResponse,
  useNavigate,
  useRouteError
} from 'react-router-dom'
import { Button } from '../../components/Button'

function getUserMessage(error: unknown) {
  if (isRouteErrorResponse(error)) {
    switch (error.status) {
      case 404:
        return 'Trang bạn tìm không tồn tại hoặc đã bị di chuyển.'
      case 401:
        return 'Bạn cần đăng nhập để tiếp tục.'
      case 403:
        return 'Bạn không có quyền truy cập trang này.'
      case 500:
        return 'Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.'
      default:
        return 'Không thể tải trang. Vui lòng thử lại.'
    }
  }

  return 'Đã xảy ra lỗi khi điều hướng.'
}

function getDebugMessage(error: unknown): string {
  if (isRouteErrorResponse(error)) {
    return `${error.status} ${error.statusText}`
  }
  if (error instanceof Error) return error.message
  return 'Unknown error'
}

export default function RouterErrorPage() {
  const error = useRouteError()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-6 text-center">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-gray-900">Có lỗi xảy ra</h1>
          <p className="text-gray-600">{getUserMessage(error)}</p>
        </div>

        {/* Optional: hide in production */}
        <div className="rounded-lg border border-gray-200 bg-gray-100 p-3">
          <p className="break-words text-xs italic text-gray-700">
            {getDebugMessage(error)}
          </p>
        </div>

        <Button
          variant="secondary"
          size="fit"
          onClick={() => navigate('/auth/login')}
        >
          Quay về trang chính
        </Button>
      </div>
    </div>
  )
}
