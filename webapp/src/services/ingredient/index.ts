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

type IngredientError = ResponseError<never>
type IngredientDeleteError = ResponseError<'ingredient-still-used'>
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
   * Dynamically selects between search, filter, and regular endpoints
   * @param params - Query parameters (cursor, limit, search, categories)
   * @throws Error if both search and categories are provided (mutually exclusive)
   */
  public getIngredients(params?: {
    cursor?: number
    limit?: number
    search?: string
    categories?: string[]
  }): ResultAsync<GetIngredientsResponse, IngredientError> {
    const hasSearch = params?.search && params.search.trim()
    const hasCategories = params?.categories && params.categories.length > 0

    // Validate mutual exclusion: cannot have both search and filter
    if (hasSearch && hasCategories) {
      throw new Error('Cannot search and filter simultaneously')
    }

    // If search is provided, use search endpoint
    if (hasSearch) {
      const url = AppUrl.INGREDIENTS_SEARCH(params.search!, {
        cursor: params?.cursor,
        limit: params?.limit
      })

      return httpGet(this.clients.auth, url).andThen((response) =>
        parseZodObject(GetIngredientsResponseSchema, response.body).mapErr(
          (e): IngredientError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
    }

    // If categories are provided, use filter endpoint
    if (hasCategories) {
      const url = AppUrl.INGREDIENTS_FILTER(params.categories!, {
        cursor: params?.cursor,
        limit: params?.limit
      })

      return httpGet(this.clients.auth, url).andThen((response) =>
        parseZodObject(GetIngredientsResponseSchema, response.body).mapErr(
          (e): IngredientError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
    }

    // Otherwise use regular endpoint for listing
    const queryParams = new URLSearchParams()

    if (params?.cursor !== undefined) {
      queryParams.append('cursor', String(params.cursor))
    }
    if (params?.limit !== undefined) {
      queryParams.append('limit', String(params.limit))
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
  public deleteIngredient(
    id: string
  ): ResultAsync<void, IngredientDeleteError> {
    const url = AppUrl.INGREDIENTS_BY_ID(id)

    return httpDelete(this.clients.auth, url)
      .map(() => {})
      .mapErr((e) =>
        e.type === 'conflict'
          ? {
              type: 'ingredient-still-used',
              desc: e.desc
            }
          : e
      )
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
