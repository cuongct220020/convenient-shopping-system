import { NotificationDataSchema } from '../schema/notificationSchema'
import { LocalStorage } from '../storage/local'

export type WebSocketNotificationMessage = {
  id: number
  group_id: string
  group_name: string
  receiver: string
  created_at: string
  template_code: string
  raw_data: Record<string, unknown>
  is_read: boolean
  title: string
  content: string
}

type WebSocketMessageCallback = (notification: WebSocketNotificationMessage) => void

/**
 * Convert HTTP/HTTPS URL to WebSocket URL
 * http://example.com -> ws://example.com
 * https://example.com -> wss://example.com
 */
function getWebSocketUrl(baseUrl: string): string {
  try {
    const url = new URL(baseUrl)
    if (url.protocol === 'https:') {
      return baseUrl.replace('https://', 'wss://')
    } else if (url.protocol === 'http:') {
      return baseUrl.replace('http://', 'ws://')
    }
    // If already ws:// or wss://, return as is
    return baseUrl
  } catch {
    // Fallback: assume https if URL parsing fails
    return baseUrl.replace(/^https?:\/\//, 'wss://')
  }
}

class WebSocketNotificationService {
  private ws: WebSocket | null = null
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private userId: string | null = null
  private messageCallbacks: Set<WebSocketMessageCallback> = new Set()
  private isManualClose = false
  private currentMethodIndex = 0

  private getBaseWebSocketUrl(): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://dichotienloi.com'
    const wsBaseUrl = getWebSocketUrl(baseUrl)
    return `${wsBaseUrl}/ws/v2/notification-service/notifications/users`
  }

  private connectionMethods: Array<(userId: string) => WebSocket> = [
    // Method 1: JWT as query parameter (correct format)
    (userId) => {
      const token = LocalStorage.inst.auth?.access_token
      const baseUrl = this.getBaseWebSocketUrl()
      const wsUrl = token
        ? `${baseUrl}/${userId}/?jwt=${encodeURIComponent(token)}`
        : `${baseUrl}/${userId}/`
      return new WebSocket(wsUrl)
    },
    // Method 2: Fallback with token query param
    (userId) => {
      const token = LocalStorage.inst.auth?.access_token
      const baseUrl = this.getBaseWebSocketUrl()
      const wsUrl = token
        ? `${baseUrl}/${userId}?token=${encodeURIComponent(token)}`
        : `${baseUrl}/${userId}`
      return new WebSocket(wsUrl)
    }
  ]

  /**
   * Connect to WebSocket notification service
   */
  public connect(userId: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.userId = userId
    this.isManualClose = false

    const method = this.connectionMethods[this.currentMethodIndex]
    const ws = method(userId)

    ws.onopen = () => {
      this.reconnectAttempts = 0
      this.currentMethodIndex = 0 // Reset to default method on success
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        // Handle wrapped message format: { event_type, data }
        const notificationData = message.data || message

        const result = NotificationDataSchema.safeParse(notificationData)
        if (result.success) {
          this.notifyListeners(result.data)
        } else {
          console.error('Invalid notification format:', result.error)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onclose = () => {
      this.ws = null

      if (!this.isManualClose && this.userId) {
        // Try next method on next reconnect
        this.currentMethodIndex = (this.currentMethodIndex + 1) % this.connectionMethods.length
        this.scheduleReconnect()
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws = ws
  }

  /**
   * Disconnect from WebSocket service
   */
  public disconnect(): void {
    this.isManualClose = true
    this.userId = null
    this.currentMethodIndex = 0

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * Subscribe to notification messages
   */
  public onMessage(callback: WebSocketMessageCallback): () => void {
    this.messageCallbacks.add(callback)
    return () => {
      this.messageCallbacks.delete(callback)
    }
  }

  /**
   * Check if WebSocket is connected
   */
  public get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  private notifyListeners(notification: WebSocketNotificationMessage): void {
    this.messageCallbacks.forEach((callback) => {
      try {
        callback(notification)
      } catch (error) {
        console.error('Error in notification callback:', error)
      }
    })
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      return
    }

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts)

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++
      if (this.userId) {
        this.connect(this.userId)
      }
    }, delay)
  }
}

export const websocketNotificationService = new WebSocketNotificationService()
