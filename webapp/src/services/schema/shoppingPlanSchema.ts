import z from 'zod'

// Plan status enum
export const PlanStatusSchema = z.enum([
  'created',
  'in_progress',
  'completed',
  'cancelled',
  'expired'
])
export type PlanStatus = z.infer<typeof PlanStatusSchema>

// Plan item type enum
export const PlanItemTypeSchema = z.enum([
  'countable_ingredient',
  'uncountable_ingredient'
])
export type PlanItemType = z.infer<typeof PlanItemTypeSchema>

// Plan item base schema
export const PlanItemBaseSchema = z.object({
  type: PlanItemTypeSchema,
  unit: z.string(),
  quantity: z.number().positive(),
  component_id: z.number().int().nonnegative(),
  component_name: z.string()
})
export type PlanItemBase = z.infer<typeof PlanItemBaseSchema>

// Shopping plan response schema
export const PlanResponseSchema = z.object({
  plan_id: z.number().int().positive(),
  group_id: z.number().int().positive(),
  deadline: z.string().datetime(),
  last_modified: z.string().datetime(),
  assigner_id: z.number().int().positive(),
  assignee_id: z.number().int().positive().nullable(),
  shopping_list: z.array(PlanItemBaseSchema),
  others: z.record(z.string(), z.unknown()).optional(),
  plan_status: PlanStatusSchema
})
export type PlanResponse = z.infer<typeof PlanResponseSchema>

// Cursor pagination response for shopping plans
export const ShoppingPlansFilterResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.object({
    items: z.array(PlanResponseSchema),
    next_cursor: z.number().int().nonnegative().nullable(),
    size: z.number().int().nonnegative()
  })
})
export type ShoppingPlansFilterResponse = z.infer<
  typeof ShoppingPlansFilterResponseSchema
>
