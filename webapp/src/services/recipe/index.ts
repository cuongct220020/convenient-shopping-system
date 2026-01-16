import { ResultAsync } from 'neverthrow'
import { AppUrl, httpGet, httpPost, type Clients, httpClients } from '../client'

export interface Recipe {
  component_id: number
  component_name: string
  level: string
  default_servings: number
  instructions: string[]
  keywords: string[]
  component_list: Array<{
    component_id: number
    quantity: number
  }>
  image_url?: string | null
  prep_time?: number | null
  cook_time?: number | null
}

export interface RecipeDetailedResponse {
  component_id: number
  component_name: string
  type: 'recipe'
  level: string
  default_servings: number
  instructions: string[]
  keywords: string[]
  image_url?: string | null
  prep_time?: number | null
  cook_time?: number | null
  component_list: Array<{
    quantity: number
    component: {
      type: 'ingredient' | 'recipe'
      component_id: number
      component_name: string
      [key: string]: unknown
    }
  }>
}

export interface RecipesSearchResponse {
  data: Recipe[]
  next_cursor: number | null
  size: number
}

export type FlattenedIngredient = {
  quantity: number
  ingredient: {
    type: 'countable_ingredient' | 'uncountable_ingredient'
    component_id: number
    component_name: string
    c_measurement_unit?: string
    uc_measurement_unit?: string
    [key: string]: unknown
  }
  available?: boolean | null
}

export type FlattenedIngredientsResponse = {
  ingredients: FlattenedIngredient[]
}

type RecipeErrorType = 'network-error' | 'not-found' | 'unauthorized'

function createRecipeError(type: string, desc: string | null = null) {
  return { type, desc } as const
}

type RecipeError = ReturnType<typeof createRecipeError>

export class RecipeService {
  constructor(private clients: Clients) {}

  /**
   * Get list of recipes with cursor-based pagination
   */
  public getRecipes(
    cursor?: number,
    limit: number = 10
  ): ResultAsync<RecipesSearchResponse, RecipeError> {
    const queryParams = new URLSearchParams()
    if (cursor !== undefined) {
      queryParams.append('cursor', String(cursor))
    }
    queryParams.append('limit', String(limit))

    const url = `${AppUrl.RECIPES}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`

    return httpGet(this.clients.recipe, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createRecipeError('not-found', e.desc)
          case 'unauthorized':
            return createRecipeError('unauthorized', e.desc)
          default:
            return createRecipeError('network-error', e.desc)
        }
      })
      .map((response) => {
        const body = response.body as any
        return {
          data: body?.data ?? body?.results ?? [],
          next_cursor: body?.next_cursor ?? null,
          size: body?.size ?? 0
        } as RecipesSearchResponse
      })
  }

  /**
   * Search recipes by keyword with cursor-based pagination
   */
  public searchRecipes(
    keyword: string,
    cursor?: number,
    limit: number = 10
  ): ResultAsync<RecipesSearchResponse, RecipeError> {
    // If there is no search keyword, fall back to regular listing.
    if (!keyword?.trim()) {
      return this.getRecipes(cursor, limit)
    }

    const queryParams = new URLSearchParams()
    queryParams.append('keyword', keyword)
    if (cursor !== undefined) {
      queryParams.append('cursor', String(cursor))
    }
    queryParams.append('limit', String(limit))
    const url = `${AppUrl.RECIPES}search?${queryParams.toString()}`

    return httpGet(this.clients.recipe, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createRecipeError('not-found', e.desc)
          case 'unauthorized':
            return createRecipeError('unauthorized', e.desc)
          default:
            return createRecipeError('network-error', e.desc)
        }
      })
      .map((response) => {
        const body = response.body as any
        return {
          data: body?.data ?? body?.results ?? [],
          next_cursor: body?.next_cursor ?? null,
          size: body?.size ?? 0
        } as RecipesSearchResponse
      })
  }

  /**
   * Get recipe by ID
   */
  public getRecipeById(recipeId: number): ResultAsync<Recipe, RecipeError> {
    const url = `/v2/recipes/${recipeId}`

    return httpGet(this.clients.recipe, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createRecipeError('not-found', e.desc)
          case 'unauthorized':
            return createRecipeError('unauthorized', e.desc)
          default:
            return createRecipeError('network-error', e.desc)
        }
      })
      .map((response) => response.body as Recipe)
  }

  /**
   * Get detailed recipe by ID
   */
  public getRecipeDetailed(recipeId: number): ResultAsync<RecipeDetailedResponse, RecipeError> {
    const url = `/v2/recipes/detailed/${recipeId}`

    return httpGet(this.clients.recipe, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createRecipeError('not-found', e.desc)
          case 'unauthorized':
            return createRecipeError('unauthorized', e.desc)
          default:
            return createRecipeError('network-error', e.desc)
        }
      })
      .map((response) => response.body as RecipeDetailedResponse)
  }

  /**
   * Get flattened ingredient list for one or more recipes
   */
  public getFlattened(
    recipesWithQuantity: Array<{ recipe_id: number; quantity: number }>,
    opts?: { checkExistence?: boolean; groupId?: string }
  ): ResultAsync<FlattenedIngredientsResponse, RecipeError> {
    const params = new URLSearchParams()
    params.append('check_existence', String(Boolean(opts?.checkExistence)))
    if (opts?.groupId) params.append('group_id', opts.groupId)
    const url = `/v2/recipes/flattened?${params.toString()}`

    return httpPost(this.clients.recipe, url, recipesWithQuantity)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createRecipeError('not-found', e.desc)
          case 'unauthorized':
            return createRecipeError('unauthorized', e.desc)
          default:
            return createRecipeError('network-error', e.desc)
        }
      })
      .map((response) => response.body as FlattenedIngredientsResponse)
  }

  /**
   * Get recommended recipes for a group
   */
  public getRecommendedRecipes(groupId: string): ResultAsync<Recipe[], RecipeError> {
    const url = `/v2/recipes/recommend?group_id=${encodeURIComponent(groupId)}`

    return httpGet(this.clients.recipe, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createRecipeError('not-found', e.desc)
          case 'unauthorized':
            return createRecipeError('unauthorized', e.desc)
          default:
            return createRecipeError('network-error', e.desc)
        }
      })
      .map((response) => {
        const body = response.body as any
        // API returns List[RecipeResponse] which is already the full recipe data
        return Array.isArray(body) ? body as Recipe[] : []
      })
  }
}

export const recipeService = new RecipeService(httpClients)

