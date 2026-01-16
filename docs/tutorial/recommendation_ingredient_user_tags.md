# Cơ Chế Tính Điểm Recommender

## Tổng Quan

Hệ thống recommender tính điểm cho các công thức (recipes) dựa trên hai yếu tố chính:
1. **Điểm dựa trên nguyên liệu có sẵn** (Exist Points)
2. **Điểm dựa trên tag preferences** (Tag Points)

Điểm tổng được tính bằng công thức:
```
total_point = tanh(exist_points) + tanh(tag_points)
```

Hệ thống trả về **top 5 recipes** có điểm cao nhất cho mỗi group.

---

## 1. Điểm Dựa Trên Nguyên Liệu Có Sẵn (Exist Points)

### Cách Tính
- Đếm số lượng nguyên liệu của recipe **có sẵn** trong kho của group
- Mỗi nguyên liệu khớp = **+1 điểm**
- Công thức: `exist_points = len(ingredient_name_set & component_name_set)`

### Dữ Liệu Đầu Vào
- **Recipe ingredients**: Danh sách tên nguyên liệu từ `RecipesFlattened.all_ingredients`
  + Do Recipe được thiết kế theo Composite Pattern khiến mỗi object có dạng 1 cây với lá là Ingredient khiến công đoạn flatten mỗi object làm tăng độ phức tạp thuật toán, kĩ thuật Denormalization đã được áp dụng để tạo bảng RecipesFlattened lưu sẵn danh sách nguyên liệu đã flatten, chấp nhận đánh đổi hiệu suất write (vốn là thao tác thuộc quyền admin không được sử dụng thường xuyên) để đổi lấy khả năng read vượt trội.
- **Group inventory**: Danh sách tên nguyên liệu từ `ComponentExistence.component_name_list` của group
  + ComponentExistence được truyền đến recipe-service qua Kafka MesssageQueue từ shopping-storage-service mỗi khi thêm mới hoặc xóa 1 loại nguyên liệu trong group

### Ví Dụ
- Recipe có 5 nguyên liệu: `["thịt gà", "hành tây", "tỏi", "nước mắm", "đường"]`
- Group có sẵn: `["thịt gà", "hành tây", "tỏi"]`
- **Exist Points = 3**

---

## 2. Điểm Dựa Trên Tag Preferences (Tag Points)

### Cách Tính
Hệ thống sử dụng bảng `TagRelation` để map giữa **user tags** (sở thích/sức khỏe của người dùng) và **ingredient tags** (đặc tính dinh dưỡng/vị của nguyên liệu).

#### Positive Relations (Quan hệ tích cực)
- Mỗi ingredient tag khớp với user tag qua positive relation = **+1 điểm**
- Ví dụ: User tag `diabetes` có positive relation với ingredient tag `high_fiber` → recipe có nguyên liệu `high_fiber` sẽ được +1 điểm

#### Negative Relations (Quan hệ tiêu cực)
- Mỗi ingredient tag khớp với user tag qua negative relation = **-10 điểm**
- Ví dụ: User tag `diabetes` có negative relation với ingredient tag `high_sugar` → recipe có nguyên liệu `high_sugar` sẽ bị -10 điểm

### Công Thức Tính Tag Points
```python
total_points = 0

for user_tag in group_tag_set:
    if user_tag in positive_relations:
        matches = recipe_bitmap & positive_relations[user_tag]
        total_points += bin(matches).count('1')  # +1 cho mỗi match
    
    if user_tag in negative_relations:
        mismatches = recipe_bitmap & negative_relations[user_tag]
        total_points -= 10 * bin(mismatches).count('1')  # -10 cho mỗi mismatch

return total_points
```

### Tối Ưu Hóa Bằng Bitmap
- Hệ thống sử dụng **bitmap** để tối ưu hiệu suất tính toán
- Mỗi tag được chuyển thành bit index: `idx = int(tag[1:])` (ví dụ: tag `1100` → index 100)
- Bitmap cho phép so sánh nhanh nhiều tags cùng lúc bằng phép toán bitwise AND

### Dữ Liệu Đầu Vào
- **Recipe tags**: Tập hợp tất cả `ingredient_tag_list` từ các nguyên liệu trong recipe
- **Group tags**: Tập hợp tất cả `user_tag_list` từ `GroupPreference` của các thành viên trong group
  + GroupPreference được truyền đến recipe-service qua Kafka MessageQueue từ user-service mỗi khi thành viên trong group cập nhật sở thích/sức khỏe

### Ví Dụ
- Group có user tags: `["diabetes", "obesity"]`
- Recipe có ingredient tags: `["high_fiber", "high_protein", "high_sugar"]`
- TagRelation:
  - `diabetes` → `high_fiber`: positive (+1)
  - `diabetes` → `high_sugar`: negative (-10)
  - `obesity` → `high_protein`: positive (+1)
- **Tag Points = 1 + 1 - 10 = -8**

---

## 3. Tính Điểm Tổng và Chọn Top K

### Normalization với Tanh
Cả hai loại điểm đều được normalize bằng hàm `tanh()` để:
- Giới hạn giá trị trong khoảng (-1, 1)
- Tránh một loại điểm chiếm ưu thế quá mức
- Tạo sự cân bằng giữa exist points và tag points

### Công Thức Tổng
```python
total_point = tanh(exist_points) + tanh(tag_points)
```

### Top K Selection
- Sử dụng **min-heap** để tối ưu việc duy trì top 5 recipes có điểm cao nhất
- Khi heap đầy (5 items), chỉ thay thế item có điểm thấp nhất nếu điểm mới cao hơn

### Ví Dụ Tính Điểm Tổng
- Recipe A: exist_points = 3, tag_points = 5
  - `total = tanh(3) + tanh(5) ≈ 0.995 + 0.9999 ≈ 1.995`
