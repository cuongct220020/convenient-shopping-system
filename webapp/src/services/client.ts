import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { ResultAsync } from 'neverthrow'
import { LocalStorage } from './storage/local'

export class AppUrl {
  static readonly BASE = import.meta.env.VITE_API_BASE_URL
  static readonly SHOPPING_BASE = import.meta.env.VITE_SHOPPING_API_BASE_URL
  static readonly RECIPE_BASE = import.meta.env.VITE_RECIPE_API_BASE_URL
  static readonly AUTH = 'api/v1/user-service/auth'
  static readonly LOGIN = this.AUTH + '/login'
  static readonly REGISTER = this.AUTH + '/register'
  static readonly LOGOUT = this.AUTH + '/logout'
  static readonly SEND_OTP = this.AUTH + '/otp/send'
  static readonly VERIFY_OTP = this.AUTH + '/otp/verify'
  static readonly RESET_PASSWORD = this.AUTH + '/reset-password'
  static readonly GROUPS = 'api/v1/user-service/groups'
  static readonly GROUP_BY_ID = (id: string) => `api/v1/user-service/groups/${id}`
  static readonly GROUP_MEMBERS = (id: string) => `api/v1/user-service/groups/${id}/members`
  static readonly GROUP_MEMBER_BY_ID = (groupId: string, userId: string) =>
    `api/v1/user-service/groups/${groupId}/members/${userId}`
  static readonly GROUP_MEMBER_IDENTITY_PROFILE = (groupId: string, userId: string) =>
    `api/v1/user-service/groups/${groupId}/members/${userId}/identity-profile`
  static readonly GROUP_MEMBER_HEALTH_PROFILE = (groupId: string, userId: string) =>
    `api/v1/user-service/groups/${groupId}/members/${userId}/health-profile`
  static readonly GROUP_LEADER = (id: string) => `api/v1/user-service/groups/${id}/leader`
  static readonly GROUP_LEAVE = (id: string) => `api/v1/user-service/groups/${id}/members/me`
  static readonly USERS_ME = 'api/v1/user-service/users/me'
  static readonly USERS_ME_IDENTITY_PROFILE = 'api/v1/user-service/users/me/profile/identity'
  static readonly USERS_ME_HEALTH_PROFILE = 'api/v1/user-service/users/me/profile/health'
  static readonly USER_SEARCH = 'api/v1/user-service/users/search'
  static readonly USERS_ME_EMAIL_REQUEST_CHANGE = 'api/v1/user-service/users/me/email/request-change'
  static readonly USERS_ME_EMAIL_CONFIRM_CHANGE = 'api/v1/user-service/users/me/email/confirm-change'
  static readonly CHANGE_PASSWORD = 'api/v1/user-service/users/me/change-password'
  static readonly USER_BY_ID = (id: string) => `api/v1/user-service/users/${id}`
  static readonly USER_IDENTITY_PROFILE_BY_ID = (id: string) =>
    `api/v1/user-service/users/${id}/profile/identity`
  static readonly USER_HEALTH_PROFILE_BY_ID = (id: string) =>
    `api/v1/user-service/users/${id}/profile/health`
  static readonly ADMIN_USERS = 'api/v1/user-service/admin/users'
  static readonly SHOPPING_PLANS_FILTER = 'v1/shopping_plans/filter'
  static readonly SHOPPING_PLANS = 'v1/shopping_plans/'
  static readonly INGREDIENTS_SEARCH = (keyword: string) => `v2/ingredients/search?keyword=${encodeURIComponent(keyword)}`
}

export type Clients = {
  pub: AxiosInstance
  auth: AxiosInstance
  shopping: AxiosInstance
  recipe: AxiosInstance
}
function initClient(): Clients {
  axios.defaults.baseURL = AppUrl.BASE
  const pub = axios.create({ url: AppUrl.BASE })
  const auth = axios.create({ url: AppUrl.BASE })
  const shopping = axios.create({
    url: AppUrl.SHOPPING_BASE,
    baseURL: AppUrl.SHOPPING_BASE
  })
  const recipe = axios.create({
    url: AppUrl.RECIPE_BASE,
    baseURL: AppUrl.RECIPE_BASE
  })

  // Add token injection to auth client
  auth.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = LocalStorage.inst.auth?.access_token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Prevent browser caching for GET requests
    if (config.method === 'get') {
      config.headers['Cache-Control'] = 'no-cache'
      config.headers.Pragma = 'no-cache'
    }
    return config
  })

  // Add token injection to shopping client
  shopping.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = LocalStorage.inst.auth?.access_token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  // Add token injection to recipe client
  recipe.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const token = LocalStorage.inst.auth?.access_token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  return { pub, auth, shopping, recipe }
}
export const httpClients = initClient()

