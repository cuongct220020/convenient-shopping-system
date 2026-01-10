import { ResultAsync } from 'neverthrow'
import {
  AppUrl,
  Clients,
  httpClients,
  httpGet
} from '../client'
import { parseZodObject } from '../../utils/zod-result'
import {
  IngredientSearchResponseSchema,
  type IngredientSearchResponse,
  type Ingredient
} from '../schema/ingredientSchema'

type IngredientError = ReturnType<typeof createIngredientError>

function createIngredientError(type: string, desc: string | null = null) {
  return { type, desc } as const
}

export type IngredientErrorType =
  | 'not-found'
  | 'validation-error'
  | 'unauthorized'
  | 'network-error'

export class IngredientService {
  constructor(private clients: Clients) {}

  /**
   * Search ingredients by keyword
   */
  public searchIngredients(
    keyword: string
  ): ResultAsync<IngredientSearchResponse, IngredientError> {
    if (!keyword.trim()) {
      return ResultAsync.fromPromise(
        Promise.resolve({
          message: null,
          data: [],
          next_cursor: null,
          size: 0
        } as IngredientSearchResponse),
        (e) => createIngredientError('network-error', String(e))
      )
    }

    const url = AppUrl.INGREDIENTS_SEARCH(keyword)

    console.log('Searching ingredients with URL:', url)

    return httpGet(this.clients.recipe, url)
      .mapErr((e) => {
        console.error('HTTP error for ingredient search:', e)
        switch (e.type) {
          case 'path-not-found':
            return createIngredientError('not-found', e.desc)
          case 'unauthorized':
            return createIngredientError('unauthorized', e.desc)
          case 'network-error':
            return createIngredientError('network-error', e.desc)
          default:
            return createIngredientError(e.type, e.desc)
        }
      })
      .andThen((response) => {
        console.log('Raw response body:', response.body)
        return parseZodObject(
          IngredientSearchResponseSchema,
          response.body
        ).mapErr((e) => {
          console.error('Schema validation error:', e)
          return createIngredientError('validation-error', e)
        })
      })
  }
}

export const ingredientService = new IngredientService(httpClients)
