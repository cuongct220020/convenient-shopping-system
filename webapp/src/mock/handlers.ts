import { http, HttpResponse } from 'msw'
import { AppUrl } from '../services/client'

function unauthorizedResponse() {
  return HttpResponse.json(
    {
      detail: 'You are stupid, wrong format'
    },
    {
      status: 401
    }
  )
}

const authHandlers = [
  http.post(AppUrl.BASE + AppUrl.LOGIN, async (e) => {
    const body = await e.request.json()
    if (!body) {
      return unauthorizedResponse()
    }
    if (/OK/.test(JSON.stringify(body))) {
      return HttpResponse.json({
        // status: 'success',
        // message: 'string',
        data: {
          access_token: 'this access token',
          refresh_token: 'this refresh token',
          token_type: 'Bearer'
        }
      })
    }
    return unauthorizedResponse()
  })
]

export const handlers = [
  // ...authHandlers
]
