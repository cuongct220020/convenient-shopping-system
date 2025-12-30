import { UserAuthSchema } from '../services/schema/authSchema'
import { LocalStorage } from '../services/storage/local'
import { Time } from '../utils/time'

class AuthController {
  private _isLoggedIn = false

  public static loadFromStorage(): AuthController {
    const auth = LocalStorage.inst.auth
    if (!auth) return new AuthController()
    const tokenExpirationTime =
      auth.expires_in_minutes * 60 + auth.token_last_refresh_timestamp
    const now = Time.now
    if (tokenExpirationTime <= now) return new AuthController()

    const result = new AuthController()
    result._isLoggedIn = true
    return result
  }

  public saveUserAuth(auth: UserAuthSchema) {
    LocalStorage.inst.auth = auth
  }

  public get isLoggedIn(): boolean {
    return this._isLoggedIn
  }
}

export const authController = AuthController.loadFromStorage()
