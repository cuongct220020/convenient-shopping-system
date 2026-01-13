import { okAsync, ResultAsync } from 'neverthrow'
import { parseZodObject } from '../../utils/zod-result'
import {
  GetIngredientsResponseSchema,
  IngredientSchema,
  IngredientSearchResponse,
  IngredientSearchResponseSchema,
  type GetIngredientsResponse,
  type Ingredient
} from '../schema/ingredientSchema'
import {
  AppUrl,
  Clients,
  httpClients,
  httpDelete,
  httpGet,
  httpPost,
  httpPut,
  ResponseError
} from '../client'

type IngredientError = ResponseError<'not-found' | 'unauthorized'>

export class IngredientService {
  constructor(private clients: Clients) {}

  /**
   * Get a single ingredient by ID
   */
  public getIngredientById(
    id: number
  ): ResultAsync<Ingredient, IngredientError> {
    const url = AppUrl.INGREDIENTS_BY_ID(String(id))

    return httpGet(this.clients.auth, url).andThen((response) =>
      parseZodObject(IngredientSchema, response.body).mapErr(
        (e): IngredientError => ({
          type: 'invalid-response-format',
          desc: e
        })
      )
    )
  }

  /**
   * Get list of ingredients with cursor-based pagination
   * Dynamically selects between search and regular endpoints
   * @param params - Query parameters (cursor, limit, search, categories)
   */
  public getIngredients(params?: {
    cursor?: number
    limit?: number
    search?: string
    categories?: string[]
  }): ResultAsync<GetIngredientsResponse, IngredientError> {
    // If search is provided, use search endpoint
    if (params?.search && params.search.trim()) {
      const queryParams = new URLSearchParams()
      queryParams.append('keyword', params.search)
      if (params?.cursor !== undefined) {
        queryParams.append('cursor', String(params.cursor))
      }
      if (params?.limit !== undefined) {
        queryParams.append('limit', String(params.limit))
      }

      const url = `${AppUrl.INGREDIENTS}search?${queryParams.toString()}`

      return httpGet(this.clients.auth, url).andThen((response) =>
        parseZodObject(GetIngredientsResponseSchema, response.body).mapErr(
          (e): IngredientError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
    }

    // Otherwise use regular endpoint for listing/filtering
    const queryParams = new URLSearchParams()

    if (params?.cursor !== undefined) {
      queryParams.append('cursor', String(params.cursor))
    }
    if (params?.limit !== undefined) {
      queryParams.append('limit', String(params.limit))
    }
    if (params?.categories && params.categories.length > 0) {
      queryParams.append('categories', params.categories.join(','))
    }

    const url = `${AppUrl.INGREDIENTS}?${queryParams.toString()}`

    return httpGet(this.clients.auth, url).andThen((response) =>
      parseZodObject(GetIngredientsResponseSchema, response.body).mapErr(
        (e): IngredientError => ({
          type: 'invalid-response-format',
          desc: e
        })
      )
    )
  }

  /**
   * Delete an ingredient by ID
   * @param id - The component_id of the ingredient to delete
   */
  public deleteIngredient(id: string): ResultAsync<void, IngredientError> {
    const url = AppUrl.INGREDIENTS_BY_ID(id)

    return httpDelete(this.clients.auth, url).map(() => {})
  }

  /**
   * Search ingredients by keyword with pagination
   */
  public searchIngredients(
    keyword: string,
    params: {
      cursor?: number
      limit?: number
    }
  ): ResultAsync<IngredientSearchResponse, IngredientError> {
    if (!keyword.trim())
      return okAsync({
        message: null,
        data: [],
        next_cursor: null,
        size: 0
      })

    const url = AppUrl.INGREDIENTS_SEARCH(keyword, params)

    return httpGet(this.clients.auth, url)
      .mapErr((e) => {
        console.error('HTTP error for ingredient search:', e)
        return e
      })
      .andThen((response) =>
        parseZodObject(IngredientSearchResponseSchema, response.body).mapErr(
          (e) => ({
            type: 'invalid-response-format' as const,
            desc: e
          })
        )
      )
  }

  /**
   * Create a new ingredient
   * @param data - Ingredient creation data
   */
  public createIngredient(
    data: Partial<Ingredient>
  ): ResultAsync<Ingredient, IngredientError> {
    return httpPost(this.clients.auth, AppUrl.INGREDIENTS, data).andThen(
      (response) =>
        parseZodObject(IngredientSchema, response.body).mapErr(
          (e): IngredientError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
    )
  }

  /**
   * Update an ingredient by ID
   * @param id - The component_id of the ingredient
   * @param data - Ingredient update data
   */
  public updateIngredient(
    id: string,
    data: Partial<Ingredient>
  ): ResultAsync<Ingredient, IngredientError> {
    const url = AppUrl.INGREDIENTS_BY_ID(id)

    return httpPut(this.clients.auth, url, data).andThen((response) =>
      parseZodObject(IngredientSchema, response.body).mapErr(
        (e): IngredientError => ({
          type: 'invalid-response-format',
          desc: e
        })
      )
    )
  }
}

export const ingredientService = new IngredientService(httpClients)
