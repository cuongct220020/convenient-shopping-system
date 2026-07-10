// Tag types and constants based on backend user-service/app/enums/tags.py

export type TagCategory = 'age' | 'medical' | 'allergy' | 'diet' | 'taste';

export type TagValue =
  // Age tags
  | '0100' | '0101' | '0102' | '0103' | '0104'
  // Medical condition tags
  | '0200' | '0201' | '0202' | '0203'
  | '0210' | '0211' | '0212' | '0213'
  | '0220' | '0221' | '0222' | '0223'
  | '0230' | '0231'
  | '0240' | '0241' | '0242'
  | '0250' | '0251' | '0252' | '0253' | '0254'
  | '0260' | '0261' | '0262' | '0263'
  | '0270' | '0271' | '0272'
  // Allergy tags
  | '0300' | '0301' | '0302' | '0303' | '0304' | '0305' | '0306' | '0307' | '0308'
  // Diet tags
  | '0400' | '0401' | '0402' | '0403'
  // Taste preference tags
  | '0500' | '0501' | '0502' | '0503' | '0504' | '0505' | '0506' | '0507';

export interface UserTag {
  id: number;
  tag_value: TagValue;
  tag_category: TagCategory;
  tag_name: string;
  description: string;
  updated_at: string;
}

export interface UserTagsData {
  age: UserTag[];
  medical: UserTag[];
  allergy: UserTag[];
  diet: UserTag[];
  taste: UserTag[];
}

export interface UserTagsResponse {
  data: UserTagsData;
  total_tags: number;
  categories_count: {
    age: number;
    medical: number;
    allergy: number;
    diet: number;
    taste: number;
  };
}

// Age tags
export const AGE_TAGS = {
  CHILDREN: { value: '0100' as TagValue, name: 'Trẻ em', nameEn: 'CHILDREN' },
  TEENAGER: { value: '0101' as TagValue, name: 'Vị thành niên', nameEn: 'TEENAGER' },
  ADULT: { value: '0102' as TagValue, name: 'Người trưởng thành', nameEn: 'ADULT' },
  MIDDLE_AGED: { value: '0103' as TagValue, name: 'Trung niên', nameEn: 'MIDDLE_AGED' },
  ELDER: { value: '0104' as TagValue, name: 'Cao tuổi', nameEn: 'ELDER' },
} as const;

// Medical condition tags
export const MEDICAL_TAGS = {
  // Cardiovascular
  CARDIOVASCULAR_DISEASE: { value: '0200' as TagValue, name: 'Bệnh tim mạch', nameEn: 'CARDIOVASCULAR_DISEASE' },
  HIGH_BLOOD_PRESSURE: { value: '0201' as TagValue, name: 'Huyết áp cao', nameEn: 'HIGH_BLOOD_PRESSURE' },
  LOW_BLOOD_PRESSURE: { value: '0202' as TagValue, name: 'Huyết áp thấp', nameEn: 'LOW_BLOOD_PRESSURE' },
  BLOOD_CLOTTING_DISORDER: { value: '0203' as TagValue, name: 'Rối loạn đông máu', nameEn: 'BLOOD_CLOTTING_DISORDER' },
  // Metabolic
  METABOLIC_DISEASE: { value: '0210' as TagValue, name: 'Bệnh chuyển hóa', nameEn: 'METABOLIC_DISEASE' },
  OBESITY: { value: '0211' as TagValue, name: 'Béo phì', nameEn: 'OBESITY' },
  DIABETES: { value: '0212' as TagValue, name: 'Tiểu đường', nameEn: 'DIABETES' },
  GOUT: { value: '0213' as TagValue, name: 'Gout', nameEn: 'GOUT' },
  // Liver & Gallbladder
  FATTY_LIVER: { value: '0220' as TagValue, name: 'Gan nhiễm mỡ', nameEn: 'FATTY_LIVER' },
  LIVER_FAILURE: { value: '0221' as TagValue, name: 'Suy gan', nameEn: 'LIVER_FAILURE' },
  CIRRHOSIS: { value: '0222' as TagValue, name: 'Xơ gan', nameEn: 'CIRRHOSIS' },
  GALLSTONES: { value: '0223' as TagValue, name: 'Sỏi mật', nameEn: 'GALLSTONES' },
  // Kidney
  KIDNEY_FAILURE: { value: '0230' as TagValue, name: 'Suy thận', nameEn: 'KIDNEY_FAILURE' },
  KIDNEY_STONES: { value: '0231' as TagValue, name: 'Sỏi thận', nameEn: 'KIDNEY_STONES' },
  // Bone & Joint
  OSTEOPOROSIS: { value: '0240' as TagValue, name: 'Loãng xương', nameEn: 'OSTEOPOROSIS' },
  RICKETS: { value: '0241' as TagValue, name: 'Còi xương', nameEn: 'RICKETS' },
  ARTHRITIS: { value: '0242' as TagValue, name: 'Viêm khớp', nameEn: 'ARTHRITIS' },
  // Digestive
  GASTRIC_ULCER: { value: '0250' as TagValue, name: 'Viêm loét dạ dày', nameEn: 'GASTRIC_ULCER' },
  ACID_REFLUX: { value: '0251' as TagValue, name: 'Trào ngược dạ dày', nameEn: 'ACID_REFLUX' },
  DIARRHEA: { value: '0252' as TagValue, name: 'Tiêu chảy', nameEn: 'DIARRHEA' },
  CONSTIPATION: { value: '0253' as TagValue, name: 'Táo bón', nameEn: 'CONSTIPATION' },
  TOOTH_DECAY: { value: '0254' as TagValue, name: 'Sâu răng', nameEn: 'TOOTH_DECAY' },
  // Nutritional
  MALNUTRITION: { value: '0260' as TagValue, name: 'Suy dinh dưỡng', nameEn: 'MALNUTRITION' },
  ANEMIA: { value: '0261' as TagValue, name: 'Thiếu máu', nameEn: 'ANEMIA' },
  POOR_EYESIGHT: { value: '0262' as TagValue, name: 'Mắt kém', nameEn: 'POOR_EYESIGHT' },
  HAIR_LOSS: { value: '0263' as TagValue, name: 'Rụng tóc', nameEn: 'HAIR_LOSS' },
  // Other
  INFLAMMATION: { value: '0270' as TagValue, name: 'Viêm mạn tính', nameEn: 'INFLAMMATION' },
  WEAK_IMMUNITY: { value: '0271' as TagValue, name: 'Miễn dịch yếu', nameEn: 'WEAK_IMMUNITY' },
  DERMATOLOGICAL_DISEASE: { value: '0272' as TagValue, name: 'Bệnh da liễu', nameEn: 'DERMATOLOGICAL_DISEASE' },
} as const;

