# microservices/user-service/app/constants/tags.py
from enum import Enum


class AgeTag(str, Enum):
    """Tags for age groups."""
    CHILDREN = "0100"  # Trẻ em
    TEENAGER = "0101"  # Vị thành niên
    ADULT = "0102"  # Người trưởng thành
    MIDDLE_AGED = "0103"  # Trung niên
    ELDER = "0104"  # Cao tuổi


class MedicalConditionTag(str, Enum):
    """Tags for medical conditions."""

    # Cardiovascular - Bệnh tim mạch
    CARDIOVASCULAR_DISEASE = "0200"  # Bệnh tim mạch
    HIGH_BLOOD_PRESSURE = "0201"  # Huyết áp cao
    LOW_BLOOD_PRESSURE = "0202"  # Huyết áp thấp
    BLOOD_CLOTTING_DISORDER = "0203"  # Rối loạn đông máu

    # Metabolic - Bệnh chuyển hóa
    METABOLIC_DISEASE = "0210"  # Bệnh chuyển hóa
    OBESITY = "0211"  # Béo phì
    DIABETES = "0212"  # Tiểu đường
    GOUT = "0213"  # Gout

    # Liver & Gallbladder - Gan & Túi mật
    FATTY_LIVER = "0220"  # Gan nhiễm mỡ
    LIVER_FAILURE = "0221"  # Suy gan
    CIRRHOSIS = "0222"  # Xơ gan
    GALLSTONES = "0223"  # Sỏi mật

    # Kidney - Thận
    KIDNEY_FAILURE = "0230"  # Suy thận
    KIDNEY_STONES = "0231"  # Sỏi thận

    # Bone & Joint - Xương & Khớp
    OSTEOPOROSIS = "0240"  # Loãng xương
    RICKETS = "0241"  # Còi xương
    ARTHRITIS = "0242"  # Viêm khớp

    # Digestive - Tiêu hóa
    GASTRIC_ULCER = "0250"  # Viêm loét dạ dày
    ACID_REFLUX = "0251"  # Trào ngược dạ dày
    DIARRHEA = "0252"  # Tiêu chảy
    CONSTIPATION = "0253"  # Táo bón
    TOOTH_DECAY = "0254"  # Sâu răng

    # Nutritional - Dinh dưỡng
    MALNUTRITION = "0260"  # Suy dinh dưỡng
    ANEMIA = "0261"  # Thiếu máu
    POOR_EYESIGHT = "0262"  # Mắt kém
    HAIR_LOSS = "0263"  # Rụng tóc

    # Other - Khác
    INFLAMMATION = "0270"  # Viêm mạn tính
    WEAK_IMMUNITY = "0271"  # Miễn dịch yếu
    DERMATOLOGICAL_DISEASE = "0272"  # Bệnh da liễu


class AllergyTag(str, Enum):
    """Tags for food allergies."""
    SHELLFISH = "0300"  # Hải sản có vỏ
    FISH = "0301"  # Cá
    DAIRY = "0302"  # Sữa
    EGG = "0303"  # Trứng
    PEANUT = "0304"  # Đậu phộng
    SOY = "0305"  # Đậu nành
    SESAME = "0306"  # Mè
    NUTS = "0307"  # Các loại hạt
    WHEAT = "0308"  # Lúa mì


class SpecialDietTag(str, Enum):
    """Tags for special dietary preferences."""
    GYMER = "0400"  # Người tập gym
    DIETER = "0401"  # Người ăn kiêng
    VEGAN = "0402"  # Người ăn chay trường (thuần chay)
    VEGETARIAN = "0403"  # Người ăn chay (có thể dùng sữa, trứng)


class TastePreferenceTag(str, Enum):
    """Tags for taste preferences."""
    SALTY_PREF = "0500"  # Thích mặn
    SWEET_PREF = "0501"  # Thích ngọt
    UMAMI_PREF = "0502"  # Thích umami
    SOUR_PREF = "0503"  # Thích chua
    BITTER_PREF = "0504"  # Thích đắng
    SPICY_PREF = "0505"  # Thích cay
    LIGHT_PREF = "0506"  # Thích thanh đạm
    RICH_PREF = "0507"  # Thích béo
