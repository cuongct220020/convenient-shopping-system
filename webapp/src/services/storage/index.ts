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
  | 'validation-error'
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
  storable_units: unknown[]
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
    const url = `${AppUrl.SHOPPING_BASE}/v1/storages`
    const body: StorageCreateRequest = {
      storage_name: name,
      storage_type: mapCategoryToStorageType(category),
      group_id: groupId
    }

    return httpPost(this.clients.auth, url, body)
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
}

export const storageService = new StorageService(httpClients)

