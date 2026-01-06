import z from 'zod'

// Group role enum
export const GroupRoleSchema = z.enum(['head_chef', 'member'])
export type GroupRole = z.infer<typeof GroupRoleSchema>

// User core info schema - lenient version to handle partial data from API
// Using z.any() and transforming to handle any data from API
// API returns user_id, but we support both id and user_id for compatibility
export const UserCoreInfoSchema = z.object({
  id: z.any().optional(),
  user_id: z.any().optional(),
  username: z.any(),
  email: z.any(),
  phone_num: z.any().nullable(),
  first_name: z.any().nullable(),
  last_name: z.any().nullable(),
  avatar_url: z.any().nullable()
}).transform((data) => ({
  // Normalize to always have id field
  id: data.id ?? data.user_id,
  user_id: data.user_id ?? data.id,
  username: data.username,
  email: data.email,
  phone_num: data.phone_num,
  first_name: data.first_name,
  last_name: data.last_name,
  avatar_url: data.avatar_url
}))
export type UserCoreInfo = z.infer<typeof UserCoreInfoSchema>

// User group schema (for list view)
export const UserGroupSchema = z.object({
  id: z.string().uuid(),
  group_name: z.string(),
  group_avatar_url: z.string().nullable(),
  creator: UserCoreInfoSchema.nullable(),
  role_in_group: GroupRoleSchema,
  member_count: z.number()
})
export type UserGroup = z.infer<typeof UserGroupSchema>

// Group membership schema
export const GroupMembershipSchema = z.object({
  user: UserCoreInfoSchema,
  role: GroupRoleSchema
})
export type GroupMembership = z.infer<typeof GroupMembershipSchema>

// Family group detailed schema (for single group view)
export const FamilyGroupDetailedSchema = z.object({
  id: z.string().uuid(),
  group_name: z.string(),
  group_avatar_url: z.string().nullable(),
  creator: UserCoreInfoSchema.nullable(),
  // API returns 'members' but we alias it to 'group_memberships' for consistency
  group_memberships: z.array(GroupMembershipSchema).optional().default([]),
  members: z.array(GroupMembershipSchema).optional().default([])
})
export type FamilyGroupDetailed = z.infer<typeof FamilyGroupDetailedSchema>

// Group list response schema
export const GroupListResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.object({
    groups: z.array(UserGroupSchema)
  })
})
export type GroupListResponse = z.infer<typeof GroupListResponseSchema>

// Group create request schema
export const GroupCreateRequestSchema = z.object({
  group_name: z.string().min(3).max(255),
  group_avatar_url: z.string().nullable().optional()
})
export type GroupCreateRequest = z.infer<typeof GroupCreateRequestSchema>

// Group create response schema
export const GroupCreateResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: FamilyGroupDetailedSchema
})
export type GroupCreateResponse = z.infer<typeof GroupCreateResponseSchema>

// Group update request schema
export const GroupUpdateRequestSchema = z.object({
  group_name: z.string().min(3).max(255),
  group_avatar_url: z.string().nullable().optional()
})
export type GroupUpdateRequest = z.infer<typeof GroupUpdateRequestSchema>

// Group update response schema
export const GroupUpdateResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: FamilyGroupDetailedSchema
})
export type GroupUpdateResponse = z.infer<typeof GroupUpdateResponseSchema>

// Generic success response (for delete)
export const GenericSuccessResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.unknown().nullable()
})
export type GenericSuccessResponse = z.infer<
  typeof GenericSuccessResponseSchema
>

// Group detail response schema
export const GroupDetailResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: FamilyGroupDetailedSchema
})
export type GroupDetailResponse = z.infer<typeof GroupDetailResponseSchema>

// Search users request schema
export const SearchUsersRequestSchema = z.object({
  email: z.string().email()
})
export type SearchUsersRequest = z.infer<typeof SearchUsersRequestSchema>

// Search users response schema
export const SearchUsersResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.object({
    user: UserCoreInfoSchema.optional().nullable()
  })
})
export type SearchUsersResponse = z.infer<typeof SearchUsersResponseSchema>

// Add member request schema
export const AddMemberRequestSchema = z.object({
  identifier: z.string()
})
export type AddMemberRequest = z.infer<typeof AddMemberRequestSchema>

