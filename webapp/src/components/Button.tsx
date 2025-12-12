import { ReactNode } from 'react'

interface ButtonProps {
  children?: ReactNode
  onClick?: () => void
  variant?:
    | 'primary'
    | 'secondary'
    | 'text'
    | 'icon'
    | 'danger'
  icon?: React.ComponentType<{ size?: number | string; className?: string }>
  className?: string
  size?: 'full' | 'fit' | 'auto'
  type?: 'button' | 'submit' | 'reset'
}

/**
 * Button Component
 * A reusable button component with different variants and sizes
 */
export const Button = ({
  children,
  onClick,
  variant = 'primary',
  icon: Icon,
  className = '',
  size = 'full',
  type = 'button'
}: ButtonProps) => {
  const sizes: Record<string, string> = {
    full: 'w-full',
    fit: 'w-fit px-6 mx-auto', // Fits content with horizontal padding and centers
    auto: 'w-auto px-6 mx-auto' // Auto width with horizontal padding and centers
  }

  // For buttons with only icons, use square padding and minimal sizing
  const isIconOnly = !children && Icon

  const baseStyle =
    isIconOnly
      ? `${size === 'fit' ? 'w-fit' : size === 'auto' ? 'w-auto' : 'w-full'} py-3 px-3 rounded-xl font-bold text-sm flex items-center justify-center transition-all duration-200 active:scale-95`
      : `${sizes[size]} py-3 rounded-xl font-bold text-sm flex items-center justify-center transition-all duration-200 active:scale-95`

  const variants: Record<string, string> = {
    primary:
      'bg-[#C3485C] text-white hover:bg-[#b02a3d] shadow-md shadow-red-200',
    secondary:
      'bg-[#FFD7C1] text-[#C3485C] border border-[#C3485C] hover:bg-[#fbd9d6]',
    text: 'bg-transparent text-[#C3485C] hover:underline text-xs font-semibold w-auto ml-auto block mb-6',
    icon:
      'bg-gray-200 text-gray-600 hover:bg-gray-300'
  }

  return (
    <button
      onClick={onClick}
      type={type}
      className={`${baseStyle} ${variants[variant]} ${className}`}
    >
      {Icon && <Icon size={18} className={!children ? '' : 'mr-2'} />}
      {children}
    </button>
  )
}
