import { Bell, BellMinus, ChevronLeft, LucideIcon, X } from 'lucide-react'
import { i18n } from '../utils/i18n/i18n'
import { Button } from './Button'

type NotificationProps = {
  icon?: LucideIcon
  title: string
  content?: string
  timestamp: string
  onDelete?: () => unknown
}

function Notification({
  icon = Bell,
  title,
  content,
  timestamp,
  onDelete
}: NotificationProps) {
  const Icon = icon
  return (
    <div className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
      {/* Icon */}
      <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-black">
        <Icon className="size-5 text-white" />
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <h3 className="mb-0.5 text-sm font-semibold text-gray-900">{title}</h3>
        {content && <p className="mb-1 text-xs text-gray-600">{content}</p>}
        <p className="text-xs text-gray-400">{timestamp}</p>
      </div>

      {/* Delete Button */}
      {onDelete && (
        <button
          onClick={onDelete}
          className="shrink-0 p-1 text-gray-400 transition-colors hover:text-gray-600"
          aria-label="Xóa thông báo"
        >
          <X className="size-4" />
        </button>
      )}
    </div>
  )
}

type NotificationListProps = {
  title?: string
  onClose?: () => unknown
  onDelete?: (id: number) => unknown
  defaultIcon?: LucideIcon
  notifications: (Pick<NotificationProps, 'title' | 'content' | 'timestamp'> & {
    id: number
  })[]
  emptyIcon?: LucideIcon
  emptyText?: string
}

export function NotificationList({
  title = i18n.t('notification'),
  defaultIcon = Bell,
  emptyIcon = BellMinus,
  notifications,
  emptyText = i18n.t('notification_none'),
  onClose,
  onDelete
}: NotificationListProps) {
  const EmptyIcon = emptyIcon
  return (
    <div className="relative flex w-full max-w-sm flex-col rounded-2xl bg-white">
      <div className="flex items-center">
        <Button
          icon={ChevronLeft}
          onClick={onClose}
          variant="text"
          size="fit"
          className="absolute left-0 top-2"
        />
        <h1 className="flex-1 whitespace-nowrap pt-4 text-center text-xl font-bold">
          {title}
        </h1>
      </div>

      <div className="flex-1 overflow-y-auto">
        {notifications.length > 0 ? (
          <div className="space-y-3 p-4">
            {notifications.map((notif) => (
              <Notification
                key={notif.id}
                {...notif}
                icon={defaultIcon}
                onDelete={onDelete ? () => onDelete(notif.id) : undefined}
              />
            ))}
          </div>
        ) : (
          <div className="flex h-full flex-col items-center justify-center px-4 py-16">
            <div className="mb-4 flex size-16 items-center justify-center rounded-full bg-gray-100">
              <EmptyIcon className="size-8 text-gray-400" />
            </div>
            <p className="text-sm text-gray-400">{emptyText}</p>
          </div>
        )}
      </div>
    </div>
  )
}
