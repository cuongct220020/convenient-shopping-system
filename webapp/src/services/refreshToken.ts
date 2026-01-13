// In a new file: tokenRefreshManager.ts

import { Time } from '../utils/time'
import { authService } from './auth'
import { UserAuthSchema } from './schema/authSchema'
import { LocalStorage } from './storage/local'

class TokenRefreshManager {
  private isRefreshing = false
  private refreshPromise: Promise<UserAuthSchema> | null = null

  /**
   * Core idea: Only ONE refresh happens at a time
   * Other requests wait for that refresh to complete
   */
  public async refresh(forceRefresh = false): Promise<UserAuthSchema> {
    // If already refreshing, return the existing promise
    if (this.isRefreshing) {
      if (!this.refreshPromise) {
        throw new Error('Expect refresh promise to exist here')
      }
      console.info('🔄 JWT refresh already in progress, waiting...')
      return this.refreshPromise
    }

    // If not force refresh, check if we even need to refresh
    if (!forceRefresh && !this.shouldProactiveRefresh()) {
      const current = LocalStorage.inst.auth
      if (current) return current
    }

    // Start refresh
    this.isRefreshing = true

    this.refreshPromise = new Promise((res, rej) =>
      authService
        .refreshToken()
        .mapErr((error) => {
          // TODO: Logout
          // authController.logout() // Clear everything
          this.isRefreshing = false
          this.refreshPromise = null
          rej(error)
        })
        .map((newAuth) => {
          // Success: update storage and notify all waiting requests
          const authData = newAuth.data
          LocalStorage.inst.auth = authData
          this.isRefreshing = false
          this.refreshPromise = null
          res(authData)
        })
    )

    return this.refreshPromise
  }
  private readonly BUFFER_SECONDS = 5 * 60 // 5 minutes

  /**
   * Check if we're within the ±5min window around expiration
   * This determines if reactive refresh should be attempted
   */
  public isWithinRefreshWindow(): boolean {
    const auth = LocalStorage.inst.auth
    if (!auth) return false

    const expiresAt =
      auth.token_last_refresh_timestamp + auth.expires_in_minutes * 60
    const now = Time.now

    // Within window: [expiresAt - 5min, expiresAt + 5min]
    return (
      now >= expiresAt - this.BUFFER_SECONDS &&
      now <= expiresAt + this.BUFFER_SECONDS
    )
  }

  /**
   * Check if proactive refresh should happen
   * Typically at 80% of token lifetime
   */
  public shouldProactiveRefresh(): boolean {
    const auth = LocalStorage.inst.auth
    if (!auth) return false

    const lifetime = auth.expires_in_minutes * 60
    const refreshAt =
      auth.token_last_refresh_timestamp + lifetime - this.BUFFER_SECONDS
    const now = Time.now

    return now >= refreshAt
  }
}

export const tokenRefreshManager = new TokenRefreshManager()
