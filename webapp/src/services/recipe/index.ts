import { ResultAsync } from 'neverthrow'
import { httpGet, type Clients, httpClients } from '../client'

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

type RecipeErrorType = 'network-error' | 'not-found' | 'unauthorized'

function createRecipeError(type: string, desc: string | null = null) {
  return { type, desc } as const
}

type RecipeError = ReturnType<typeof createRecipeError>

export class RecipeService {
  constructor(private clients: Clients) {}

  /**
   * Search recipes by keyword with cursor-based pagination
   */
  public searchRecipes(
    keyword: string,
    cursor?: number,
    limit: number = 10
  ): ResultAsync<RecipesSearchResponse, RecipeError> {
    const queryParams = new URLSearchParams()
    queryParams.append('keyword', keyword)
    if (cursor !== undefined) {
      queryParams.append('cursor', String(cursor))
    }
    queryParams.append('limit', String(limit))
    const url = `/v2/recipes/search?${queryParams.toString()}`

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
          data: body.data || [],
          next_cursor: body.next_cursor || null,
          size: body.size || 0
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
}

export const recipeService = new RecipeService(httpClients)

