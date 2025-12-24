import { err, ok, Result, ResultAsync } from 'neverthrow'
import {
  AppUrl,
  Clients,
  httpClients,
  httpPost,
  ResponseError
} from '../client'
import z from 'zod'
import { parseZodObject } from '../../utils/zod-result'
import { i18nKeys } from '../../utils/i18n/keys'

const LogInResponseSchema = z.object({
  data: z.object({
    access_token: z.string(),
    refresh_token: z.string(),
    token_type: z.string()
  })
})
type LogInResponse = z.infer<typeof LogInResponseSchema>

type LogInError = ResponseError<'incorrect-credentials'>

export class AuthService {
  constructor(private clients: Clients) {}

  public static validateEmailOrUsername(input: string): Result<void, i18nKeys> {
    if (!input.trim()) {
      return err('empty_username')
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
    const isEmail = emailRegex.test(input)
    const isUsername = usernameRegex.test(input)
    if (!isEmail && !isUsername) {
      return err('invalid_username_or_email')
    }

    return ok()
  }

  public static validatePassword(password: string): Result<void, i18nKeys> {
    if (!password.trim()) {
      return err('empty_password')
    }
    return ok()
  }

  public logIn(
    email: string,
    password: string
  ): ResultAsync<LogInResponse, LogInError> {
    return httpPost(this.clients.pub, AppUrl.LOGIN, {
      email,
      password
    })
      .mapErr(
        (e): LogInError =>
          e.type === 'unauthorized'
            ? { ...e, type: 'incorrect-credentials' }
            : e
      )
      .andThen((e) =>
        parseZodObject(LogInResponseSchema, e.body).mapErr(
          (e): LogInError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }
}

export const authService = new AuthService(httpClients)
