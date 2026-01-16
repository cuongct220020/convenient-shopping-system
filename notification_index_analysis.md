# Đánh giá Index cho bảng Notification

## Index hiện có

1. **id** (Primary Key) - ✅ Tự động có index
2. **group_id** - ✅ Đã có index (`index=True`)
3. **receiver** - ✅ Đã có index (`index=True`)
4. **is_read** - ✅ Đã có index (`index=True`)

## Query Patterns phân tích

### 1. `get_by_receiver` (Query chính)
```sql
SELECT * FROM notifications 
WHERE receiver = ? 
ORDER BY created_at DESC
```
- **Filter**: `receiver` (đã có index) ✅
- **Sort**: `created_at DESC`
- **Phân tích**: 
  - Index trên `receiver` giúp filter nhanh
  - Sort theo `created_at` có thể tốn kém nếu user có nhiều notifications
  - Index đơn trên `created_at` không hiệu quả vì không filter theo nó
  - **Lưu ý**: Composite index `(receiver, created_at)` sẽ rất hiệu quả, nhưng yêu cầu chỉ index đơn

### 2. `mark_as_read` (Update)
```sql
UPDATE notifications 
SET is_read = TRUE 
WHERE id = ? AND receiver = ?
```
- **Filter**: `id` (PK - đã có index) ✅ và `receiver` (đã có index) ✅
- **Không cần thêm index**

### 3. Các query tiềm năng (chưa có trong code hiện tại)
- Filter theo `group_id`: Không thấy query nào filter theo `group_id` trong repository/view
- Filter theo `is_read`: Không thấy query riêng filter theo `is_read` (chỉ dùng kết hợp với `receiver`)
- Filter theo `created_at`: Không thấy query filter theo date range

## Đề xuất Index

### ✅ **created_at** - CÓ THỂ CẦN (Tùy chọn)
**Lý do:**
- Được dùng trong `ORDER BY created_at DESC` trong query chính `get_by_receiver`
- Nếu mỗi user có nhiều notifications (hàng trăm/thousands), sort có thể chậm
- Index trên `created_at` có thể giúp PostgreSQL sort nhanh hơn sau khi filter theo `receiver`

**Lưu ý:**
- Index đơn trên `created_at` không hiệu quả bằng composite index `(receiver, created_at)`
- Chỉ nên thêm nếu:
  - Có vấn đề performance với ORDER BY trong production
  - Mỗi user có rất nhiều notifications (>1000)
  - Hoặc có query filter theo date range trong tương lai

**Cách thêm:**
```python
created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False, index=True)
```

### ❌ **group_id** - KHÔNG CẦN THÊM
- Đã có index
- Không thấy query nào filter theo `group_id` trong code hiện tại
- Nếu trong tương lai cần query notifications của một group, index đã có sẵn

### ❌ **is_read** - KHÔNG CẦN THÊM
- Đã có index
- Không thấy query riêng filter theo `is_read` (chỉ dùng trong UPDATE)

### ❌ **template_code** - KHÔNG CẦN
- Không thấy query filter theo `template_code`

### ❌ **title, content** - KHÔNG CẦN
- Text fields, không phù hợp cho index đơn
- Nếu cần search, nên dùng full-text search index

## Kết luận

### Index nên thêm:
1. **created_at** (tùy chọn) - Chỉ nên thêm nếu có vấn đề performance với ORDER BY

### Index đã đủ:
- `id` (PK)
- `group_id`
- `receiver`
- `is_read`

### Lưu ý quan trọng:
- Query pattern chính `get_by_receiver` sẽ được tối ưu tốt nhất với **composite index** `(receiver, created_at DESC)`
- Nhưng vì yêu cầu chỉ index đơn, nên:
  - Index trên `receiver` đã đủ cho filter
  - Index trên `created_at` có thể giúp sort (nhưng không hiệu quả bằng composite)
  - Nên monitor performance và chỉ thêm `created_at` index nếu thực sự cần

## Khuyến nghị

**Nên thêm index trên `created_at`** nếu:
- Hệ thống có nhiều notifications per user (>100)
- Có vấn đề performance với query `get_by_receiver`
- Hoặc dự kiến sẽ có query filter theo date range trong tương lai

**Không cần thêm** nếu:
- Số lượng notifications per user nhỏ (<100)
- Performance hiện tại đã đủ tốt
- Không có kế hoạch query theo date range



