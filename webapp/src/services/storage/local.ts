import z from 'zod'
import { Constant } from '../../utils/constants'
import { Time } from '../../utils/time'
import { assert } from '../../utils/assert'

const DefaultDataSchema = z.object({
  otpExpireTime: z.number(),
  emailRequestingOtp: z.string().or(z.undefined())
})
type DataType = z.infer<typeof DefaultDataSchema>
const DEFAULT_DATA: DataType = {
  otpExpireTime: 0,
  emailRequestingOtp: undefined
} as const

export class LocalStorage {
  private static _inst = new LocalStorage()
  public static get inst() {
    return this._inst
  }
  private data: DataType

  constructor() {
    const maybeData = localStorage.getItem(Constant.keys.localStorage)
    if (!maybeData) {
      this.data = structuredClone(DEFAULT_DATA)
      this.save()
      return
    }
    const parsed = z.parse(DefaultDataSchema, JSON.parse(maybeData))
    this.data = parsed
  }

  public otpStartCountdown(): number {
    assert(
      this.otpCanRequest,
      'Must wait until time to next request reaches zero'
    )
    const dur = Constant.otpRequestInterval
    this.data.otpExpireTime = Time.now + dur
    this.save()
    return this.otpTimeToNextRequest
  }

  public get otpTimeToNextRequest(): number {
    return Math.max(0, this.data.otpExpireTime - Time.now)
  }

  public get otpCanRequest(): boolean {
    return this.otpTimeToNextRequest <= 0
  }

  public set emailRequestingOtp(val: string | null) {
    this.data.emailRequestingOtp = val ?? undefined
    this.save()
  }

  public get emailRequestingOtp(): string | null {
    return this.data.emailRequestingOtp ?? null
  }

  private save() {
    localStorage.setItem(Constant.keys.localStorage, JSON.stringify(this.data))
  }
}
