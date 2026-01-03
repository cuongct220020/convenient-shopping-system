import { ResultAsync } from 'neverthrow'
import {
  AppUrl,
  Clients,
  httpClients,
  httpGet,
  httpPost,
  httpPut,
  httpPatch,
  httpDelete,
  ResponseError
} from '../client'
import { parseZodObject } from '../../utils/zod-result'
import {
  GroupListResponseSchema,
  GroupCreateResponseSchema,
  GroupUpdateResponseSchema,
  GroupDetailResponseSchema,
  AddMemberResponseSchema,
  RemoveMemberResponseSchema,
  SetLeaderResponseSchema,
  UpdateMemberRoleResponseSchema,
  LeaveGroupResponseSchema,
  type GroupListResponse,
  type GroupCreateResponse,
  type GroupUpdateResponse,
  type GroupDetailResponse,
  type AddMemberResponse,
  type RemoveMemberResponse,
  type SetLeaderResponse,
  type UpdateMemberRoleResponse,
  type LeaveGroupResponse
} from '../schema/groupSchema'

type GroupError = ResponseError<
  'not-found' | 'validation-error' | 'unauthorized'
>

export class GroupService {
  constructor(private clients: Clients) {}

  /**
   * Get all groups for the authenticated user
   */
  public getGroups(): ResultAsync<GroupListResponse, GroupError> {
    return httpGet(this.clients.auth, AppUrl.GROUPS)
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(GroupListResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Create a new group
   */
  public createGroup(
    groupName: string,
    avatarUrl?: string
  ): ResultAsync<GroupCreateResponse, GroupError> {
    const requestData = {
      group_name: groupName,
      group_avatar_url: avatarUrl ?? null
    }

    return httpPost(this.clients.auth, AppUrl.GROUPS, requestData)
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(GroupCreateResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Update an existing group
   */
  public updateGroup(
    groupId: string,
    groupName: string,
    avatarUrl?: string
  ): ResultAsync<GroupUpdateResponse, GroupError> {
    const requestData = {
      group_name: groupName,
      group_avatar_url: avatarUrl ?? null
    }

    return httpPut(this.clients.auth, AppUrl.GROUP_BY_ID(groupId), requestData)
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(GroupUpdateResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Delete a group
   */
  public deleteGroup(groupId: string): ResultAsync<void, GroupError> {
    return httpDelete(this.clients.auth, AppUrl.GROUP_BY_ID(groupId))
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .map(() => undefined)
  }

  /**
   * Get group detail by ID
   */
  public getGroupById(
    groupId: string
  ): ResultAsync<GroupDetailResponse, GroupError> {
    return httpGet(this.clients.auth, AppUrl.GROUP_BY_ID(groupId))
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(GroupDetailResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Get group members by group ID
   * Uses the /groups/{id}/members endpoint which returns group with memberships
   */
  public getGroupMembers(
    groupId: string
  ): ResultAsync<GroupDetailResponse, GroupError> {
    return httpGet(this.clients.auth, AppUrl.GROUP_MEMBERS(groupId))
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          default:
            return e
        }
      })
      .andThen((response) => {
        return parseZodObject(GroupDetailResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      })
  }

  /**
   * Add a member to the group
   */
  public addMember(
    groupId: string,
    identifier: string
  ): ResultAsync<AddMemberResponse, GroupError> {
    return httpPost(this.clients.auth, AppUrl.GROUP_MEMBERS(groupId), {
      identifier
    })
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(AddMemberResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Remove a member from the group
   */
  public removeMember(
    groupId: string,
    userId: string
  ): ResultAsync<RemoveMemberResponse, GroupError> {
    return httpDelete(
      this.clients.auth,
      AppUrl.GROUP_MEMBER_BY_ID(groupId, userId)
    )
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(RemoveMemberResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Set a member as the group leader (head_chef)
   * @deprecated Use updateMemberRole instead for role management
   */
  public setLeader(
    groupId: string,
    userId: string
  ): ResultAsync<SetLeaderResponse, GroupError> {
    return httpPut(this.clients.auth, AppUrl.GROUP_LEADER(groupId), {
      user_id: userId
    })
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(SetLeaderResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Update a member's role in the group
   * @param groupId - The group ID
   * @param userId - The user ID whose role will be updated
   * @param role - The new role ('head_chef' | 'member')
   */
  public updateMemberRole(
    groupId: string,
    userId: string,
    role: 'head_chef' | 'member' | null
  ): ResultAsync<UpdateMemberRoleResponse, GroupError> {
    return httpPatch(
      this.clients.auth,
      AppUrl.GROUP_MEMBER_BY_ID(groupId, userId),
      { role }
    )
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(UpdateMemberRoleResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Leave the group (current user leaves)
   */
  public leaveGroup(
    groupId: string
  ): ResultAsync<LeaveGroupResponse, GroupError> {
    return httpDelete(this.clients.auth, AppUrl.GROUP_LEAVE(groupId))
      .mapErr((e): GroupError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          case 'path-not-found':
            return { ...e, type: 'not-found' }
          case 'forbidden':
            return { ...e, type: 'validation-error' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(LeaveGroupResponseSchema, response.body).mapErr(
          (e): GroupError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }
}

export const groupService = new GroupService(httpClients)
