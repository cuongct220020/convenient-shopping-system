import { useEffect, useState } from 'react'
import { Bell, X } from 'lucide-react'
import { createPortal } from 'react-dom'

export interface ToastData {
  id: string
  title: string
  content: string
  groupName?: string
  timestamp: Date
}

interface ToastItemProps {
  toast: ToastData
  onClose: (id: string) => void
}

function ToastItem({ toast, onClose }: ToastItemProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [isExiting, setIsExiting] = useState(false)

  useEffect(() => {
    // Animate in
    setIsVisible(true)

    // Auto-dismiss after 5 seconds
    const timer = setTimeout(() => {
      handleClose()
    }, 5000)

    return () => clearTimeout(timer)
  }, [toast.id])

  const handleClose = () => {
    setIsExiting(true)
    setTimeout(() => {
      onClose(toast.id)
    }, 300)
  }

  const timeAgo = new Intl.RelativeTimeFormat('vi', { numeric: 'auto' }).format(
    Math.floor((toast.timestamp.getTime() - Date.now()) / 1000 / 60),
    'minute'
  )

  return (
    <div
      className={`
        flex items-start gap-3 w-full max-w-sm bg-white rounded-lg shadow-lg border border-gray-200 p-4
        transition-all duration-300 ease-in-out
        ${isVisible && !isExiting ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
      `}
    >
      {/* Icon */}
      <div className="flex-shrink-0 mt-0.5">
        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
          <Bell className="w-5 h-5 text-blue-600" strokeWidth={2} />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-900 truncate">
              {toast.title}
            </p>
            {toast.groupName && (
              <p className="text-xs text-blue-600 mt-0.5">
                {toast.groupName}
              </p>
            )}
          </div>
          <button
            onClick={handleClose}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
          {toast.content}
        </p>
        <p className="text-xs text-gray-400 mt-2">
          {timeAgo}
        </p>
      </div>
    </div>
  )
}

interface ToastContainerProps {
  toasts: ToastData[]
  onClose: (id: string) => void
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return createPortal(
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      <div className="flex flex-col gap-2 pointer-events-auto">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={onClose} />
        ))}
      </div>
    </div>,
    document.body
  )
}
