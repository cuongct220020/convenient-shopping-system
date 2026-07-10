import { Link, To } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'

interface BackButtonProps {
  to?: To
  text?: string
  className?: string
  state?: unknown
  onClick?: () => void
}

export const BackButton = ({
  to = '/',
  text = '',
  className = '',
  state
}: BackButtonProps) => {
  return (
    <div className="flex items-center px-0 py-2">
      <Link
        to={to}
        state={state}
        className={`flex items-center text-sm font-bold text-[#C3485C] hover:opacity-80 ${className}`}
      >
        <ChevronLeft size={20} strokeWidth={3} />
        <span className="ml-1">{text}</span>
      </Link>
    </div>
  )
}
