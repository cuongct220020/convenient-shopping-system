import { Link } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'

interface BackButtonProps {
  to?: string
  text?: string
  className?: string
  onClick?: () => void
}

export const BackButton = ({
  to = '/',
  text = '',
  className = '',
  onClick
}: BackButtonProps) => {
  return (
    <div className="flex items-center px-0 py-2">
      {onClick ? (
        <button
          onClick={onClick}
          className={`flex items-center text-sm font-bold text-[#C3485C] hover:opacity-80 ${className}`}
        >
          <ChevronLeft size={20} strokeWidth={3} />
          <span className="ml-1">{text}</span>
        </button>
      ) : (
        <Link
          to={to}
          className={`flex items-center text-sm font-bold text-[#C3485C] hover:opacity-80 ${className}`}
        >
          <ChevronLeft size={20} strokeWidth={3} />
          <span className="ml-1">{text}</span>
        </Link>
      )}
    </div>
  )
}
