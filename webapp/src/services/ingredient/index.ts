import { ResultAsync } from 'neverthrow'
import { Clients, httpGet, ResponseError } from '../client'
import { parseZodObject } from '../../utils/zod-result'
import {
  GetIngredientsResponseSchema,
  type GetIngredientsResponse
} from '../schema/ingredientSchema'

type IngredientError = ResponseError<'not-found' | 'unauthorized'>

export class IngredientService {
  constructor(private clients: Clients) {}

  /**
   * Get list of ingredients with cursor-based pagination
   * @param params - Query parameters (cursor, limit, search, categories)
   */
  public getIngredients(params?: {
    cursor?: number
    limit?: number
    search?: string
    categories?: string[]
  }): ResultAsync<GetIngredientsResponse, IngredientError> {
    const queryParams = new URLSearchParams()

    if (params?.cursor !== undefined) {
      queryParams.append('cursor', String(params.cursor))
    }
    if (params?.limit !== undefined) {
      queryParams.append('limit', String(params.limit))
    }
    if (params?.search) {
      queryParams.append('search', params.search)
    }
    if (params?.categories && params.categories.length > 0) {
      queryParams.append('categories', params.categories.join(','))
    }

    const url = `/v2/ingredients/?${queryParams.toString()}`

    return httpGet(this.clients.auth, url)
      .mapErr((e): IngredientError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(GetIngredientsResponseSchema, response.body).mapErr(
          (e): IngredientError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }
}

export { httpClients } from '../client'
import { httpClients } from '../client'

export const ingredientService = new IngredientService(httpClients)