// Add member response schema
export const AddMemberResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.unknown().nullable()
})
export type AddMemberResponse = z.infer<typeof AddMemberResponseSchema>

// Remove member response schema (API returns data: null on success)
export const RemoveMemberResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: FamilyGroupDetailedSchema.nullable()
})
export type RemoveMemberResponse = z.infer<typeof RemoveMemberResponseSchema>

// Set leader request schema
export const SetLeaderRequestSchema = z.object({
  user_id: z.string().uuid()
})
export type SetLeaderRequest = z.infer<typeof SetLeaderRequestSchema>

// Set leader response schema
export const SetLeaderResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: FamilyGroupDetailedSchema
})
export type SetLeaderResponse = z.infer<typeof SetLeaderResponseSchema>

// Update member role response schema
// For PATCH /groups/{id}/members/{userId} endpoint
export const UpdateMemberRoleResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.unknown().nullable()
})
export type UpdateMemberRoleResponse = z.infer<
  typeof UpdateMemberRoleResponseSchema
>

// Leave group response schema
export const LeaveGroupResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.unknown().nullable()
})
export type LeaveGroupResponse = z.infer<typeof LeaveGroupResponseSchema>

// Current user info response schema
export const CurrentUserResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: UserCoreInfoSchema
})
export type CurrentUserResponse = z.infer<typeof CurrentUserResponseSchema>

// User identity profile schema
export const UserIdentityProfileSchema = z.object({
  user_id: z.string().uuid(),
  gender: z.enum(['male', 'female', 'other']),
  date_of_birth: z.string().nullable().optional(),
  occupation: z.string().nullable().optional(),
  address: z
    .object({
      ward: z.string().nullable().optional(),
      district: z.string().nullable().optional(),
      city: z.string().nullable().optional(),
      province: z.string().nullable().optional()
    })
    .nullable()
    .optional()
})
export type UserIdentityProfile = z.infer<typeof UserIdentityProfileSchema>

// User identity profile response schema
export const UserIdentityProfileResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: UserIdentityProfileSchema
})
export type UserIdentityProfileResponse = z.infer<
  typeof UserIdentityProfileResponseSchema
>

// User health profile schema
export const UserHealthProfileSchema = z.object({
  user_id: z.string().uuid().nullable().optional(),
  height_cm: z.number().int().positive().nullable().optional(),
  weight_kg: z.number().positive().nullable().optional(),
  activity_level: z
    .enum(['sedentary', 'light', 'moderate', 'active', 'very_active'])
    .nullable()
    .optional(),
  curr_condition: z
    .enum(['normal', 'pregnant', 'injured'])
    .nullable()
    .optional(),
  health_goal: z
    .enum(['lose_weight', 'maintain', 'gain_weight'])
    .nullable()
    .optional()
})
export type UserHealthProfile = z.infer<typeof UserHealthProfileSchema>

// User health profile response schema
export const UserHealthProfileResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: UserHealthProfileSchema
})
export type UserHealthProfileResponse = z.infer<
  typeof UserHealthProfileResponseSchema
>

// Admin user info schema (extends UserCoreInfoSchema with additional fields)
export const AdminUserInfoSchema = z.object({
  user_id: z.string().uuid(),
  username: z.string(),
  email: z.string(),
  phone_num: z.string().nullable(),
  first_name: z.string().nullable(),
  last_name: z.string().nullable(),
  avatar_url: z.string().nullable(),
  identity_profile: z.unknown().nullable(),
  health_profile: z.unknown().nullable(),
  system_role: z.enum(['user', 'admin']),
  is_active: z.boolean(),
  created_at: z.string(),
  last_login: z.string().nullable()
})
export type AdminUserInfo = z.infer<typeof AdminUserInfoSchema>

// Admin users list response schema (paginated)
export const AdminUsersListResponseSchema = z.object({
  status: z.literal('success'),
  message: z.string().nullable(),
  data: z.object({
    data: z.array(AdminUserInfoSchema),
    page: z.number(),
    page_size: z.number(),
    total_items: z.number(),
    total_pages: z.number()
  })
})
export type AdminUsersListResponse = z.infer<typeof AdminUsersListResponseSchema>
