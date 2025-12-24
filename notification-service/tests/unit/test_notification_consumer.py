import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.consumers.notification_consumer import consume_notifications

@pytest.mark.asyncio
async def test_consume_notification_success():
    """
    Test xem Consumer có xử lý đúng message từ Kafka và gọi EmailService không.
    """
    # 1. Giả lập một Message từ Kafka
    mock_msg = MagicMock()
    # Giả lập cấu trúc dữ liệu JSON mà user-service gửi sang
    mock_msg.value = {
        "email": "test_consumer@example.com",
        "otp_code": "999888",
        "action": "register"
    }

    # 2. Mock Kafka Consumer
    mock_consumer = AsyncMock()
    mock_consumer.start = AsyncMock()
    mock_consumer.stop = AsyncMock()
    
    # Kỹ thuật Mock Async Iterator:
    # Khi gọi `async for msg in consumer`, nó sẽ gọi `__aiter__`.
    # Ta trả về một iterator có sẵn danh sách các message.
    mock_consumer.__aiter__.return_value = iter([mock_msg])

    # 3. Mock KafkaManager để trả về mock_consumer trên
    with patch("app.consumers.notification_consumer.kafka_manager") as mock_manager:
        mock_manager.create_consumer.return_value = mock_consumer
        
        # 4. Mock EmailService để verify xem nó có được gọi không
        # Lưu ý đường dẫn patch phải trỏ tới nơi EmailService ĐƯỢC SỬ DỤNG (app.consumers...)
        with patch("app.consumers.notification_consumer.email_service.send_otp", new_callable=AsyncMock) as mock_send_email:
            
            # 5. Chạy hàm consumer
            # Hàm này sẽ chạy hết danh sách message (1 cái) rồi dừng vòng lặp
            await consume_notifications()

            # 6. Assert: Consumer đã start và stop
            mock_consumer.start.assert_awaited_once()
            mock_consumer.stop.assert_awaited_once()

            # 7. Assert QUAN TRỌNG NHẤT: Email Service phải được gọi với đúng thông tin từ message
            mock_send_email.assert_awaited_once_with(
                email="test_consumer@example.com",
                otp_code="999888",
                action="register"
            )
