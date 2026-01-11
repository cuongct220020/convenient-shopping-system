import { okAsync, ResultAsync } from 'neverthrow'
import { parseZodObject } from '../../utils/zod-result'
import {
  GetIngredientsResponseSchema,
  IngredientSearchResponse,
  IngredientSearchResponseSchema,
  type GetIngredientsResponse
} from '../schema/ingredientSchema'

import { AppUrl, Clients, httpClients, httpGet, ResponseError } from '../client'

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

  /**
   * Search ingredients by keyword
   */
  public searchIngredients(
    keyword: string
  ): ResultAsync<IngredientSearchResponse, IngredientError> {
    if (!keyword.trim())
      return okAsync({
        message: null,
        data: [],
        next_cursor: null,
        size: 0
      })

    const url = AppUrl.INGREDIENTS_SEARCH(keyword)

    console.log('Searching ingredients with URL:', url)

    return httpGet(this.clients.recipe, url)
      .mapErr((e) => {
        console.error('HTTP error for ingredient search:', e)
        return e
      })
      .andThen((response) => {
        console.log('Raw response body:', response.body)
        return parseZodObject(
          IngredientSearchResponseSchema,
          response.body
        ).mapErr((e) => {
          console.error('Schema validation error:', e)
          return {
            type: 'invalid-response-format' as const,
            desc: e
          }
        })
      })
  }
}

export const ingredientService = new IngredientService(httpClients)
