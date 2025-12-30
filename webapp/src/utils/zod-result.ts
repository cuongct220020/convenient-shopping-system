import { err, ok, Result } from 'neverthrow'
import z from 'zod'

export function parseZodObject<Z extends z.ZodType>(
  type: Z,
  data: unknown
): Result<z.infer<Z>, string> {
  const res = type.safeParse(data)
  return res.success ? ok(res.data) : err(z.prettifyError(res.error))
}
