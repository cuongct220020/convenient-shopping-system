// 1. Phân tích phản hồi JSON
var jsonData = pm.response.json();

// 2. Kiểm tra token có tồn tại trong đường dẫn data.access_token không
if (jsonData.data && jsonData.data.access_token) {
    // 3. Lưu vào biến môi trường
    pm.environment.set("jwt_token", jsonData.data.access_token);
    
    // In ra console để kiểm tra
    console.log("SUCCESS: Token đã được lưu:", jsonData.data.access_token);
} else {
    console.error("ERROR: Không tìm thấy token! Kiểm tra lại cấu trúc JSON.");
}