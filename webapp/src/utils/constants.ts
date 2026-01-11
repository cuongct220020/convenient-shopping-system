import { i18nKeys } from './i18n/keys'

export const MealTypes = [
  'breakfast',
  'lunch',
  'dinner',
  'late-night',
  'snack'
] as const

export type MealType = (typeof MealTypes)[number]

export function mealTypeStr(e: MealType): i18nKeys {
  switch (e) {
    case 'breakfast':
      return 'meal_breakfast'
    case 'dinner':
      return 'meal_dinner'
    case 'late-night':
      return 'meal_late_night'
    case 'lunch':
      return 'meal_lunch'
    case 'snack':
      return 'meal_snack'
  }
}

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

// Ingredient measurement units
export const COUNTABLE_UNITS = [
  'quả',
  'củ',
  'gói',
  'bó',
  'miếng',
  'nhánh',
  'tép',
  'con',
  'viên',
  'túi',
  'cây',
  'lát',
  'khúc',
  'lá',
  'hộp',
  'cái'
] as const

export type CountableUnit = (typeof COUNTABLE_UNITS)[number]

export const UNCOUNTABLE_UNITS = ['G', 'ML'] as const

export type UncountableUnit = (typeof UNCOUNTABLE_UNITS)[number]

// Ingredient categories
export const INGREDIENT_CATEGORIES = [
  'Đồ uống có cồn',
  'Đồ uống',
  'Bánh ngọt',
  'Kẹo',
  'Ngũ cốc và hạt',
  'Thịt nguội, xúc xích và giăm bông',
  'Trái cây sấy khô',
  'Trái cây tươi',
  'Thịt tươi',
  'Mứt trái cây',
  'Lương thực',
  'Kem và phô mai',
  'Thực phẩm ăn liền',
  'Sữa',
  'Khác',
  'Hải sản và cá viên',
  'Gia vị',
  'Đồ ăn vặt',
  'Rau củ',
  'Sữa chua'
] as const

export type IngredientCategory = (typeof INGREDIENT_CATEGORIES)[number]

export const Constant = {
  keys: {
    localStorage: 'ShopSense',
    sessionStorage: 'ShopSense'
  },
  otpRequestInterval: 60 /* seconds */
} as const
