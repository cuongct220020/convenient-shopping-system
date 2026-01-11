import z from 'zod'

// Ingredient type enum
export const IngredientTypeSchema = z.enum([
  'countable_ingredient',
  'uncountable_ingredient'
])
export type IngredientType = z.infer<typeof IngredientTypeSchema>

// Individual ingredient schema
export const IngredientSchema = z
  .object({
    type: IngredientTypeSchema,
    estimated_shelf_life: z.number().nonnegative().nullable().optional(),
    protein: z.number().nonnegative().nullable().optional(),
    fat: z.number().nonnegative().nullable().optional(),
    carb: z.number().nonnegative().nullable().optional(),
    fiber: z.number().nonnegative().nullable().optional(),
    calories: z.number().nonnegative().nullable().optional(),
    estimated_price: z.number().nonnegative().nullable().optional(),
    ingredient_tag_list: z.array(z.string()).nullable().optional(),
    component_id: z.number().int().positive(),
    component_name: z.string(),
    category: z.string().nullable().optional(),
    // API is inconsistent, sometimes returns c_measurement_unit, sometimes uc_measurement_unit
    c_measurement_unit: z.string().nullable().optional(),
    uc_measurement_unit: z.string().nullable().optional()
  })
  .transform((data) => ({
    ...data,
    // Normalize to always use measurementUnit for internal use
    measurementUnit: data.uc_measurement_unit || data.c_measurement_unit || null
  }))
export type Ingredient = z.infer<typeof IngredientSchema>

// Ingredient search response schema with pagination
export const IngredientSearchResponseSchema = z.object({
  message: z.string().nullable(),
  data: z.array(IngredientSchema),
  next_cursor: z.number().int().nonnegative().nullable(),
  size: z.number().int().nonnegative()
})
export type IngredientSearchResponse = z.infer<
  typeof IngredientSearchResponseSchema
>

export const GetIngredientsResponseSchema = z.object({
  message: z.string().nullable(),
  data: z.array(IngredientSchema),
  next_cursor: z.number().nullable(),
  size: z.number()
})

export type GetIngredientsResponse = z.infer<
  typeof GetIngredientsResponseSchema
>
