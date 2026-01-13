import z from 'zod'

export const DishLevelTypeSchema = z.enum(['Dễ', 'Trung bình', 'Khó'])
export type DishLevelType = z.infer<typeof DishLevelTypeSchema>

export const DishCreateSchema = z.object({
  component_name: z.string(),
  image_url: z.string().nullable().optional(),
  prep_time: z.number().int().nonnegative().nullable().optional(),
  cook_time: z.number().int().nonnegative().nullable().optional(),
  level: DishLevelTypeSchema.optional(),
  default_servings: z.number().int().positive(),
  instructions: z.array(z.string()),
  keywords: z.array(z.string()),
  component_list: z.array(
    z.object({
      component_id: z.number().int().positive(),
      quantity: z.number().nonnegative()
    })
  )
})
export const DishSchema = DishCreateSchema.extend({
  component_id: z.number().int().positive()
})
export type Dish = z.infer<typeof DishSchema>

export const GetDishesResponseSchema = z.object({
  message: z.string().nullable(),
  data: z.array(DishSchema),
  next_cursor: z.number().int().nonnegative().nullable(),
  size: z.number().int().nonnegative()
})
export type GetDishesResponse = z.infer<typeof GetDishesResponseSchema>
