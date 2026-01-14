import { ResultAsync } from 'neverthrow'
import {
  AppUrl,
  Clients,
  httpClients,
  httpGet,
  httpPost,
  httpPut,
  httpDelete
} from '../client'
import { parseZodObject } from '../../utils/zod-result'
import {
  ShoppingPlansFilterResponseSchema,
  type ShoppingPlansFilterResponse,
  type PlanItemBase,
  PlanResponseSchema,
  type PlanResponse
} from '../schema/shoppingPlanSchema'

type ShoppingPlanError = ReturnType<typeof createShoppingPlanError>

function createShoppingPlanError(type: string, desc: string | null = null) {
  return { type, desc } as const
}

export type ShoppingPlanErrorType =
  | 'not-found'
  | 'validation-error'
  | 'unauthorized'

export class ShoppingPlanService {
  constructor(private clients: Clients) {}

  /**
   * Get a shopping plan by ID
   */
  public getPlanById(
    planId: number
  ): ResultAsync<PlanResponse, ShoppingPlanError> {
    const url = `${AppUrl.SHOPPING_PLANS}${planId}`

    return httpGet(this.clients.auth, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .andThen((response) =>
        parseZodObject(PlanResponseSchema, response.body).mapErr((e) =>
          createShoppingPlanError('validation-error', e)
        )
      )
  }

  /**
   * Filter shopping plans by group_id and optionally by plan_status
   */
  public filterPlans(
    groupId: string,
    options?: {
      planStatus?:
        | 'created'
        | 'in_progress'
        | 'completed'
        | 'cancelled'
        | 'expired'
      sortBy?: 'last_modified' | 'deadline'
      order?: 'asc' | 'desc'
      cursor?: number | null
      limit?: number
    }
  ): ResultAsync<ShoppingPlansFilterResponse, ShoppingPlanError> {
    const params = new URLSearchParams()
    params.append('group_id', groupId)

    if (options?.planStatus) {
      params.append('plan_status', options.planStatus)
    }
    if (options?.sortBy) {
      params.append('sort_by', options.sortBy)
    }
    if (options?.order) {
      params.append('order', options.order)
    }
    if (options?.cursor !== undefined && options.cursor !== null) {
      params.append('cursor', options.cursor.toString())
    }
    if (options?.limit !== undefined) {
      params.append('limit', options.limit.toString())
    }

    const url = `${AppUrl.SHOPPING_PLANS_FILTER}?${params.toString()}`

    return httpGet(this.clients.auth, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .andThen((response) =>
        parseZodObject(ShoppingPlansFilterResponseSchema, response.body).mapErr(
          (e) => createShoppingPlanError('validation-error', e)
        )
      )
  }

  /**
   * Create a new shopping plan
   */
  public createPlan(params: {
    groupId: string
    deadline: string
    assignerId: string
    shoppingList: PlanItemBase[]
    others?: Record<string, unknown>
  }): ResultAsync<{ message: string }, ShoppingPlanError> {
    const body: Record<string, unknown> = {
      group_id: params.groupId,
      deadline: params.deadline,
      assigner_id: params.assignerId,
      shopping_list: params.shoppingList
    }

    // Only add others if it has values
    if (params.others && Object.keys(params.others).length > 0) {
      body.others = params.others
    }

    // Debug logging
    console.log('Create plan request body:', JSON.stringify(body, null, 2))

    return httpPost(this.clients.auth, AppUrl.SHOPPING_PLANS, body)
      .mapErr((e) => {
        switch (e.type) {
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .map((response) => response.body as { message: string })
  }

  /**
   * Update an existing shopping plan
   */
  public updatePlan(
    planId: number,
    params: {
      deadline: string
      shoppingList: PlanItemBase[]
      others?: Record<string, unknown> | null
    }
  ): ResultAsync<{ message: string }, ShoppingPlanError> {
    const body: Record<string, unknown> = {
      deadline: params.deadline,
      shopping_list: params.shoppingList
    }

    // Only add others if it has values
    if (params.others && Object.keys(params.others).length > 0) {
      body.others = params.others
    }

    // Debug logging
    console.log('Update plan request body:', JSON.stringify(body, null, 2))

    return httpPut(this.clients.auth, `${AppUrl.SHOPPING_PLANS}${planId}`, body)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .map((response) => response.body as { message: string })
  }

  /**
   * Cancel a shopping plan by ID
   */
  public cancelPlan(
    planId: number,
    assignerId: string
  ): ResultAsync<PlanResponse, ShoppingPlanError> {
    const url = `${AppUrl.SHOPPING_PLANS}${planId}/cancel?assigner_id=${assignerId}`

    return httpPost(this.clients.auth, url, {})
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .andThen((response) =>
        parseZodObject(PlanResponseSchema, response.body).mapErr((e) =>
          createShoppingPlanError('validation-error', e)
        )
      )
  }

  /**
   * Reopen a cancelled shopping plan by ID
   */
  public reopenPlan(
    planId: number,
    assignerId: string
  ): ResultAsync<PlanResponse, ShoppingPlanError> {
    const url = `${AppUrl.SHOPPING_PLANS}${planId}/reopen?assigner_id=${assignerId}`

    return httpPost(this.clients.auth, url, {})
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .andThen((response) =>
        parseZodObject(PlanResponseSchema, response.body).mapErr((e) =>
          createShoppingPlanError('validation-error', e)
        )
      )
  }

  /**
   * Delete a shopping plan by ID
   */
  public deletePlan(
    planId: number
  ): ResultAsync<{ message: string }, ShoppingPlanError> {
    return httpDelete(this.clients.auth, `${AppUrl.SHOPPING_PLANS}${planId}`)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .map((response) => response.body as { message: string })
  }

  /**
   * Assign a shopping plan to an assignee (start implementation)
   */
  public assignPlan(
    planId: number,
    assigneeId: string,
    assigneeUsername: string
  ): ResultAsync<PlanResponse, ShoppingPlanError> {
    const url = `${AppUrl.SHOPPING_PLANS}${planId}/assign?assignee_id=${assigneeId}&assignee_username=${assigneeUsername}`

    return httpPost(this.clients.auth, url, {})
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .andThen((response) =>
        parseZodObject(PlanResponseSchema, response.body).mapErr((e) =>
          createShoppingPlanError('validation-error', e)
        )
      )
  }

  /**
   * Report a shopping plan as completed (confirm implementation)
   * Returns response with message and optional missing_items if report is incomplete
   */
  public reportPlan(
    planId: number,
    assigneeId: string,
    assigneeUsername: string,
    report: {
      plan_id: number
      report_content: Array<{
        storage_id: number
        package_quantity: number
        unit_name: string
        component_id?: number | null
        content_type?: 'countable_ingredient' | 'uncountable_ingredient' | null
        content_quantity?: number | null
        content_unit?: string | null
        expiration_date?: string | null
      }>
      spent_amount: number
    },
    confirm: boolean = false
  ): ResultAsync<
    | { message: string; missing_items?: undefined }
    | { message: string; missing_items: Array<{ component_id: number; component_name: string; missing_quantity: number }> },
    ShoppingPlanError
  > {
    const url = `${AppUrl.SHOPPING_PLANS}${planId}/report?assignee_id=${assigneeId}&assignee_username=${assigneeUsername}&confirm=${confirm}`

    return httpPost(this.clients.auth, url, report)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .map((response) => {
        const body = response.body as { message: string; data?: { missing_items?: Array<{ component_id: number; component_name: string; missing_quantity: number }> } }
        if (body.data?.missing_items) {
          return {
            message: body.message,
            missing_items: body.data.missing_items
          }
        }
        return {
          message: body.message
        }
      })
  }

  /**
   * Unassign a shopping plan from the assignee (cancel implementation)
   */
  public unassignPlan(
    planId: number,
    assigneeId: string,
    assigneeUsername: string
  ): ResultAsync<{ message: string }, ShoppingPlanError> {
    const url = `${AppUrl.SHOPPING_PLANS}${planId}/unassign?assignee_id=${assigneeId}&assignee_username=${assigneeUsername}`

    return httpPost(this.clients.auth, url, {})
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createShoppingPlanError('not-found', e.desc)
          case 'unauthorized':
            return createShoppingPlanError('unauthorized', e.desc)
          default:
            return createShoppingPlanError(e.type, e.desc)
        }
      })
      .map((response) => response.body as { message: string })
  }
}

export const shoppingPlanService = new ShoppingPlanService(httpClients)
