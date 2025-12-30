import z from 'zod'

export const UserAuthSchemaZ = z.object({
  access_token: z.string(),
  token_type: z.string(),
  expires_in_minutes: z.number()
})

export type UserAuthSchema = z.infer<typeof UserAuthSchemaZ>
