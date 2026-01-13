import { useEffect, useState, useCallback, useRef } from 'react'
import { websocketNotificationService, WebSocketNotificationMessage } from '../services/websocket'
import { ToastData } from '../components/Toast'
import { userService } from '../services/user'
import { LocalStorage } from '../services/storage/local'

// Global connection state
let globalConnectFn: (() => Promise<void>) | null = null

/**
 * Manually connect to WebSocket after login
 * Call this function after a successful login
 */
export async function connectWebSocketAfterLogin() {
  if (globalConnectFn) {
    await globalConnectFn()
  }
}

/**
 * Disconnect WebSocket (call after logout)
 */
export function disconnectWebSocket() {
  websocketNotificationService.disconnect()
}

export function useWebSocketNotification() {
  const [toasts, setToasts] = useState<ToastData[]>([])
  const userIdRef = useRef<string | null>(null)
  const isConnectingRef = useRef(false)
  const seenNotificationIds = useRef<Set<number>>(new Set())

  const addToast = useCallback((notification: WebSocketNotificationMessage) => {
    // Prevent duplicate toasts for the same notification
    if (seenNotificationIds.current.has(notification.id)) {
      return
    }
    seenNotificationIds.current.add(notification.id)

    const newToast: ToastData = {
      id: crypto.randomUUID(),
      title: notification.title,
      content: notification.content,
      groupName: notification.group_name,
      timestamp: new Date(notification.created_at)
    }

    setToasts((prev) => [newToast, ...prev])

    // Browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.content,
        icon: '/vite.svg',
        tag: notification.id.toString()
      })
    }
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const connect = useCallback(async () => {
    // Don't reconnect if already connected or connecting
    if (
      websocketNotificationService.isConnected ||
      isConnectingRef.current ||
      userIdRef.current
    ) {
      return
    }

    isConnectingRef.current = true

    try {
      // Get current user ID
      const result = await userService.getCurrentUser()

      if (result.isOk()) {
        const userData = result.value.data
        const userId = userData.user_id ?? userData.id

        if (userId) {
          userIdRef.current = userId
          websocketNotificationService.connect(userId)
          console.log('WebSocket connected for user:', userId)

          // Request notification permission
          if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission()
          }
        }
      } else {
        console.error('Failed to get user for WebSocket connection:', result.error)
      }
    } catch (error) {
      console.error('Error connecting WebSocket:', error)
    } finally {
      isConnectingRef.current = false
    }
  }, [])

  const disconnect = useCallback(() => {
    userIdRef.current = null
    isConnectingRef.current = false
    websocketNotificationService.disconnect()
  }, [])

  // Register global connect function
  useEffect(() => {
    globalConnectFn = connect
  }, [connect])

  useEffect(() => {
    // Check if user is logged in by checking localStorage
    const isLoggedIn = !!LocalStorage.inst.auth

    if (isLoggedIn) {
      connect()
    }

    // Subscribe to WebSocket messages
    const unsubscribe = websocketNotificationService.onMessage((notification) => {
      addToast(notification)
    })

    // Listen for storage changes (cross-tab login/logout)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth') {
        const isLoggedIn = !!e.newValue
        if (isLoggedIn && !websocketNotificationService.isConnected) {
          connect()
        } else if (!isLoggedIn) {
          disconnect()
        }
      }
    }

    window.addEventListener('storage', handleStorageChange)

    return () => {
      unsubscribe()
      disconnect()
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [connect, disconnect, addToast])

  return {
    toasts,
    removeToast,
    isConnected: websocketNotificationService.isConnected,
    connect
  }
}
