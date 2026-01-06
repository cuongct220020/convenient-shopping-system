import z from 'zod'
import { ResultAsync } from 'neverthrow'
import {
  AppUrl,
  Clients,
  httpClients,
  httpGet,
  httpPost,
  ResponseError
} from '../client'
import { parseZodObject } from '../../utils/zod-result'
import {
  UserCoreInfoSchema,
  CurrentUserResponseSchema,
  UserIdentityProfileSchema,
  UserIdentityProfileResponseSchema,
  UserHealthProfileSchema,
  UserHealthProfileResponseSchema,
  SearchUsersResponseSchema,
  AdminUsersListResponseSchema,
  type CurrentUserResponse,
  type UserIdentityProfileResponse,
  type UserHealthProfileResponse,
  type SearchUsersResponse,
  type UserCoreInfo,
  type AdminUsersListResponse
} from '../schema/groupSchema'

type UserError = ResponseError<'not-found' | 'validation-error' | 'unauthorized'>

export class UserService {
  constructor(private clients: Clients) {}

  /**
   * Get current user's profile information
   */
  public getCurrentUser(): ResultAsync<CurrentUserResponse, UserError> {
    return httpGet(this.clients.auth, AppUrl.USERS_ME)
      .mapErr((e): UserError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(CurrentUserResponseSchema, response.body).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Get user by ID
   */
  public getUserById(userId: string): ResultAsync<{ data: UserCoreInfo }, UserError> {
    return httpGet(this.clients.auth, AppUrl.USER_BY_ID(userId))
      .mapErr((e): UserError => {
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
        // Wrap the user data in the expected format
        const wrappedResponse = {
          body: {
            status: 'success',
            message: null,
            data: response.body
          }
        }
        return parseZodObject(
          z.object({
            status: z.literal('success'),
            message: z.string().nullable(),
            data: UserCoreInfoSchema
          }),
          wrappedResponse.body
        ).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      })
  }

  /**
   * Get user identity profile by user ID
   */
  public getUserIdentityProfile(
    userId: string
  ): ResultAsync<UserIdentityProfileResponse, UserError> {
    return httpGet(this.clients.auth, AppUrl.USER_IDENTITY_PROFILE_BY_ID(userId))
      .mapErr((e): UserError => {
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
        parseZodObject(UserIdentityProfileResponseSchema, response.body).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Get user health profile by user ID
   */
  public getUserHealthProfile(
    userId: string
  ): ResultAsync<UserHealthProfileResponse, UserError> {
    return httpGet(this.clients.auth, AppUrl.USER_HEALTH_PROFILE_BY_ID(userId))
      .mapErr((e): UserError => {
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
        parseZodObject(UserHealthProfileResponseSchema, response.body).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Search for users by email
   */
  public searchUsersByEmail(email: string): ResultAsync<SearchUsersResponse, UserError> {
    return httpPost(this.clients.auth, AppUrl.USER_SEARCH, { email })
      .mapErr((e): UserError => {
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
        parseZodObject(SearchUsersResponseSchema, response.body).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Get current user's identity profile
   */
  public getMyIdentityProfile(): ResultAsync<UserIdentityProfileResponse, UserError> {
    return httpGet(this.clients.auth, AppUrl.USERS_ME_IDENTITY_PROFILE)
      .mapErr((e): UserError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(UserIdentityProfileResponseSchema, response.body).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Get current user's health profile
   */
  public getMyHealthProfile(): ResultAsync<UserHealthProfileResponse, UserError> {
    return httpGet(this.clients.auth, AppUrl.USERS_ME_HEALTH_PROFILE)
      .mapErr((e): UserError => {
        switch (e.type) {
          case 'unauthorized':
            return { ...e, type: 'unauthorized' }
          default:
            return e
        }
      })
      .andThen((response) =>
        parseZodObject(UserHealthProfileResponseSchema, response.body).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }

  /**
   * Get list of users (admin endpoint with pagination)
   * @param page - Page number (default: 1)
   * @param pageSize - Number of items per page (default: 10)
   */
  public getUsersList(
    page: number = 1,
    pageSize: number = 10
  ): ResultAsync<AdminUsersListResponse, UserError> {
    return httpGet(
      this.clients.auth,
      `${AppUrl.ADMIN_USERS}?page=${page}&page_size=${pageSize}`
    )
      .mapErr((e): UserError => {
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
        parseZodObject(AdminUsersListResponseSchema, response.body).mapErr(
          (e): UserError => ({
            type: 'invalid-response-format',
            desc: e
          })
        )
      )
  }
}

export const userService = new UserService(httpClients)
