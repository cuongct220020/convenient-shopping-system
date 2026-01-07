# Kế hoạch Triển khai: Kong Gateway Auto-SSL (ACME Challenge Routing)

Tài liệu này hướng dẫn chi tiết quy trình triển khai hệ thống "Convenient Shopping System" lên AWS EC2.
Mô hình này sử dụng cơ chế **"Challenge Routing"** để tự động hóa việc xác thực và gia hạn chứng chỉ SSL Let's Encrypt mà không cần dừng dịch vụ hay can thiệp thủ công (Zero-Downtime Renewal).

## Kiến trúc

```text
User (HTTPS) --> [ AWS EC2 (Elastic IP) ] --> [ Kong Gateway (Port 8443) ] --> [ Microservices ]
User (HTTP)  --> [ AWS EC2 (Elastic IP) ] --> [ Kong Gateway (Port 80) ]
                                                      |
                                                      | (/.well-known/acme-challenge/*)
                                                      v
                                              [ ACME Challenge Service ] <--- [ Certbot Auto-Renew ]
```

---

## Giai đoạn 1: Chuẩn bị Hạ tầng AWS

### 1.1. Database (AWS RDS)
*   Tạo một **PostgreSQL** database trên AWS RDS.
*   **Lưu ý:** Ghi lại `Endpoint`, `Username`, `Password`, và `Database Name`.
*   **Security Group (RDS):** Cho phép EC2 Instance kết nối vào port `5432`.

### 1.2. EC2 Instance
*   **OS:** Ubuntu 22.04 LTS (Khuyên dùng) hoặc Amazon Linux 2023.
*   **Instance Type:** Tối thiểu t2.medium (để chạy Kafka và Java/Python services).
*   **Elastic IP:** Cấp phát và gán 1 Elastic IP cố định cho Instance.

### 1.3. DNS
*   Tạo **A Record** cho tên miền (ví dụ: `dichotienloi.com`) trỏ về **Elastic IP** vừa tạo.

### 1.4. Security Group (Firewall)
Cấu hình Inbound Rules cho EC2:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | My IP | Chỉ cho phép IP quản trị viên |
| HTTP | TCP | 80 | 0.0.0.0/0 | Để xác thực SSL & Redirect |
| HTTPS| TCP | 443 | 0.0.0.0/0 | Cổng API chính thức |

### 1.5. Hướng dẫn truy cập Server (SSH)
Trước khi cài đặt, bạn cần kết nối vào server từ máy tính cá nhân.

#### A. Đối với MacOS / Linux
1.  Mở **Terminal**.
2.  Di chuyển đến thư mục chứa file key (`.pem`) bạn đã tải về từ AWS:
    ```bash
    cd ~/Downloads
    ```
3.  Cấp quyền bảo mật cho file key (Bắt buộc, nếu không AWS sẽ từ chối):
    ```bash
    chmod 400 your-key-pair.pem
    ```
4.  Kết nối SSH:
    ```bash
    ssh -i your-key-pair.pem ubuntu@<Public-IP-Của-EC2>
    ```

#### B. Đối với Windows (Windows 10/11)
Hiện nay Windows 10/11 đã tích hợp sẵn OpenSSH Client trong PowerShell hoặc CMD.

1.  Mở **PowerShell** hoặc **Command Prompt**.
2.  Di chuyển đến thư mục chứa file key:
    ```powershell
    cd $env:USERPROFILE\Downloads
    ```
3.  **Lưu ý về quyền:** Windows thường không có lệnh `chmod`. Nếu SSH báo lỗi *"UNPROTECTED PRIVATE KEY FILE"*, bạn cần vào **Properties** của file .pem -> **Security** -> **Advanced** -> **Disable Inheritance** -> Xóa hết các user khác, chỉ giữ lại user của bạn với quyền **Read**.
4.  Kết nối SSH:
    ```powershell
    ssh -i your-key-pair.pem ubuntu@<Public-IP-Của-EC2>
    ```
