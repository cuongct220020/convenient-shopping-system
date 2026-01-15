import { ResultAsync } from 'neverthrow'
import { httpClients, httpGet, httpPost } from '../client'

export type MealType3 = 'breakfast' | 'lunch' | 'dinner'
export type MealStatus = 'created' | 'cancelled' | 'done' | string

export type MealRecipe = {
  recipe_id: number
  recipe_name: string
  servings: number
}

export type MealResponse = {
  meal_id: number
  date: string // YYYY-MM-DD
  group_id: string
  meal_type: MealType3
  meal_status: MealStatus
  recipe_list: MealRecipe[]
}

export type MealMissingResponse = {
  date: string // YYYY-MM-DD
  group_id: string
  meal_type: MealType3
  detail: string
}

export type DailyMealAction = 'upsert' | 'delete' | 'skip'
export type MealCommand = {
  action: DailyMealAction
  recipe_list?: MealRecipe[]
}

export type DailyMealsCommand = {
  date: string // YYYY-MM-DD
  group_id: string
  breakfast: MealCommand
  lunch: MealCommand
  dinner: MealCommand
}

type MealErrorType = 'network-error' | 'unauthorized' | 'not-found' | 'validation-error'
type MealError = { type: MealErrorType; desc: string | null }

function createMealError(type: MealErrorType, desc: string | null = null): MealError {
  return { type, desc }
}

export class MealService {
  /**
   * Get daily meals (always 3 items: breakfast/lunch/dinner)
   */
  public getDailyMeals(params: {
    mealDate: string // YYYY-MM-DD
    groupId: string
  }): ResultAsync<Array<MealResponse | MealMissingResponse>, MealError> {
    const query = new URLSearchParams()
    query.append('meal_date', params.mealDate)
    query.append('group_id', params.groupId)
    const url = `/v1/meals/?${query.toString()}`

    return httpGet(httpClients.auth, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'unauthorized':
            return createMealError('unauthorized', e.desc)
          case 'path-not-found':
            return createMealError('not-found', e.desc)
          default:
            return createMealError('network-error', e.desc)
        }
      })
      .map((response) => response.body as Array<MealResponse | MealMissingResponse>)
  }

  /**
   * Save daily meals via command API
   */
  public commandDailyMeals(params: {
    groupId: string
    command: DailyMealsCommand
  }): ResultAsync<Array<MealResponse | MealMissingResponse>, MealError> {
    const query = new URLSearchParams()
    query.append('group_id', params.groupId)
    const url = `/v1/meals/command?${query.toString()}`

    return httpPost(httpClients.auth, url, params.command)
      .mapErr((e) => {
        switch (e.type) {
          case 'unauthorized':
            return createMealError('unauthorized', e.desc)
          case 'path-not-found':
            return createMealError('not-found', e.desc)
          default:
            return createMealError('network-error', e.desc)
        }
      })
      .map((response) => response.body as Array<MealResponse | MealMissingResponse>)
  }

  /**
   * Cancel a meal (status transition CREATED -> CANCELLED)
   */
  public cancelMeal(params: {
    mealId: number
    groupId: string
  }): ResultAsync<MealResponse, MealError> {
    const query = new URLSearchParams()
    query.append('group_id', params.groupId)
    const url = `/v1/meals/${params.mealId}/cancel?${query.toString()}`

    return httpPost(httpClients.auth, url, {})
      .mapErr((e) => {
        switch (e.type) {
          case 'unauthorized':
            return createMealError('unauthorized', e.desc)
          case 'path-not-found':
            return createMealError('not-found', e.desc)
          default:
            return createMealError('network-error', e.desc)
        }
      })
      .map((response) => response.body as MealResponse)
  }

  /**
   * Reopen a meal (status transition CANCELLED -> CREATED)
   */
  public reopenMeal(params: {
    mealId: number
    groupId: string
  }): ResultAsync<MealResponse, MealError> {
    const query = new URLSearchParams()
    query.append('group_id', params.groupId)
    const url = `/v1/meals/${params.mealId}/reopen?${query.toString()}`

    return httpPost(httpClients.auth, url, {})
      .mapErr((e) => {
        switch (e.type) {
          case 'unauthorized':
            return createMealError('unauthorized', e.desc)
          case 'path-not-found':
            return createMealError('not-found', e.desc)
          default:
            return createMealError('network-error', e.desc)
        }
      })
      .map((response) => response.body as MealResponse)
  }
}

export const mealService = new MealService()


