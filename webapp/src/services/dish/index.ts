import { ResultAsync } from 'neverthrow'
import { parseZodObject } from '../../utils/zod-result'
import {
  Dish,
  DishLevelType,
  DishSchema,
  GetDishesResponseSchema,
  type GetDishesResponse
} from '../schema/dishSchema'
import {
  AppUrl,
  Clients,
  httpClients,
  httpGet,
  httpPost,
  httpPut,
  httpDelete,
  ResponseError
} from '../client'

type DishError = ResponseError<never>

export class DishService {
  constructor(private clients: Clients) {}

  /**
   * Get a single dish by ID
   */
  public getDishById(id: number): ResultAsync<Dish, DishError> {
    return httpGet(this.clients.auth, `${AppUrl.RECIPES}${id}`).andThen(
      (response) =>
        parseZodObject(DishSchema, response.body).mapErr(
          (e): DishError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
    )
  }

  /**
   * Update a dish by ID
   * @param component_id - The dish ID
   * @param data - Partial dish data to update
   */
  public updateDish(
    component_id: number,
    data: Partial<Omit<GetDishesResponse['data'][0], 'component_id'>>
  ): ResultAsync<GetDishesResponse['data'][0], DishError> {
    return httpPut(
      this.clients.auth,
      `${AppUrl.RECIPES}${component_id}`,
      data
    ).andThen((response) =>
      parseZodObject(DishSchema, response.body).mapErr(
        (e): DishError => ({
          type: 'invalid-response-format',
          desc: e
        })
      )
    )
  }

  /**
   * Create a new dish
   * @param data - Dish data to create
   */
  public createDish(data: Dish): ResultAsync<Dish, DishError> {
    return httpPost(this.clients.auth, AppUrl.RECIPES, data).andThen(
      (response) =>
        parseZodObject(DishSchema, response.body).mapErr(
          (e): DishError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
    )
  }

  /**
   * Delete a dish by ID
   * @param component_id - The dish ID to delete
   */
  public deleteDish(component_id: number): ResultAsync<void, DishError> {
    return httpDelete(
      this.clients.auth,
      `${AppUrl.RECIPES}${component_id}`
    ).map(() => {})
  }

  /**
   * Search dishes by keyword with pagination
   */
  public searchDishes(params: {
    keyword: string
    cursor?: number
    limit?: number
  }): ResultAsync<GetDishesResponse, DishError> {
    const queryParams = new URLSearchParams()
    queryParams.append('keyword', params.keyword)
    if (params.cursor !== undefined) {
      queryParams.append('cursor', String(params.cursor))
    }
    if (params.limit !== undefined) {
      queryParams.append('limit', String(params.limit))
    }

    const url = `${AppUrl.RECIPES}search?${queryParams.toString()}`

    return httpGet(this.clients.auth, url).andThen((response) =>
      parseZodObject(GetDishesResponseSchema, response.body).mapErr(
        (e): DishError => ({
          type: 'invalid-response-format',
          desc: e
        })
      )
    )
  }

  /**
   * Get list of dishes with cursor-based pagination
   * @param params - Query parameters (cursor, limit)
   */
  public getDishes(params?: {
    cursor?: number
    limit?: number
    /** @note This is a place holder, search has different endpoints */
    search?: string
    /** @note This is a place holder, filtering probably has different endpoints */
    level?: DishLevelType[]
  }): ResultAsync<GetDishesResponse, DishError> {
    const queryParams = new URLSearchParams()

    if (params?.cursor !== undefined) {
      queryParams.append('cursor', String(params.cursor))
    }
    if (params?.limit !== undefined) {
      queryParams.append('limit', String(params.limit))
    }

    const url = `${AppUrl.RECIPES}${
      queryParams.toString() ? '?' + queryParams.toString() : ''
    }`

    return httpGet(this.clients.auth, url).andThen((response) =>
      parseZodObject(GetDishesResponseSchema, response.body).mapErr(
        (e): DishError => ({
          type: 'invalid-response-format',
          desc: e
        })
      )
    )
  }
}

export const dishService = new DishService(httpClients)
