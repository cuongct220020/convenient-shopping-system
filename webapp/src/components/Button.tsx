import { ReactNode } from 'react'

interface ButtonProps {
  children?: ReactNode
  onClick?: () => void
  variant?:
    | 'primary'
    | 'secondary'
    | 'text'
    | 'pagination'
    | 'pagination-active'
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
    variant === 'pagination' || variant === 'pagination-active'
      ? 'w-8 h-8 flex items-center justify-center rounded transition-all duration-200 active:scale-95'
      : isIconOnly
        ? `${size === 'fit' ? 'w-fit' : size === 'auto' ? 'w-auto' : 'w-full'} py-3 px-3 rounded-xl font-bold text-sm flex items-center justify-center transition-all duration-200 active:scale-95`
        : `${sizes[size]} py-3 rounded-xl font-bold text-sm flex items-center justify-center transition-all duration-200 active:scale-95`

  const variants: Record<string, string> = {
    primary:
      'bg-[#c93045] text-white hover:bg-[#b02a3d] shadow-md shadow-red-200',
    secondary:
      'bg-[#fcece9] text-[#c93045] border border-[#eeb4b4] hover:bg-[#fbd9d6]',
    text: 'bg-transparent text-[#c93045] hover:underline text-xs font-semibold w-auto ml-auto block mb-6',
    pagination:
      'bg-transparent text-gray-600 hover:bg-gray-100 hover:text-rose-500 text-sm font-medium',
    'pagination-active':
      'bg-[#c93045] text-white hover:bg-[#b02a3d] shadow-md shadow-red-200 text-sm font-medium',
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
