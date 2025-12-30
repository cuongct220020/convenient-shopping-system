import z from 'zod'
import { Constant } from '../../utils/constants'

const DefaultDataSchema = z.object({
  resetPasswordOtp: z.string().or(z.undefined())
})
type DataType = z.infer<typeof DefaultDataSchema>
const DEFAULT_DATA: DataType = {
  resetPasswordOtp: undefined
} as const

export class SessionStorage {
  private static _inst = new SessionStorage()
  public static get inst() {
    return this._inst
  }
  private data: DataType

  constructor() {
    const maybeData = sessionStorage.getItem(Constant.keys.sessionStorage)
    if (!maybeData) {
      this.data = structuredClone(DEFAULT_DATA)
      this.save()
      return
    }
    const parsed = z.parse(DefaultDataSchema, JSON.parse(maybeData))
    this.data = parsed
  }

  public get resetPasswordOtp(): string | null {
    return this.data.resetPasswordOtp ?? null
  }

  public set resetPasswordOtp(val: string | null) {
    this.data.resetPasswordOtp = val ?? undefined
    this.save()
  }

  private save() {
    sessionStorage.setItem(
      Constant.keys.sessionStorage,
      JSON.stringify(this.data)
    )
  }
}
