import { i18nKeys } from './i18n/keys'

export const FoodStorageCategories = [
  'freezer',
  'non-freezer',
  'bulk',
  'fridge'
] as const

export type FoodStorageCategory = (typeof FoodStorageCategories)[number]

export function foodStorageCategoryStr(e: FoodStorageCategory): i18nKeys {
  switch (e) {
    case 'bulk':
      return 'storage_bulk'
    case 'freezer':
      return 'storage_freezer'
    case 'non-freezer':
      return 'storage_nonfreezer'
    case 'fridge':
      return 'storage_fridge'
    default:
      throw new Error('Unimplemented')
  }
}

export const Constant = {
  keys: {
    localStorage: 'ShopSense',
    sessionStorage: 'ShopSense'
  },
  otpRequestInterval: 60 /* seconds */
} as const