- Recipe B: exist_points = 2, tag_points = -8
  - `total = tanh(2) + tanh(-8) ≈ 0.964 - 0.9999 ≈ -0.036`

---

## 4. Caching

Do thuật toán tính điểm recommend phức tạp, Recommender được tích hợp hệ thống cache kết quả trong Redis:
- **Cache key**: `recipe:recommendations:{group_id}`
- **TTL**: mặc định 8 giờ (28800 giây)
- Giúp giảm tải database và tăng tốc độ phản hồi

---

## 5. Cấu Trúc Dữ Liệu

### TagRelation
Bảng mapping giữa user tags và ingredient tags:
- `user_tag`: User tag ID (ví dụ: `0212` cho `diabetes`)
- `ingredient_tag`: Ingredient tag ID (ví dụ: `1104` cho `high_sugar`)
- `relation`: `True` = positive, `False` = negative

### GroupPreference
Lưu user tags của từng thành viên trong group:
- `user_id`: ID của user
- `group_id`: ID của group
- `user_tag_list`: Danh sách user tags (ví dụ: `["0212", "0211"]`)

### ComponentExistence
Lưu danh sách nguyên liệu có sẵn trong kho của group:
- `group_id`: ID của group
- `component_name_list`: Danh sách tên nguyên liệu (ví dụ: `["thịt gà", "hành tây"]`)

---

## 6. Ví Dụ Tổng Hợp

### Input
- **Group ID**: `abc-123`
- **Group preferences**: 
  - User 1: `["0212", "0211"]` (diabetes, obesity)
  - User 2: `["0400"]` (gymer)
- **Inventory**: `["thịt gà", "trứng", "rau xanh"]`
- **TagRelations**:
  - `diabetes` → `high_fiber`: positive
  - `diabetes` → `high_sugar`: negative
  - `obesity` → `high_protein`: positive
  - `gymer` → `high_protein`: positive

### Recipe A: "Gà luộc rau"
- Ingredients: `["thịt gà", "rau xanh"]` → có 2/2 trong kho
- Ingredient tags: `["high_protein", "high_fiber"]`
- **Exist Points**: 2
- **Tag Points**: 
  - `high_protein` khớp với `obesity` (+1) và `gymer` (+1) = +2
  - `high_fiber` khớp với `diabetes` (+1) = +1
  - Tổng: +3
- **Total**: `tanh(2) + tanh(3) ≈ 0.964 + 0.995 ≈ 1.959`

### Recipe B: "Bánh ngọt"
- Ingredients: `["trứng", "đường", "bột mì"]` → có 1/3 trong kho
- Ingredient tags: `["high_sugar", "high_carb"]`
- **Exist Points**: 1
- **Tag Points**:
  - `high_sugar` khớp với `diabetes` (-10) = -10
  - Tổng: -10
- **Total**: `tanh(1) + tanh(-10) ≈ 0.762 - 0.9999 ≈ -0.238`

### Kết Quả
Recipe A sẽ được recommend (điểm cao hơn), Recipe B sẽ không được recommend.

---

## 8. Danh sách các loại tag
### Ingredient Tags
- 1100: high_fat 
- 1101: high_cholesterol
- 1102: high_fiber
- 1103: high_protein
- 1104: high_sugar
- 1105: high_carb
- 1106: high_calorie
- 1107: high_omega3
- 1108: high_omega6
- 1109: high_omega9
- 1110: high_sodium
- 1111: high_potassium
- 1112: high_phosphorus
- 1113: high_calcium
- 1114: high_magnesium
- 1115: high_iron
- 1116: high_zinc
- 1120: high_vitaminA
- 1121: high_vitaminC
- 1122: high_vitaminD
- 1123: high_vitaminK
- 1124: high_vitaminB7
- 1125: high_vitaminB9
- 1126: high_vitaminB12
- 1130: high_acidity
- 1131: high_alkaline
- 1132: high_capsaicin
- 1133: high_alcohol
- 1134: high_caffeine
- 1135: high_oxalate
- 1200: salty
- 1201: sweet
- 1202: umami
- 1203: sour
- 1204: bitter
- 1205: spicy
- 1206: light
- 1207: rich
- 1300: vegan
- 1301: vegetarian

### User Tags
- 0100: children
- 0101: teenager
- 0102: adult
- 0103: middle_aged
- 0104: elder
- 0200: cardiovascular_disease
- 0201: high_blood_pressure
- 0202: low_blood_pressure
- 0203: blood_clotting_disorder
- 0210: metabolic_disease
- 0211: obesity
- 0212: diabetes
- 0213: gout
- 0220: fatty_liver
- 0221: liver_failure
- 0222: cirrhosis
- 0223: gallstones
- 0230: kidney_failure
- 0231: kidney_stones
- 0240: osteoporosis
- 0241: rickets
- 0242: arthritis
- 0250: gastric_ulcer
- 0251: acid_reflux
- 0252: diarrhea
- 0253: constipation
- 0254: tooth_decay
- 0260: malnutrition
- 0261: anemia
- 0262: poor_eyesight
- 0263: hair_loss
- 0270: inflammation
- 0271: weak_immunity
- 0272: dermatological_disease
- 0300: shellfish
- 0301: fish
- 0302: dairy
- 0303: egg
- 0304: peanut
- 0305: soy
- 0306: sesame
- 0307: nuts
- 0308: wheat
- 0400: gymer
- 0401: dieter
- 0402: vegan
- 0403: vegetarian
- 0500: salty_pref
- 0501: sweet_pref
- 0502: umami_pref
- 0503: sour_pref
- 0504: bitter_pref
- 0505: spicy_pref
- 0506: light_pref
- 0507: rich_pref