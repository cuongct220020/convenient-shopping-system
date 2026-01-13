import React, { useState, useEffect } from 'react'
import { Loader, Bell } from 'lucide-react'
import { notificationService } from '../../../services/notification'
import { userService } from '../../../services/user'

type Notification = {
  id: number
  title: string
  content?: string
  timestamp: string
  isRead: boolean
}

const Notification = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [userId, setUserId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get current user to obtain user ID
    userService.getCurrentUser().match(
      (response) => {
        const id = response.data.user_id ?? response.data.id
        if (id) {
          setUserId(id)
          fetchNotifications(id)
        } else {
          setLoading(false)
        }
      },
      (error) => {
        console.error('Failed to fetch user:', error)
        setLoading(false)
      }
    )
  }, [])

  const fetchNotifications = (id: string) => {
    notificationService.getUserNotifications(id).match(
      (response) => {
        const formattedNotifications = response.data.map((notif) => ({
          id: notif.id,
          title: notif.title,
          content: notif.content,
          timestamp: formatTimestamp(notif.created_at),
          isRead: notif.is_read
        }))
        setNotifications(formattedNotifications)
        setLoading(false)
      },
      (error) => {
        console.error('Failed to fetch notifications:', error)
        setLoading(false)
      }
    )
  }

  const formatTimestamp = (createdAt: string): string => {
    const date = new Date(createdAt)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffInSeconds < 60) {
      return 'Vừa xong'
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return `${minutes} phút trước`
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return `${hours} giờ trước`
    } else {
      const days = Math.floor(diffInSeconds / 86400)
      return `${days} ngày trước`
    }
  }

  const handleDelete = (id: number) => {
    if (!userId) return

    notificationService.deleteNotification(id, userId).match(
      () => {
        setNotifications((prev) => prev.filter((n) => n.id !== id))
      },
      (error) => {
        console.error('Failed to delete notification:', error)
      }
    )
  }

  const handleMarkAsRead = (id: number) => {
    if (!userId) return

    // Mark as read via API
    notificationService.markAsRead(id, userId).match(
      () => {
        // Update local state
        setNotifications((prev) =>
          prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
        )
      },
      (error) => {
        console.error('Failed to mark notification as read:', error)
      }
    )
  }

  return (
    <div className="flex flex-col px-3 py-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <p className="whitespace-nowrap text-xl font-bold text-[#C3485C]">
          Thông báo
        </p>
        {loading && <Loader className="animate-spin text-[#C3485C]" />}
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="text-gray-400">Đang tải...</div>
        </div>
      ) : notifications.length === 0 ? (
        <div className="flex h-full flex-col items-center justify-center px-4 py-16">
          <p className="text-sm text-gray-400">Không có thông báo nào</p>
        </div>
      ) : (
        <div className="space-y-3 pb-20">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              onClick={() => !notif.isRead && handleMarkAsRead(notif.id)}
              className={`relative flex cursor-pointer items-start gap-3 rounded-lg border p-4 shadow-sm transition-all hover:shadow-md ${
                !notif.isRead
                  ? 'border-l-4 border-l-[#C3485C] border-gray-200 bg-[#C3485C]/10'
                  : 'border-gray-200 bg-white opacity-75'
              }`}
            >
              {/* Unread indicator dot */}
              {!notif.isRead && (
                <div className="absolute right-2 top-2 size-2 rounded-full bg-[#C3485C]" />
              )}

              {/* Icon */}
              <div
                className={`flex size-10 shrink-0 items-center justify-center rounded-full ${
                  !notif.isRead ? 'bg-[#C3485C]' : 'bg-gray-300'
                }`}
              >
                <Bell className={`size-5 ${!notif.isRead ? 'text-white' : 'text-gray-500'}`} />
              </div>

              {/* Content */}
              <div className="min-w-0 flex-1">
                <h3
                  className={`mb-0.5 text-sm font-semibold ${
                    !notif.isRead ? 'text-gray-900' : 'text-gray-600'
                  }`}
                >
                  {notif.title}
                </h3>
                {notif.content && (
                  <p className="mb-1 text-xs text-gray-600">{notif.content}</p>
                )}
                <p className="text-xs text-gray-400">{notif.timestamp}</p>
              </div>

              {/* Delete Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleDelete(notif.id)
                }}
                className="shrink-0 p-1 text-3xl text-gray-400 transition-colors hover:text-gray-600"
                aria-label="Xóa thông báo"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Notification
