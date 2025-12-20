import axios, { AxiosInstance } from 'axios'
import { ResultAsync } from 'neverthrow'

export class AppUrl {
  static readonly BASE = import.meta.env.VITE_API_BASE_URL
  static readonly AUTH = '/auth'
  static readonly LOGIN = this.AUTH + '/login'
}

export type Clients = {
  pub: AxiosInstance
  auth: AxiosInstance
}

export function initClient(): Clients {
  axios.defaults.baseURL = AppUrl.BASE
  const pub = axios.create({ url: AppUrl.BASE })
  const auth = axios.create({ url: AppUrl.BASE })
  return { pub, auth }
}

type RequestErrorType = 'network-error' | 'unauthorized' | 'path-not-found'
type WithType<T extends string> = {
  [K in T]: {
    type: K
    desc: string | null
  }
}[T]
export type RequestError = WithType<RequestErrorType>
export type RequestOk = {
  body: string
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
  return ResultAsync.fromPromise(client.post(url, other), (e): RequestError => {
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
      default:
        return {
          type: 'network-error',
          desc: `HTTP ${status}`
        }
    }
  })
}
