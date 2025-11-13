# User Service

## NOTE ve phan quyen

✦ Đây là một câu hỏi rất quan trọng về kiến trúc hệ thống. Việc thiết kế phân quyền đúng cách ngay từ đầu sẽ giúp hệ thống của bạn an toàn, hiệu quả và dễ bảo trì.

  Câu trả lời ngắn gọn: KHÔNG, bạn không nên tạo một endpoint /roles để các microservice khác gọi đến và kiểm tra quyền. Đây là một anti-pattern. Giải pháp tốt nhất là một mô hình hybrid, kết hợp giữa API
  Gateway và logic tại từng microservice.

  ---

  Phân tích và Giải pháp tốt nhất (Best Practice)

  Hãy phân biệt rõ 2 khái niệm:
   * Authentication (Xác thực): "Bạn là ai?" - Hệ thống của bạn đã làm tốt việc này. User-service xác thực người dùng và cấp ra một JWT (JSON Web Token).
   * Authorization (Phân quyền): "Bạn được làm gì?" - Đây là phần chúng ta cần làm rõ.

  Trong hệ thống của bạn có 2 cấp độ vai trò:
   1. Vai trò hệ thống (System Role): USER, ADMIN. Vai trò này là toàn cục, gắn liền với tài khoản người dùng.
   2. Vai trò theo ngữ cảnh (Contextual Role): HEAD_CHEF, MEMBER. Vai trò này chỉ có ý nghĩa bên trong một nhóm cụ thể.

  Mô hình phân quyền tốt nhất cho kiến trúc microservice có API Gateway là:

  1. API Gateway: Thực hiện "Phân quyền thô" (Coarse-Grained Authorization)

   * Nhiệm vụ của `user-service`: Khi người dùng đăng nhập thành công, user-service phải tạo ra một JWT. Điều cốt lõi là payload của JWT này phải chứa các thông tin định danh quan trọng và vai trò hệ thống của
     người dùng.

   1     // JWT Payload Example
   2     {
   3       "user_id": "a1b2c3d4-...",
   4       "system_role": "ADMIN", // hoặc "USER"
   5       "exp": 1678886400 // Thời gian hết hạn
   6     }

   * Nhiệm vụ của API Gateway (Kong):
      a.  Xác thực JWT: Với mọi request gửi đến các microservice, Gateway sẽ là người đầu tiên kiểm tra chữ ký của JWT để đảm bảo tính hợp lệ. Nếu token không hợp lệ, request sẽ bị chặn ngay tại cửa.
  b. Phân quyền thô: Gateway sẽ đọc payload của JWT và thực thi các quy tắc đơn giản. Ví dụ: bạn có thể cấu hình Kong để chỉ cho phép các request có system_role: "ADMIN" trong JWT được đi tiếp đến các đường
  dẫn bắt đầu bằng /admin/*. Các request khác sẽ bị trả về lỗi 403 Forbidden ngay lập tức.

   * Lợi ích:
       * Hiệu năng cao: Chặn các truy cập không hợp lệ ngay tại biên, giảm tải cho các microservice bên trong.
       * Bảo mật lớp đầu: Bảo vệ toàn bộ các nhóm endpoint nhạy cảm một cách dễ dàng.

  2. Microservice: Thực hiện "Phân quyền mịn" (Fine-Grained Authorization)

  Sau khi request vượt qua được Gateway, nó sẽ đến microservice tương ứng (ví dụ: user-service).

   * Nhiệm vụ của Microservice:
      a.  Microservice tin tưởng vào thông tin trong JWT (vì Gateway đã xác thực nó) và lấy ra user_id, system_role.
      b.  Dựa vào thông tin đó, microservice thực hiện logic phân quyền chi tiết mà chỉ nó mới hiểu được. Ví dụ, với request DELETE /groups/{groupId}:
           * user-service sẽ kiểm tra trong database của chính nó: "User với user_id này có phải là HEAD_CHEF của nhóm {groupId} không? HOẶC system_role của user này có phải là ADMIN không?"
           * Nếu một trong hai điều kiện đúng, request được thực thi. Nếu không, trả về lỗi 403 Forbidden.

   * Lợi ích:
       * Logic đúng chỗ: Logic nghiệp vụ phức tạp (ai là headchef của nhóm nào) nằm ở service sở hữu dữ liệu đó (user-service).
       * Không phụ thuộc chéo: Các service không cần phải gọi nhau để hỏi quyền, giúp giảm độ trễ và tăng tính ổn định.

  Vậy có nên tạo endpoint /roles không?

  KHÔNG, không dùng cho việc kiểm tra quyền ở backend. Như đã giải thích, việc service A gọi sang service B để hỏi "user này có quyền X không?" sẽ tạo ra sự phụ thuộc không cần thiết, làm tăng độ trễ và điểm
  chết cho hệ thống.

  Tuy nhiên, endpoint `/roles` có một mục đích sử dụng hợp lệ:

   * Dành cho Frontend/UI: Bạn có thể tạo một endpoint GET /admin/roles (chỉ Admin được gọi) để trả về danh sách tất cả các vai trò có thể có trong hệ thống: ["USER", "ADMIN", "HEAD_CHEF", "MEMBER"].
   * Mục đích: Giúp trang quản trị của Admin có thể hiển thị một danh sách dropdown để chọn và gán vai trò cho người dùng. Đây là nghiệp vụ phục vụ cho giao diện, không phải để kiểm tra quyền lúc thực thi API.


