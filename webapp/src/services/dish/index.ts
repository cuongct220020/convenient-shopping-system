import { ResultAsync } from 'neverthrow'
import { parseZodObject } from '../../utils/zod-result'
import {
  GetDishesResponseSchema,
  type GetDishesResponse
} from '../schema/dishSchema'
import { AppUrl, Clients, httpClients, httpGet, ResponseError } from '../client'

type DishError = ResponseError<never>

export class DishService {
  constructor(private clients: Clients) {}

  /**
   * Get list of dishes with cursor-based pagination
   * @param params - Query parameters (cursor, limit)
   */
  public getDishes(params?: {
    cursor?: number
    limit?: number
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

    return httpGet(this.clients.recipe, url).andThen((response) =>
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
