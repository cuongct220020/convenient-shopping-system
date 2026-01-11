import z from 'zod'

export const IngredientZ = z.object({
  component_id: z.number(),
  component_name: z.string(),
  category: z.string(),
  c_measurement_unit: z.string().optional(),
  type: z.string().optional(),
  estimated_shelf_life: z.number().nullable().optional(),
  protein: z.number().optional(),
  fat: z.number().optional(),
  carb: z.number().optional(),
  fiber: z.number().optional(),
  calories: z.number().optional(),
  estimated_price: z.number().nullable().optional(),
  ingredient_tag_list: z.any().nullable().optional()
})

export type Ingredient = z.infer<typeof IngredientZ>

export const GetIngredientsResponseSchema = z.object({
  message: z.string().nullable(),
  data: z.array(IngredientZ),
  next_cursor: z.number().nullable(),
  size: z.number()
})

export type GetIngredientsResponse = z.infer<
  typeof GetIngredientsResponseSchema
>