type RequestErrorType =
  | 'network-error'
  | 'unauthorized'
  | 'path-not-found'
  | 'forbidden'
  | 'conflict'
type WithType<T extends string> = {
  [K in T]: {
    type: K
    desc: string | null
  }
}[T]
export type RequestError = WithType<RequestErrorType>
export type RequestOk = {
  body: unknown
}
export type ResponseError<Codes extends string> =
  | RequestError
  | WithType<Codes>
  | WithType<'invalid-response-format'>

export function httpPost<T>(
  client: AxiosInstance,
  url: string,
  other: T
): ResultAsync<RequestOk, RequestError> {
  return ResultAsync.fromThrowable(
    () => client.post(url, other),
    (e): RequestError => {
      if (!axios.isAxiosError(e) || e.response === undefined) {
        return {
          type: 'network-error',
          desc: null
        }
      }
      const status = e.response.status
      switch (status) {
        case 401:
          return { type: 'unauthorized', desc: null }
        case 404:
          return { type: 'path-not-found', desc: null }
        case 403:
          return { type: 'forbidden', desc: null }
        case 409:
          return { type: 'conflict', desc: null }
        default:
          return {
            type: 'network-error',
            desc: `HTTP ${status}`
          }
      }
    }
  )().map((response) => {
    return {
      body: response.data
    }
  })
}

export function httpGet(
  client: AxiosInstance,
  url: string
): ResultAsync<RequestOk, RequestError> {
  return ResultAsync.fromThrowable(
    () => client.get(url),
    (e): RequestError => {
      if (!axios.isAxiosError(e) || e.response === undefined) {
        return {
          type: 'network-error',
          desc: null
        }
      }
      const status = e.response.status
      switch (status) {
        case 401:
          return { type: 'unauthorized', desc: null }
        case 404:
          return { type: 'path-not-found', desc: null }
        case 403:
          return { type: 'forbidden', desc: null }
        case 409:
          return { type: 'conflict', desc: null }
        default:
          return {
            type: 'network-error',
            desc: `HTTP ${status}`
          }
      }
    }
  )().map((response) => {
    return {
      body: response.data
    }
  })
}

export function httpPut<T>(
  client: AxiosInstance,
  url: string,
  data: T
): ResultAsync<RequestOk, RequestError> {
  return ResultAsync.fromThrowable(
    () => client.put(url, data),
    (e): RequestError => {
      if (!axios.isAxiosError(e) || e.response === undefined) {
        return {
          type: 'network-error',
          desc: null
        }
      }
      const status = e.response.status
      switch (status) {
        case 401:
          return { type: 'unauthorized', desc: null }
        case 404:
          return { type: 'path-not-found', desc: null }
        case 403:
          return { type: 'forbidden', desc: null }
        case 409:
          return { type: 'conflict', desc: null }
        default:
          return {
            type: 'network-error',
            desc: `HTTP ${status}`
          }
      }
    }
  )().map((response) => {
    return {
      body: response.data
    }
  })
}

export function httpPatch<T>(
  client: AxiosInstance,
  url: string,
  data: T
): ResultAsync<RequestOk, RequestError> {
  return ResultAsync.fromThrowable(
    () => client.patch(url, data),
    (e): RequestError => {
      if (!axios.isAxiosError(e) || e.response === undefined) {
        return {
          type: 'network-error',
          desc: null
        }
      }
      const status = e.response.status
      switch (status) {
        case 401:
          return { type: 'unauthorized', desc: null }
        case 404:
          return { type: 'path-not-found', desc: null }
        case 403:
          return { type: 'forbidden', desc: null }
        case 409:
          return { type: 'conflict', desc: null }
        default:
          return {
            type: 'network-error',
            desc: `HTTP ${status}`
          }
      }
    }
  )().map((response) => {
    return {
      body: response.data
    }
  })
}

export function httpDelete(
  client: AxiosInstance,
  url: string
): ResultAsync<RequestOk, RequestError> {
  return ResultAsync.fromThrowable(
    () => client.delete(url),
    (e): RequestError => {
      if (!axios.isAxiosError(e) || e.response === undefined) {
        return {
          type: 'network-error',
          desc: null
        }
      }
      const status = e.response.status
      switch (status) {
        case 401:
          return { type: 'unauthorized', desc: null }
        case 404:
          return { type: 'path-not-found', desc: null }
        case 403:
          return { type: 'forbidden', desc: null }
        case 409:
          return { type: 'conflict', desc: null }
        default:
          return {
            type: 'network-error',
            desc: `HTTP ${status}`
          }
      }
    }
  )().map((response) => {
    return {
      body: response.data
    }
  })
}
