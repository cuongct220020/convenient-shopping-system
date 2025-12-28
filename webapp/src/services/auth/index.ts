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
    access_token: z.string()
  })
})
type LogInResponse = z.infer<typeof LogInResponseSchema>
type LogInError = ResponseError<'incorrect-credentials' | 'unverfified'>

type FullnameValidationOk = {
  firstName: string
  lastName: string
}
type RegisterResponse = null
type RegisterError = ResponseError<never>

type VerificationResponse = null
type VerificationError = ResponseError<'incorrect-otp'>

type AskVerifyResponse = null
type AskVerifyError = ResponseError<never>

type OtpType = 'register' | 'reset_password' | 'change_email'

export class AuthService {
  constructor(private clients: Clients) {}

  public static validateEmail(input: string): Result<void, i18nKeys> {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const isEmail = emailRegex.test(input)
    if (!isEmail) return err('invalid_email')
    return ok()
  }

  public static validateUsername(input: string): Result<void, i18nKeys> {
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
    const isUsername = usernameRegex.test(input)
    if (!isUsername) return err('invalid_username')
    return ok()
  }

  public static validateEmailOrUsername(input: string): Result<void, i18nKeys> {
    if (!input.trim()) {
      return err('empty_username')
    }
    const emailValidation = this.validateEmail(input)
    const usernameValidation = this.validateUsername(input)
    if (emailValidation.isErr() && usernameValidation.isErr()) {
      return err('invalid_username_or_email')
    }

    return ok()
  }

  private static validateFirstOrLastName(
    input: string
  ): Result<void, i18nKeys> {
    const trimmed = input.trim()
    if (!trimmed) {
      return err('empty_name')
    }
    if (trimmed.length > 50) {
      return err('invalid_name_length')
    }
    const nameRegex = /^[\p{L}\s]+$/u
    if (!nameRegex.test(trimmed)) {
      return err('invalid_name_format')
    }
    return ok()
  }

  public static validateFullName(
    input: string
  ): Result<FullnameValidationOk, i18nKeys> {
    const trimmed = input.trim()
    if (!trimmed) {
      return err('empty_name')
    }
    if (trimmed.length > 100) {
      return err('invalid_name_length')
    }
    const nameRegex = /^[\p{L}\s]+$/u
    if (!nameRegex.test(trimmed)) {
      return err('invalid_name_format')
    }
    // Split by spaces and filter out empty strings
    const parts = trimmed.split(/\s+/)
    if (parts.length < 2) {
      return err('name_requires_two_parts')
    }
    const firstName = parts[0]
    const lastName = parts.slice(1).join(' ')
    return Result.combine([
      this.validateFirstOrLastName(firstName),
      this.validateFirstOrLastName(lastName)
    ]).map(() => ({ firstName, lastName }))
  }

  public static validatePassword(input: string): Result<void, i18nKeys> {
    if (!input.trim()) {
      return err('empty_password')
    }
    if (input.length < 6) {
      return err('invalid_password')
    }
    return ok()
  }

  public static validateOtpFormat(input: string): boolean {
    return /^\d{6}$/.test(input)
  }

  public logIn(
    identifier: string,
    password: string
  ): ResultAsync<LogInResponse, LogInError> {
    return httpPost(this.clients.pub, AppUrl.LOGIN, {
      identifier,
      password
    })
      .mapErr((e): LogInError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'incorrect-credentials' }
          case 'forbidden':
            return { ...e, type: 'unverfified' }
          default:
            return e
        }
      })
      .andThen((e) =>
        parseZodObject(LogInResponseSchema, e.body).mapErr(
          (e): LogInError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  public register(opts: {
    email: string
    username: string
    password: string
    firstName: string
    lastName: string
  }): ResultAsync<RegisterResponse, RegisterError> {
    return httpPost(this.clients.pub, AppUrl.REGISTER, {
      email: opts.email,
      username: opts.username,
      password: opts.password,
      first_name: opts.firstName,
      last_name: opts.lastName
    }).map(() => null)
  }

  public sendOtpRequest(
    type: OtpType,
    email: string
  ): ResultAsync<AskVerifyResponse, AskVerifyError> {
    return httpPost(this.clients.pub, AppUrl.SEND_OTP, {
      email,
      action: type
    }).map(() => null)
  }

  public verifyOtp(opts: {
    identification: string
    otp: string
    type: OtpType
  }): ResultAsync<VerificationResponse, VerificationError> {
    return httpPost(this.clients.pub, AppUrl.VERIFY_OTP, {
      email: opts.identification,
      otp_code: opts.otp,
      action: opts.type
    })
      .map(() => null)
      .mapErr((e) =>
        e.type === 'unauthorized' ? { ...e, type: 'incorrect-otp' } : e
      )
  }
}

export const authService = new AuthService(httpClients)
