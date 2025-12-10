import { Link } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'

interface BackButtonProps {
  to?: string
  text?: string
  className?: string
}

export const BackButton = ({
  to = '/',
  text = 'Trang chủ',
  className = ''
}: BackButtonProps) => {
  return (
    <div className="flex items-center px-4 py-2">
      <Link
        to={to}
        className={`flex items-center text-sm font-bold text-[#c93045] hover:opacity-80 ${className}`}
      >
        <ChevronLeft size={20} strokeWidth={3} />
        <span className="ml-1">{text}</span>
      </Link>
    </div>
  )
}
