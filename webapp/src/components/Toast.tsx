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

  return (
    <div
      className={`
        flex items-start gap-3 w-full bg-white rounded-lg shadow-lg border border-gray-200 p-4
        transition-all duration-300 ease-in-out
        ${isVisible && !isExiting ? 'translate-y-0 opacity-100' : 'translate-y-[-20px] opacity-0'}
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
            <p className="text-sm font-semibold text-gray-900">
              {toast.title}
            </p>
          </div>
          <button
            onClick={handleClose}
            className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          {toast.content}
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
    <div className="fixed inset-x-0 top-4 z-50 flex flex-col items-center gap-2 pointer-events-none px-4">
      <div className="flex flex-col items-center gap-2 pointer-events-auto max-w-sm mx-auto w-full">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={onClose} />
        ))}
      </div>
    </div>,
    document.body
  )
}