*(Nếu dùng Windows 7/8 hoặc thích giao diện đồ họa, bạn có thể dùng phần mềm **PuTTY**, nhưng cần dùng PuTTYgen để chuyển đổi file `.pem` sang `.ppk` trước).*

---

## Giai đoạn 2: Cài đặt Môi trường Server

SSH vào server EC2 và thực hiện:

### 2.1. Cài đặt Docker & Docker Compose
```bash
# Update hệ thống & Cài đặt gói cần thiết
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Thêm Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Setup repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Cấp quyền Docker cho user hiện tại
sudo usermod -aG docker $USER
# LƯU Ý: Logout và SSH lại để lệnh này có hiệu lực
```

### 2.2. Lấy chứng chỉ SSL lần đầu (Bootstrap)
Vì Kong cần chứng chỉ để khởi động, ta cần lấy chứng chỉ lần đầu tiên bằng Certbot trên Host.

```bash
# Cài đặt Certbot trên Host (chỉ dùng lần đầu)
sudo apt-get update && sudo apt-get install -y certbot

# Tắt Docker nếu đang chạy để giải phóng port 80
sudo systemctl stop docker

# Lấy chứng chỉ (Thay api.yourdomain.com bằng domain thật)
sudo certbot certonly --standalone -d dichotienloi.com

# Khởi động lại Docker service
sudo systemctl start docker
```
Chứng chỉ sẽ được lưu tại: `/etc/letsencrypt/live/dichotienloi.com/`

---

## Giai đoạn 3: Triển khai Ứng dụng

### 3.1. Clone Source Code
```bash
git clone https://github.com/your-repo/convenient-shopping-system.git
cd convenient-shopping-system
```

### 3.2. Cập nhật Docker Compose
Mở file `docker-compose.prod.yml` và tìm service `kong-gateway`.
Cập nhật phần `volumes` để trỏ đúng thư mục tên miền của bạn:

```yaml
    volumes:
      # ...
      # Thay 'api.yourdomain.com' bằng tên miền thật
      - /etc/letsencrypt/live/dichotienloi.com/fullchain.pem:/etc/secrets/cert/fullchain.pem:ro
      - /etc/letsencrypt/live/dichotienloi.com/privkey.pem:/etc/secrets/cert/privkey.pem:ro
```

### 3.3. Tạo file biến môi trường (.env)
Tạo file `.env` từ `.env.example` và điền thông tin RDS, Redis, Kafka thật:

```bash
cp .env.example .env
nano .env
```
Nội dung quan trọng cần sửa:
```ini
# AWS RDS Config
DB_HOST=your-rds-endpoint.amazonaws.com
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Kong Config Path
KONG_CONFIG_FILE=./api-gateway/kong.prod.yml
```

---

## Giai đoạn 4: Khởi chạy & Vận hành

### 4.1. Start Services
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Hệ thống sẽ khởi chạy bao gồm cả service `certbot` (auto-renew) và `acme-challenge`.

### 4.2. Kiểm tra hoạt động
1.  **SSL Auto-Renew:** Service `certbot` sẽ chạy ngầm, kiểm tra mỗi 12 giờ.
2.  **HTTPS Redirect:** Truy cập `http://api.shopping.system.com` -> Sẽ tự chuyển sang `https://`.
3.  **ACME Challenge:** Truy cập `http://api.shopping.system.com/.well-known/acme-challenge/test` -> Sẽ trả về 404 từ Nginx (hoặc file test nếu bạn tạo), chứng tỏ routing đã đúng.

---

## Giai đoạn 5: Bảo trì (Maintenance)

Hệ thống được thiết kế để **Tự động hoàn toàn**.
Tuy nhiên, nếu bạn cần gia hạn thủ công để kiểm tra:

```bash
# Chạy lệnh renew bên trong container certbot
docker compose -f docker-compose.prod.yml exec certbot certbot renew --force-renewal
```

Nếu gia hạn thành công, bạn cần reload Kong để nhận chứng chỉ mới (nếu Kong không tự nhận):
```bash
docker compose -f docker-compose.prod.yml restart kong-gateway
```
