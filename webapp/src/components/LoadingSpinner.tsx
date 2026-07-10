import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  showText?: boolean
  text?: string
}

const sizeClasses = {
  sm: 'size-4',
  md: 'size-8',
  lg: 'size-12'
}

export function LoadingSpinner({ 
  size = 'md', 
  className = '', 
  showText = false,
  text = 'Đang tải...'
}: LoadingSpinnerProps) {
  return (
    <div className={`flex flex-col items-center justify-center gap-2 ${className}`}>
      <Loader2 className={`${sizeClasses[size]} animate-spin text-[#C3485C]`} />
      {showText && (
        <p className="text-sm text-gray-600">{text}</p>
      )}
    </div>
  )
}

