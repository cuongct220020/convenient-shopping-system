import { ResultAsync } from 'neverthrow'
import {
  AppUrl,
  Clients,
  httpClients,
  httpPost,
  httpGet,
  httpPut,
  httpDelete
} from '../client'
import type { FoodStorageCategory } from '../../utils/constants'

type StorageError = ReturnType<typeof createStorageError>

function createStorageError(type: string, desc: string | null = null) {
  return { type, desc } as const
}

export type StorageErrorType =
  | 'not-found'
  | 'unauthorized'
  | 'network-error'

// Map frontend category to backend storage type
function mapCategoryToStorageType(
  category: FoodStorageCategory
): 'fridge' | 'freezer' | 'pantry' {
  switch (category) {
    case 'fridge':
      return 'fridge'
    case 'freezer':
      return 'freezer'
    case 'pantry':
      return 'pantry'
    default:
      return 'fridge'
  }
}

export interface StorageCreateRequest {
  storage_name: string
  storage_type: 'fridge' | 'freezer' | 'pantry'
  group_id: string
}

export interface StorageResponse {
  storage_id: number
  storage_name: string
  storage_type: string
  group_id: string
  storage_unit_list: unknown[]
}

export interface StorageListItem {
  storage_id: number
  storage_name: string
  storage_type: 'fridge' | 'freezer' | 'pantry'
  group_id: string
  storage_unit_list?: unknown[]
  item_count?: number
}

export interface StorableUnit {
  unit_id: number
  unit_name: string
  storage_id: number
  package_quantity: number
  component_id: number | null
  content_type: string | null
  content_quantity: number | null
  content_unit: 'G' | 'ML' | null
  added_date: string
  expiration_date: string | null
}

export interface StorableUnitsResponse {
  data: StorableUnit[]
  next_cursor: number | null
  size: number
}

export class StorageService {
  constructor(private clients: Clients) {}

  /**
   * Create a new storage
   */
  public createStorage(
    name: string,
    category: FoodStorageCategory,
    groupId: string
  ): ResultAsync<StorageResponse, StorageError> {
    const url = `/v1/storages/`
    const body: StorageCreateRequest = {
      storage_name: name,
      storage_type: mapCategoryToStorageType(category),
      group_id: groupId
    }

    return httpPost(this.clients.shopping, url, body)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createStorageError('not-found', e.desc)
          case 'unauthorized':
            return createStorageError('unauthorized', e.desc)
          default:
            return createStorageError('network-error', e.desc)
        }
      })
      .map((response) => response.body as StorageResponse)
  }

  /**
   * Filter storages by group_id and optionally storage_type
   */
  public filterStorages(
    groupId: string,
    storageType?: 'fridge' | 'freezer' | 'pantry'
  ): ResultAsync<StorageListItem[], StorageError> {
    const queryParams = new URLSearchParams()
    queryParams.append('group_id', groupId)
    if (storageType) {
      queryParams.append('storage_type', storageType)
    }
    const url = `/v1/storages/filter?${queryParams.toString()}`

    return httpGet(this.clients.shopping, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createStorageError('not-found', e.desc)
          case 'unauthorized':
            return createStorageError('unauthorized', e.desc)
          default:
            return createStorageError('network-error', e.desc)
        }
      })
      .map((response) => {
        // Handle different response structures
        const body = response.body as any
        if (Array.isArray(body)) {
          return body as StorageListItem[]
        }
        if (body?.data && Array.isArray(body.data)) {
          return body.data as StorageListItem[]
        }
        if (body?.results && Array.isArray(body.results)) {
          return body.results as StorageListItem[]
        }
        return []
      })
  }

  /**
   * Get list of storages for a group (deprecated - use filterStorages instead)
   * @deprecated Use filterStorages instead
   */
  public getStorages(
    groupId: string
  ): ResultAsync<StorageListItem[], StorageError> {
    return this.filterStorages(groupId)
  }

  /**
   * Delete a storage by ID
   */
  public deleteStorage(
    storageId: number
  ): ResultAsync<void, StorageError> {
    const url = `/v1/storages/${storageId}`

    return httpDelete(this.clients.shopping, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createStorageError('not-found', e.desc)
          case 'unauthorized':
            return createStorageError('unauthorized', e.desc)
          default:
            return createStorageError('network-error', e.desc)
        }
      })
      .map(() => undefined)
  }

  /**
   * Get storage items (units) for a storage
   */
  public getStorageItems(
    storageId: number,
    cursor?: number,
    limit: number = 100
  ): ResultAsync<StorableUnitsResponse, StorageError> {
    const queryParams = new URLSearchParams()
    queryParams.append('storage_id', String(storageId))
    if (cursor !== undefined) {
      queryParams.append('cursor', String(cursor))
    }
    queryParams.append('limit', String(limit))
    const url = `/v1/storable_units/filter?${queryParams.toString()}`

    return httpGet(this.clients.shopping, url)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createStorageError('not-found', e.desc)
          case 'unauthorized':
            return createStorageError('unauthorized', e.desc)
          default:
            return createStorageError('network-error', e.desc)
        }
      })
      .map((response) => {
        const body = response.body as any
        return {
          data: body.data || body.results || [],
          next_cursor: body.next_cursor || null,
          size: body.size || 0
        } as StorableUnitsResponse
      })
  }

  /**
   * Create a new storage item (storable unit)
   */
  public createStorageItem(data: {
    unit_name: string
    storage_id: number
    package_quantity: number
    component_id?: number | null
    content_type?: string | null
    content_quantity?: number | null
    content_unit?: 'G' | 'ML' | null
    expiration_date?: string | null
  }): ResultAsync<StorableUnit, StorageError> {
    const url = `/v1/storable_units/`

    const body: any = {
      unit_name: data.unit_name,
      storage_id: data.storage_id,
      package_quantity: data.package_quantity
    }

    if (data.component_id !== undefined && data.component_id !== null) {
      body.component_id = data.component_id
    }
    if (data.content_type) {
      body.content_type = data.content_type
    }
    if (data.content_quantity !== undefined && data.content_quantity !== null) {
      body.content_quantity = data.content_quantity
    }
    if (data.content_unit) {
      body.content_unit = data.content_unit
    }
    if (data.expiration_date) {
      body.expiration_date = data.expiration_date
    }

    return httpPost(this.clients.shopping, url, body)
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createStorageError('not-found', e.desc)
          case 'unauthorized':
            return createStorageError('unauthorized', e.desc)
          default:
            return createStorageError('network-error', e.desc)
        }
      })
      .map((response) => response.body as StorableUnit)
  }

  /**
   * Consume a storable unit by ID
   */
  public consumeStorableUnit(
    unitId: number,
    consumeQuantity: number = 1
  ): ResultAsync<{ message: string; data: any }, StorageError> {
    const url = `/v1/storable_units/${unitId}/consume?consume_quantity=${consumeQuantity}`

    return httpPost(this.clients.shopping, url, {})
      .mapErr((e) => {
        switch (e.type) {
          case 'path-not-found':
            return createStorageError('not-found', e.desc)
          case 'unauthorized':
            return createStorageError('unauthorized', e.desc)
          default:
            return createStorageError('network-error', e.desc)
        }
      })
      .map((response) => response.body as { message: string; data: any })
  }
}

export const storageService = new StorageService(httpClients)

