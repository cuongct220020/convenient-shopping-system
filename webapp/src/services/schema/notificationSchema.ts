import z from 'zod'

export const NotificationDataSchema = z.object({
  id: z.number(),
  group_id: z.string().uuid(),
  group_name: z.string(),
  receiver: z.string().uuid(),
  created_at: z.string(),
  template_code: z.string(),
  raw_data: z.record(z.string(), z.unknown()),
  is_read: z.boolean(),
  title: z.string(),
  content: z.string()
})

export type NotificationData = z.infer<typeof NotificationDataSchema>

export const NotificationsResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
  data: z.array(NotificationDataSchema)
})

export type NotificationsResponse = z.infer<typeof NotificationsResponseSchema>

export const NotificationMarkReadResponseSchema = z.object({
  status: z.string(),
  message: z.string()
})

export type NotificationMarkReadResponse = z.infer<typeof NotificationMarkReadResponseSchema>

export const NotificationDeleteResponseSchema = z.object({
  status: z.string(),
  message: z.string()
})

export type NotificationDeleteResponse = z.infer<typeof NotificationDeleteResponseSchema>
