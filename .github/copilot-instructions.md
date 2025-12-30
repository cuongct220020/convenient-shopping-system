# Custom Instructions for Convenient Shopping System Project

## 1. Context & Domain Knowledge

Đây là hệ thống quản lý mua sắm và thực phẩm thông minh với các nghiệp vụ chính:

* **Shopping Plan:** Lập kế hoạch, phân loại hàng hóa, chia sẻ nhóm gia đình.
* **Storage/Fridge Management:** Theo dõi hạn sử dụng (trước 3 ngày), vị trí lưu trữ, tồn kho.
* **Meal Planning:** Gợi ý món ăn từ nguyên liệu sẵn có (Inventory-based), quản lý công thức (Recipes).
* **Automation:** Sau khi mua hàng xong (Shopping Plan hoàn tất), hệ thống tự động cập nhật vào Storage. Khi nấu ăn, tự động trừ tồn kho.

## 2. Technical Stack & Architecture

* **Architecture:** Microservices.
* **Backend:** Python 3.12+.
* **FastAPI:** Sử dụng cho Recipe Service (tại `Recipe Service/`).
* **Sanic:** Sử dụng cho User Service, Shopping & Storage Service (tại `microservices/` và `Shopping & Storage Service/`).


* **Frontend:** React, TypeScript, Tailwind CSS, Vite (tại `webapp/`).
* **Infrastructure:**
* **Message Broker:** Kafka (dùng để giao tiếp giữa các service, ví dụ: Shopping -> Storage).
* **Caching:** Redis.
* **API Gateway:** Kong.
* **Database:** SQLAlchemy (PostgreSQL).



## 3. Coding Standards (Python & Backend)

Tuân thủ nghiêm ngặt tệp `docs/conventions/python_oop_conventions.md`:

* **OOP First:** Luôn sử dụng Class, kế thừa từ `BaseRepository`, `BaseService`, `BaseModel` trong thư mục `shared/`.
* **Typing:** Luôn sử dụng Type Hints (ví dụ: `def get_user(user_id: int) -> User:`) cho tất cả các hàm.
* **Schema:** Sử dụng Pydantic (FastAPI) hoặc các BaseSchema (Sanic) để validate dữ liệu.
* **Dependencies:** Sử dụng Dependency Injection trong FastAPI.
* **Async:** Luôn sử dụng `async/await` cho các tác vụ I/O, Database và Kafka.

## 4. Coding Standards (Frontend)

* **TypeScript:** Nghiêm cấm sử dụng `any`. Luôn định nghĩa Interface/Type rõ ràng.
* **Components:** Sử dụng Functional Components và Hooks.
* **Testing:** Viết Unit Test bằng Vitest cho các logic xử lý dữ liệu (tham khảo `webapp/src/components/Avatar/test.tsx`).
* **Styling:** Sử dụng Tailwind CSS utility classes.

## 5. Specific Service Instructions

* **User Service:** Tập trung vào xác thực (JWT), OTP, và quản lý Family Group.
* **Recipe Service:** Ưu tiên logic gợi ý món ăn dựa trên nguyên liệu (Ingredient matching).
* **Shopping & Storage Service:** Chú trọng vào State Machine của đơn hàng (Plan Status) và logic trừ tồn kho.

## 6. Communication Style

* Phản hồi bằng **tiếng Việt**, nhưng comment code bằng tiếng anh. 
* Khi giải thích code, hãy giải thích theo tư duy hệ thống Microservices (Ví dụ: "Đoạn code này sẽ gửi một event qua Kafka để thông báo cho Storage Service").
* Nếu phát hiện code hiện tại vi phạm `python-oop-conventions.md`, hãy cảnh báo và đề xuất phương án refactor theo chuẩn OOP.