// Allergy tags
export const ALLERGY_TAGS = {
  SHELLFISH: { value: '0300' as TagValue, name: 'Hải sản có vỏ', nameEn: 'SHELLFISH' },
  FISH: { value: '0301' as TagValue, name: 'Cá', nameEn: 'FISH' },
  DAIRY: { value: '0302' as TagValue, name: 'Sữa', nameEn: 'DAIRY' },
  EGG: { value: '0303' as TagValue, name: 'Trứng', nameEn: 'EGG' },
  PEANUT: { value: '0304' as TagValue, name: 'Đậu phộng', nameEn: 'PEANUT' },
  SOY: { value: '0305' as TagValue, name: 'Đậu nành', nameEn: 'SOY' },
  SESAME: { value: '0306' as TagValue, name: 'Mè', nameEn: 'SESAME' },
  NUTS: { value: '0307' as TagValue, name: 'Các loại hạt', nameEn: 'NUTS' },
  WHEAT: { value: '0308' as TagValue, name: 'Lúa mì', nameEn: 'WHEAT' },
} as const;

// Diet tags
export const DIET_TAGS = {
  GYMER: { value: '0400' as TagValue, name: 'Người tập gym', nameEn: 'GYMER' },
  DIETER: { value: '0401' as TagValue, name: 'Người ăn kiêng', nameEn: 'DIETER' },
  VEGAN: { value: '0402' as TagValue, name: 'Người ăn chay trường', nameEn: 'VEGAN' },
  VEGETARIAN: { value: '0403' as TagValue, name: 'Người ăn chay', nameEn: 'VEGETARIAN' },
} as const;

// Taste preference tags
export const TASTE_TAGS = {
  SALTY_PREF: { value: '0500' as TagValue, name: 'Thích mặn', nameEn: 'SALTY_PREF' },
  SWEET_PREF: { value: '0501' as TagValue, name: 'Thích ngọt', nameEn: 'SWEET_PREF' },
  UMAMI_PREF: { value: '0502' as TagValue, name: 'Thích umami', nameEn: 'UMAMI_PREF' },
  SOUR_PREF: { value: '0503' as TagValue, name: 'Thích chua', nameEn: 'SOUR_PREF' },
  BITTER_PREF: { value: '0504' as TagValue, name: 'Thích đắng', nameEn: 'BITTER_PREF' },
  SPICY_PREF: { value: '0505' as TagValue, name: 'Thích cay', nameEn: 'SPICY_PREF' },
  LIGHT_PREF: { value: '0506' as TagValue, name: 'Thích thanh đạm', nameEn: 'LIGHT_PREF' },
  RICH_PREF: { value: '0507' as TagValue, name: 'Thích béo', nameEn: 'RICH_PREF' },
} as const;

// Tag category display names
export const TAG_CATEGORY_NAMES: Record<TagCategory, string> = {
  age: 'Độ tuổi',
  medical: 'Bệnh lý',
  allergy: 'Dị ứng',
  diet: 'Chế độ ăn',
  taste: 'Khẩu vị',
};

// Get tag by value
export function getTagByValue(value: TagValue) {
  const allTags = {
    ...AGE_TAGS,
    ...MEDICAL_TAGS,
    ...ALLERGY_TAGS,
    ...DIET_TAGS,
    ...TASTE_TAGS,
  };

  for (const tag of Object.values(allTags)) {
    if (tag.value === value) {
      return tag;
    }
  }
  return null;
}
