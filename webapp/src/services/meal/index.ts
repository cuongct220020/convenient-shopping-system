import { ResultAsync } from 'neverthrow'
import { AppUrl, Clients, httpClients, httpGet, ResponseError } from '../client'
import { parseZodObject } from '../../utils/zod-result'
import { MealsResponseSchema, type MealsResponse } from '../schema/mealSchema'

type MealError = ResponseError<never>

export class MealService {
  constructor(private clients: Clients) {}

  /**
   * Get meals by group and date
   */
  public getMealsByGroupAndDate(
    groupId: string,
    date: Date
  ): ResultAsync<MealsResponse, MealError> {
    date = new Date(date)
    date.setHours(1)
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()

    const dateString = `${year}-${month.toString().padStart(2, '0')}-${day
      .toString()
      .padStart(2, '0')}`

    const params = new URLSearchParams()
    params.append('meal_date', dateString)
    params.append('group_id', groupId)

    const url = `${AppUrl.MEALS}?${params.toString()}`

    return httpGet(this.clients.auth, url).andThen((response) =>
      parseZodObject(MealsResponseSchema, response.body).mapErr(
        (e) => ({ type: 'invalid-response-format', desc: e }) as const
      )
    )
  }
}

export const mealService = new MealService(httpClients)
