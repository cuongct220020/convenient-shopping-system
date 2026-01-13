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
  'fridge',
  'freezer',
  'pantry'
] as const

export type FoodStorageCategory = (typeof FoodStorageCategories)[number]

export function foodStorageCategoryStr(e: FoodStorageCategory): i18nKeys {
  switch (e) {
    case 'fridge':
      return 'storage_fridge'
    case 'freezer':
      return 'storage_freezer'
    case 'pantry':
      return 'storage_pantry'
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

// Ingredient tags mapping
export const INGREDIENT_TAGS_MAP: Record<number, string> = {
  // Age (0100-0104)
  100: 'Trẻ em',
  101: 'Vị thành niên',
  102: 'Người trưởng thành',
  103: 'Trung niên',
  104: 'Cao tuổi',
  // Disease (0200-0272)
  200: 'Bệnh tim mạch',
  201: 'Huyết áp cao',
  202: 'Huyết áp thấp',
  203: 'Rối loạn đông máu',
  210: 'Bệnh chuyển hóa',
  211: 'Béo phì',
  212: 'Tiểu đường',
  213: 'Gout',
  220: 'Gan nhiễm mỡ',
  221: 'Suy gan',
  222: 'Xơ gan',
  223: 'Sỏi mật',
  230: 'Suy thận',
  231: 'Sỏi thận',
  240: 'Loãng xương',
  241: 'Còi xương',
  242: 'Viêm khớp',
  250: 'Viêm loét dạ dày',
  251: 'Trào ngược dạ dày',
  252: 'Tiêu chảy',
  253: 'Táo bón',
  254: 'Sâu răng',
  260: 'Suy dinh dưỡng',
  261: 'Thiếu máu',
  262: 'Mắt kém',
  263: 'Rụng tóc',
  270: 'Viêm mạn tính',
  271: 'Miễn dịch yếu',
  272: 'Bệnh da liễu',
  // Allergy (0300-0308)
  300: 'Hải sản có vỏ',
  301: 'Cá',
  302: 'Sữa',
  303: 'Trứng',
  304: 'Đậu phộng',
  305: 'Đậu nành',
  306: 'Mè',
  307: 'Các loại hạt',
  308: 'Lúa mì',
  // Special diet (0400-0402)
  400: 'Gymer',
  401: 'Dieter',
  402: 'Vegan',
  403: 'Vegetarian',
  // Taste preference (0500-0507)
  500: 'Thích mặn',
  501: 'Thích ngọt',
  502: 'Thích umami',
  503: 'Thích chua',
  504: 'Thích đắng',
  505: 'Thích cay',
  506: 'Thích thanh đạm',
  507: 'Thích béo',
  // Ingredient nutrients (1100-1135)
  1100: 'Chất béo cao',
  1101: 'Cholesterol cao',
  1102: 'Chất xơ cao',
  1103: 'Protein cao',
  1104: 'Đường cao',
  1105: 'Carb cao',
  1106: 'Calo cao',
  1107: 'Omega 3 cao',
  1108: 'Omega 6 cao',
  1109: 'Omega 9 cao',
  1110: 'Natri cao',
  1111: 'Kali cao',
  1112: 'Phospho cao',
  1113: 'Canxi cao',
  1114: 'Magie cao',
  1115: 'Sắt cao',
  1116: 'Kẽm cao',
  1120: 'Vitamin A cao',
  1121: 'Vitamin C cao',
  1122: 'Vitamin D cao',
  1123: 'Vitamin K cao',
  1124: 'Vitamin B7 cao',
  1125: 'Vitamin B9 cao',
  1126: 'Vitamin B12 cao',
  1130: 'Độ axit cao',
  1131: 'Độ kiềm cao',
  1132: 'Capsaicin cao',
  1133: 'Cồn cao',
  1134: 'Caffeine cao',
  1135: 'Oxalate cao',
  // Flavor (1200-1207)
  1200: 'Mặn',
  1201: 'Ngọt',
  1202: 'Umami',
  1203: 'Chua',
  1204: 'Đắng',
  1205: 'Cay',
  1206: 'Thanh đạm',
  1207: 'Béo',
  // Diet type (1300-1301)
  1300: 'Vegan',
  1301: 'Vegetarian'
} as const

export const Constant = {
  keys: {
    localStorage: 'ShopSense',
    sessionStorage: 'ShopSense'
  },
  otpRequestInterval: 60 /* seconds */
} as const
