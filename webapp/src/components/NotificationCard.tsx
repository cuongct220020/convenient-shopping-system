import { LucideIcon } from 'lucide-react'
import { Button } from './Button'

interface NotificationCardProps {
  title: string
  message: string
  icon?: LucideIcon
  iconSize?: number
  iconColor?: string
  iconBgColor?: string
  buttonText?: string
  onButtonClick?: () => void
  buttonVariant?: 'primary' | 'secondary'
  buttonIcon?: LucideIcon
  // Second button props
  button2Text?: string
  onButton2Click?: () => void
  button2Variant?: 'primary' | 'secondary'
  button2Icon?: LucideIcon
  titleColor?: string
  messageColor?: string
}

export function NotificationCard({
  title,
  message,
  icon,
  iconSize = 48,
  iconColor = 'text-white',
  iconBgColor = 'bg-green-500',
  buttonText = 'Đóng',
  onButtonClick,
  buttonVariant = 'primary',
  buttonIcon,
  button2Text,
  onButton2Click,
  button2Variant = 'secondary',
  button2Icon,
  titleColor = 'text-[#c93045]',
  messageColor = 'text-gray-600'
}: NotificationCardProps) {
  const Icon = icon

  return (
    <div className="rounded-2xl bg-white p-6 sm:p-8 md:p-10 text-center shadow-lg border border-gray-100 mx-auto w-full max-w-sm">
      {/* Title */}
      <h1 className={`mb-6 text-xl sm:text-2xl md:text-3xl font-bold ${titleColor}`}>
        {title}
      </h1>

      {/* Icon */}
      {Icon && (
        <div className="mb-6 flex justify-center">
          <div className={`flex size-20 items-center justify-center rounded-full ${iconBgColor}`}>
            <Icon size={iconSize} className={iconColor} strokeWidth={2.5} />
          </div>
        </div>
      )}

      {/* Message */}
      <p
        className={`mb-8 text-sm leading-relaxed ${messageColor}`}
        dangerouslySetInnerHTML={{ __html: message }}
      />

      {/* Button(s) */}
      {(onButtonClick || onButton2Click) && (
        <div className="flex gap-3 justify-center">
          {onButtonClick && (
            <Button variant={buttonVariant} size="fit" icon={buttonIcon} onClick={onButtonClick}>
              {buttonText}
            </Button>
          )}
          {onButton2Click && button2Text && (
            <Button variant={button2Variant} size="fit" icon={button2Icon} onClick={onButton2Click}>
              {button2Text}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}