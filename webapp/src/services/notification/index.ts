import { ResultAsync } from 'neverthrow'
import z from 'zod'
import {
  AppUrl,
  Clients,
  httpClients,
  httpGet,
  httpPatch,
  httpDelete,
  ResponseError
} from '../client'
import { parseZodObject } from '../../utils/zod-result'

// Inline schemas to avoid circular dependency issues
const NotificationDataSchema = z.object({
  id: z.number(),
  group_id: z.string(),
  group_name: z.string(),
  receiver: z.string(),
  created_at: z.string(),
  template_code: z.string(),
  raw_data: z.any(),
  is_read: z.boolean(),
  title: z.string(),
  content: z.string()
})

const NotificationsResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
  data: z.array(NotificationDataSchema)
})

const NotificationMarkReadResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
  data: z.object({
    id: z.number(),
    is_read: z.boolean()
  })
})

const NotificationDeleteResponseSchema = z.object({
  status: z.string(),
  message: z.string()
})

type NotificationsResponse = z.infer<typeof NotificationsResponseSchema>
type NotificationMarkReadResponse = z.infer<
  typeof NotificationMarkReadResponseSchema
>
type NotificationDeleteResponse = z.infer<
  typeof NotificationDeleteResponseSchema
>

type NotificationError = ResponseError<
  'not-found' | 'validation-error' | 'unauthorized' | 'conflict'
>

export class NotificationService {
  constructor(private clients: Clients) {}

  /**
   * Get user's notifications
   */
  public getUserNotifications(
    userId: string
  ): ResultAsync<NotificationsResponse, NotificationError> {
    return httpGet(this.clients.auth, AppUrl.NOTIFICATIONS(userId))
      .mapErr((e): NotificationError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(NotificationsResponseSchema, response.body).mapErr(
          (e): NotificationError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Mark notification as read
   */
  public markAsRead(
    notificationId: number,
    userId: string
  ): ResultAsync<NotificationMarkReadResponse, NotificationError> {
    return httpPatch(
      this.clients.auth,
      AppUrl.NOTIFICATION_MARK_READ(notificationId, userId),
      {}
    )
      .mapErr((e): NotificationError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(
          NotificationMarkReadResponseSchema,
          response.body
        ).mapErr(
          (e): NotificationError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Delete notification
   */
  public deleteNotification(
    notificationId: number,
    userId: string
  ): ResultAsync<NotificationDeleteResponse, NotificationError> {
    return httpDelete(
      this.clients.auth,
      AppUrl.NOTIFICATION_DELETE(notificationId, userId)
    )
      .mapErr((e): NotificationError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(NotificationDeleteResponseSchema, response.body).mapErr(
          (e): NotificationError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }
}

export const notificationService = new NotificationService(httpClients)
