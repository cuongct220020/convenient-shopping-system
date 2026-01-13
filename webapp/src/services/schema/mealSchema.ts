import z from 'zod'

// Recipe in meal schema
export const MealRecipeSchema = z.object({
  recipe_id: z.number(),
  recipe_name: z.string(),
  servings: z.number()
})
export type MealRecipe = z.infer<typeof MealRecipeSchema>

export const MealTypeSchema = z.enum(['breakfast', 'lunch', 'dinner'])
export type MealType = z.infer<typeof MealTypeSchema>

export const MealStatusSchema = z.enum(['created', 'in_progress', 'completed'])
export type MealStatus = z.infer<typeof MealStatusSchema>

// Planned meal schema (with recipe_list)
export const PlannedMealSchema = z.object({
  meal_id: z.number(),
  date: z.string(),
  group_id: z.uuid(),
  meal_type: MealTypeSchema,
  meal_status: MealStatusSchema,
  recipe_list: z.array(MealRecipeSchema)
})
export type PlannedMeal = z.infer<typeof PlannedMealSchema>

// Unplanned meal schema (without recipe_list)
export const UnplannedMealSchema = z.object({
  date: z.string(),
  group_id: z.uuid(),
  meal_type: MealTypeSchema,
  detail: z.string().includes('has not been planned')
})
export type UnplannedMeal = z.infer<typeof UnplannedMealSchema>

// Discriminated union for meal
export const MealSchema = z.union([
  PlannedMealSchema,
  UnplannedMealSchema.extend({
    meal_id: z.never().optional()
  })
])
export type Meal = z.infer<typeof MealSchema>

// Response type for meals list
export const MealsResponseSchema = z.array(MealSchema)
export type MealsResponse = z.infer<typeof MealsResponseSchema>
