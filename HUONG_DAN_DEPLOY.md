# Hướng Dẫn Deploy Hệ Thống Convenient Shopping System

Tài liệu này hướng dẫn chi tiết từng bước để:
1. **Deploy Backend lên AWS EC2** với domain `dichotienloi123.duckdns.org`
2. **Deploy Frontend (webapp) lên Netlify**

---

## PHẦN 1: DEPLOY BACKEND LÊN AWS EC2

### Bước 1: Chuẩn bị Hạ tầng AWS

#### 1.1. Tạo EC2 Instance

1. Đăng nhập vào **AWS Console** → **EC2 Dashboard**
2. Click **Launch Instance**
3. Cấu hình:
   - **Name**: `convenient-shopping-backend`
   - **AMI**: Ubuntu Server 22.04 LTS (hoặc Amazon Linux 2023)
   - **Instance Type**: `t2.medium` (tối thiểu, khuyến nghị `t2.large` hoặc `t3.medium` để chạy Kafka)
   - **Key Pair**: Tạo mới hoặc chọn key pair có sẵn (lưu file `.pem` an toàn)
   - **Network Settings**: 
     - VPC: Chọn VPC mặc định hoặc tạo mới
     - Subnet: Chọn public subnet
     - Auto-assign Public IP: **Enable**
     - Security Group: Tạo mới với tên `shopping-backend-sg`
4. **Configure Security Group** (hoặc tạo sau):
   - **SSH (22)**: Chỉ cho phép IP của bạn (My IP)
   - **HTTP (80)**: 0.0.0.0/0 (cho Let's Encrypt)
   - **HTTPS (443)**: 0.0.0.0/0 (cho API)
5. Click **Launch Instance**

#### 1.2. Cấp phát Elastic IP

1. Trong **EC2 Dashboard** → **Elastic IPs** (bên trái)
2. Click **Allocate Elastic IP address**
3. Chọn **Amazon's pool of IPv4 addresses**
4. Click **Allocate**
5. Chọn Elastic IP vừa tạo → **Actions** → **Associate Elastic IP address**
6. Chọn Instance vừa tạo → **Associate**
7. **Ghi lại Elastic IP** (ví dụ: `54.123.45.67`)

#### 1.3. Cấu hình DNS trên DuckDNS

1. Truy cập https://www.duckdns.org/
2. Đăng nhập hoặc đăng ký tài khoản
3. Chọn domain `dichotienloi123`
4. Trong phần **IPv4**, nhập **Elastic IP** của EC2
5. Click **Update IP**
6. Đợi vài phút để DNS propagate

#### 1.4. Tạo RDS PostgreSQL Database

1. Trong **AWS Console** → **RDS Dashboard**
2. Click **Create database**
3. Cấu hình:
   - **Engine**: PostgreSQL (phiên bản mới nhất)
   - **Templates**: Free tier (nếu có) hoặc Production
   - **DB Instance identifier**: `shopping-db`
   - **Master username**: `postgres` (hoặc tên khác)
   - **Master password**: Tạo mật khẩu mạnh (lưu lại)
   - **DB Instance class**: `db.t3.micro` (free tier) hoặc `db.t3.small`
   - **Storage**: 20 GB (tối thiểu)
   - **VPC**: Chọn cùng VPC với EC2
   - **Subnet group**: Mặc định hoặc tạo mới
   - **Public access**: **No** (bảo mật hơn)
   - **VPC Security Group**: Tạo mới `rds-sg`
4. Click **Create database**
5. Sau khi tạo xong, vào **Connectivity & security** → Ghi lại **Endpoint** (ví dụ: `shopping-db.xxxxx.us-east-1.rds.amazonaws.com`)

#### 1.5. Cấu hình Security Group cho RDS

1. Vào **RDS Dashboard** → Chọn database → **Connectivity & security**
2. Click vào Security Group → **Inbound rules** → **Edit inbound rules**
3. Thêm rule:
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: Chọn Security Group của EC2 instance (shopping-backend-sg)
4. Click **Save rules**

---

### Bước 2: Kết nối vào EC2 Instance

#### 2.1. Trên Windows (PowerShell/CMD)

1. Mở **PowerShell** hoặc **Command Prompt**
2. Di chuyển đến thư mục chứa file `.pem`:
   ```powershell
   cd $env:USERPROFILE\Downloads
   ```
3. Cấp quyền cho file key (nếu cần):
   - Click chuột phải file `.pem` → **Properties** → **Security** → **Advanced**
   - **Disable Inheritance** → Xóa các user khác, chỉ giữ user của bạn với quyền **Read**
4. Kết nối SSH:
   ```powershell
   ssh -i your-key-pair.pem ubuntu@<Elastic-IP>
   ```
   (Thay `your-key-pair.pem` bằng tên file key của bạn, và `<Elastic-IP>` bằng Elastic IP thực tế)

#### 2.2. Trên MacOS/Linux

1. Mở **Terminal**
2. Di chuyển đến thư mục chứa file `.pem`:
   ```bash
   cd ~/Downloads
   ```
3. Cấp quyền:
   ```bash
   chmod 400 your-key-pair.pem
   ```
4. Kết nối SSH:
   ```bash
   ssh -i your-key-pair.pem ubuntu@<Elastic-IP>
   ```

---

### Bước 3: Cài đặt Môi trường trên EC2

#### 3.1. Cập nhật hệ thống

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 3.2. Cài đặt Docker và Docker Compose

```bash
# Cài đặt các gói cần thiết
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Thêm Docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Setup repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Cài đặt Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Cấp quyền Docker cho user hiện tại
sudo usermod -aG docker $USER

# Logout và SSH lại để áp dụng quyền
exit
```

**Lưu ý**: Sau khi logout, SSH lại vào server để tiếp tục.

#### 3.3. Xác minh cài đặt Docker

```bash
docker --version
docker compose version
```

---

### Bước 4: Lấy SSL Certificate lần đầu

#### 4.1. Cài đặt Certbot trên Host

```bash
sudo apt-get update
sudo apt-get install -y certbot
```

#### 4.2. Tắt Docker tạm thời (để giải phóng port 80)

```bash
sudo systemctl stop docker
```

#### 4.3. Lấy chứng chỉ SSL

```bash
sudo certbot certonly --standalone -d dichotienloi123.duckdns.org
```

- Nhập email của bạn khi được hỏi
- Đồng ý với điều khoản
- Chọn **Y** để chia sẻ email với EFF (tùy chọn)

#### 4.4. Khởi động lại Docker

```bash
sudo systemctl start docker
```

#### 4.5. Kiểm tra chứng chỉ

```bash
sudo ls -la /etc/letsencrypt/live/dichotienloi123.duckdns.org/
```

Bạn sẽ thấy các file:
- `fullchain.pem`
- `privkey.pem`

---

### Bước 5: Clone và Cấu hình Source Code

#### 5.1. Clone repository

```bash
cd ~
git clone https://github.com/your-repo/IT4990-Convenient-Shopping-System.git
cd IT4990-Convenient-Shopping-System
```

(Thay `your-repo` bằng repository thực tế của bạn)

#### 5.2. Tạo file .env

```bash
nano .env
```

Thêm nội dung sau (điều chỉnh theo thông tin thực tế):

```ini
# Database Configuration (AWS RDS)
DB_HOST=shopping-db.xxxxx.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_NAME=postgres

# Redis Configuration
REDIS_HOST=redis-caching
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password_here
REDIS_DECODE_RESPONSES=true

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka-broker:9092

# Kong Gateway Configuration
KONG_CONFIG_FILE=./api-gateway/kong.prod.yml

# JWT Configuration (cần lấy từ user-service)
JWT_RSA_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
...your public key here...
-----END PUBLIC KEY-----
```

**Lưu ý quan trọng**:
- Thay `DB_HOST` bằng RDS endpoint thực tế
- Thay `DB_PASSWORD` bằng mật khẩu RDS
- Tạo `REDIS_PASSWORD` mạnh (ví dụ: dùng `openssl rand -base64 32`)
- Để lấy `JWT_RSA_PUBLIC_KEY`, xem file trong `user-service/secrets/` hoặc tạo mới

#### 5.3. Tạo file .env cho user-service (nếu cần)

```bash
nano user-service/.env
```

Thêm các biến môi trường riêng cho user-service nếu có.

#### 5.4. Tạo file .env cho notification-service (nếu cần)

```bash
nano notification-service/.env
```

Thêm các biến môi trường riêng cho notification-service nếu có.

#### 5.5. Cập nhật docker-compose.prod.yml

Mở file `docker-compose.prod.yml` và tìm phần `kong-gateway` → `volumes`:

```bash
nano docker-compose.prod.yml
```

Tìm dòng:
```yaml
      - ./certs/fullchain.pem:/etc/secrets/cert/fullchain.pem:ro
      - ./certs/privkey.pem:/etc/secrets/cert/privkey.pem:ro
```

Thay bằng:
```yaml
      - /etc/letsencrypt/live/dichotienloi123.duckdns.org/fullchain.pem:/etc/secrets/cert/fullchain.pem:ro
      - /etc/letsencrypt/live/dichotienloi123.duckdns.org/privkey.pem:/etc/secrets/cert/privkey.pem:ro
```

Lưu file: `Ctrl + O`, `Enter`, `Ctrl + X`

#### 5.6. Tạo thư mục certs (nếu chưa có)

```bash
mkdir -p certs
```

---

### Bước 6: Cấu hình Kong Gateway

#### 6.1. Kiểm tra file kong.prod.yml

File `api-gateway/kong.prod.yml` đã được cấu hình sẵn. Đảm bảo domain trong file này phù hợp (nếu có).

#### 6.2. Cập nhật JWT Public Key

Nếu bạn chưa có JWT public key:

1. Tạo cặp key RSA (trên máy local hoặc server):
   ```bash
   ssh-keygen -t rsa -b 2048 -f jwt_key -N ""
   ```

2. Lấy public key:
   ```bash
   cat jwt_key.pub
   ```

3. Copy toàn bộ nội dung (bao gồm `-----BEGIN PUBLIC KEY-----` và `-----END PUBLIC KEY-----`)

4. Thêm vào file `.env`:
   ```ini
   JWT_RSA_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
   ...paste key here...
   -----END PUBLIC KEY-----
   ```

---

### Bước 7: Khởi chạy Hệ thống

#### 7.1. Build và khởi động services

```bash
cd ~/IT4990-Convenient-Shopping-System
docker compose -f docker-compose.prod.yml up -d --build
```

Quá trình này sẽ mất vài phút để build các images.

#### 7.2. Kiểm tra logs

```bash
# Xem logs của tất cả services
docker compose -f docker-compose.prod.yml logs -f

# Xem logs của service cụ thể
docker compose -f docker-compose.prod.yml logs -f kong-gateway
docker compose -f docker-compose.prod.yml logs -f user-service
```

#### 7.3. Kiểm tra trạng thái containers

```bash
docker compose -f docker-compose.prod.yml ps
```

Tất cả containers phải có trạng thái `Up` và `healthy`.

---

### Bước 8: Chạy Database Migrations

#### 8.1. User Service Migration

```bash
docker compose -f docker-compose.prod.yml exec user-service alembic upgrade head
```

#### 8.2. Recipe Service Migration

```bash
docker compose -f docker-compose.prod.yml exec recipe-service alembic upgrade head
```

#### 8.3. Meal Service Migration

```bash
docker compose -f docker-compose.prod.yml exec meal-service alembic upgrade head
```

#### 8.4. Shopping Storage Service Migration

```bash
docker compose -f docker-compose.prod.yml exec shopping-storage-service alembic upgrade head
```

#### 8.5. Notification Service Migration

```bash
docker compose -f docker-compose.prod.yml exec notification-service alembic upgrade head
```

---

### Bước 9: Kiểm tra Hệ thống

#### 9.1. Kiểm tra Health Check

```bash
# Kiểm tra Kong Gateway
curl http://localhost:8001/health

# Kiểm tra User Service qua Kong
curl https://dichotienloi123.duckdns.org/api/v1/user-service/health

# Kiểm tra các service khác
curl https://dichotienloi123.duckdns.org/api/v2/notification-service/health
```

#### 9.2. Kiểm tra SSL

Truy cập trình duyệt:
- `https://dichotienloi123.duckdns.org/api/v1/user-service/health`
- Phải thấy chứng chỉ SSL hợp lệ (khóa xanh)

#### 9.3. Kiểm tra HTTP → HTTPS Redirect

Truy cập:
- `http://dichotienloi123.duckdns.org/api/v1/user-service/health`
- Phải tự động redirect sang HTTPS

---

### Bước 10: Cấu hình Auto-Renew SSL

Service `certbot` trong `docker-compose.prod.yml` đã được cấu hình để tự động gia hạn SSL mỗi 12 giờ. Để kiểm tra:

```bash
docker compose -f docker-compose.prod.yml logs certbot
```

Để test manual renewal:

```bash
docker compose -f docker-compose.prod.yml exec certbot certbot renew --force-renewal
```

Sau khi renew, reload Kong:

```bash
docker compose -f docker-compose.prod.yml restart kong-gateway
```

---

### Bước 11: Cấu hình Firewall (UFW) - Tùy chọn

Để tăng cường bảo mật, cấu hình UFW:

```bash
# Cho phép SSH
sudo ufw allow 22/tcp

# Cho phép HTTP và HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Bật firewall
sudo ufw enable

# Kiểm tra trạng thái
sudo ufw status
```

**Lưu ý**: Đảm bảo Security Group trên AWS đã mở port 22, 80, 443 trước khi bật UFW.

---

## PHẦN 2: DEPLOY FRONTEND (WEBAPP) LÊN NETLIFY

### Bước 1: Chuẩn bị Source Code

#### 1.1. Cấu hình Environment Variables cho Frontend

Trong thư mục `webapp`, tạo file `.env.production`:

```bash
cd ~/IT4990-Convenient-Shopping-System/webapp
nano .env.production
```

Thêm nội dung:

```ini
VITE_API_BASE_URL=https://dichotienloi123.duckdns.org
```

**Lưu ý**: File này sẽ được sử dụng khi build production.

#### 1.2. Kiểm tra vite.config.ts

Đảm bảo file `vite.config.ts` không cần chỉnh sửa gì (đã đúng cấu hình).

---

### Bước 2: Build Frontend Locally (Test)

#### 2.1. Cài đặt dependencies

Trên máy local (Windows/Mac/Linux):

```bash
cd webapp
npm install
# hoặc nếu dùng pnpm
pnpm install
```

#### 2.2. Build production

```bash
npm run build
# hoặc
pnpm build
```

Thư mục `dist` sẽ được tạo ra chứa các file build.

#### 2.3. Test build locally

```bash
npm run serve
# hoặc
pnpm serve
```

Truy cập `http://localhost:4173` để kiểm tra.

---

### Bước 3: Deploy lên Netlify

#### 3.1. Tạo tài khoản Netlify

1. Truy cập https://www.netlify.com/
2. Đăng ký/Đăng nhập bằng GitHub, GitLab, hoặc Email

#### 3.2. Cách 1: Deploy qua Netlify CLI (Khuyến nghị)

**Trên máy local:**

1. Cài đặt Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Đăng nhập Netlify:
   ```bash
   netlify login
   ```
   (Sẽ mở trình duyệt để xác thực)

3. Di chuyển đến thư mục webapp:
   ```bash
   cd webapp
   ```

4. Khởi tạo site Netlify:
   ```bash
   netlify init
   ```
   - Chọn **Create & configure a new site**
   - Nhập tên site (ví dụ: `convenient-shopping-webapp`)
   - Chọn team (nếu có)
   - Build command: `npm run build` hoặc `pnpm build`
   - Directory to deploy: `dist`

5. Tạo file `netlify.toml` trong thư mục `webapp`:
   ```bash
   nano netlify.toml
   ```
   
   Thêm nội dung:
   ```toml
   [build]
     command = "npm run build"
     publish = "dist"
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

6. Deploy:
   ```bash
   netlify deploy --prod
   ```

7. Netlify sẽ cung cấp URL (ví dụ: `https://convenient-shopping-webapp.netlify.app`)

#### 3.3. Cách 2: Deploy qua GitHub (Tự động)

1. **Push code lên GitHub** (nếu chưa có):
   ```bash
   git add .
   git commit -m "Prepare for Netlify deployment"
   git push origin main
   ```

2. Trên **Netlify Dashboard**:
   - Click **Add new site** → **Import an existing project**
   - Chọn **GitHub** → Authorize Netlify
   - Chọn repository `IT4990-Convenient-Shopping-System`
   - **Configure build settings**:
     - **Base directory**: `webapp`
     - **Build command**: `npm run build` hoặc `pnpm build`
     - **Publish directory**: `webapp/dist`
   - Click **Deploy site**

3. **Cấu hình Environment Variables**:
   - Trong site settings → **Environment variables**
   - Thêm biến:
     - **Key**: `VITE_API_BASE_URL`
     - **Value**: `https://dichotienloi123.duckdns.org`
   - Click **Save**

4. **Trigger lại build**:
   - Vào **Deploys** → **Trigger deploy** → **Clear cache and deploy site**

#### 3.4. Cách 3: Deploy thủ công (Drag & Drop)

1. Build project trên máy local:
   ```bash
   cd webapp
   npm run build
   ```

2. Trên **Netlify Dashboard**:
   - Click **Add new site** → **Deploy manually**
   - Kéo thả thư mục `webapp/dist` vào vùng deploy
   - Netlify sẽ tự động deploy

3. **Cấu hình Environment Variables** (nếu cần rebuild):
   - Site settings → **Environment variables**
   - Thêm `VITE_API_BASE_URL=https://dichotienloi123.duckdns.org`

---

### Bước 4: Cấu hình Custom Domain (Tùy chọn)

#### 4.1. Thêm Custom Domain trên Netlify

1. Trong **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Nhập domain (ví dụ: `app.dichotienloi123.duckdns.org`)
4. Làm theo hướng dẫn để cấu hình DNS

#### 4.2. Cấu hình DNS trên DuckDNS

1. Truy cập https://www.duckdns.org/
2. Thêm subdomain mới (ví dụ: `app`)
3. Trong phần **IPv4**, nhập địa chỉ IP mà Netlify cung cấp (hoặc CNAME nếu Netlify yêu cầu)

---

### Bước 5: Cấu hình CORS trên Backend

Đảm bảo Kong Gateway cho phép CORS từ domain Netlify:

1. Kiểm tra file `api-gateway/kong.prod.yml`
2. Tìm phần `cors` plugin:
   ```yaml
   - name: cors
     config:
       origins:
         - "*"  # Hoặc thêm domain Netlify cụ thể
   ```

3. Nếu muốn giới hạn, thay `"*"` bằng:
   ```yaml
   origins:
     - "https://convenient-shopping-webapp.netlify.app"
     - "https://dichotienloi123.duckdns.org"
   ```

4. Rebuild và restart Kong:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build kong-gateway
   ```

---

### Bước 6: Kiểm tra Frontend

1. Truy cập URL Netlify (ví dụ: `https://convenient-shopping-webapp.netlify.app`)
2. Mở **Developer Tools** (F12) → **Console**
3. Kiểm tra:
   - Không có lỗi CORS
   - API calls thành công
   - WebSocket kết nối được (nếu có)

---

## PHẦN 3: BẢO TRÌ VÀ MONITORING

### 3.1. Xem Logs

```bash
# Tất cả services
docker compose -f docker-compose.prod.yml logs -f

# Service cụ thể
docker compose -f docker-compose.prod.yml logs -f user-service
docker compose -f docker-compose.prod.yml logs -f kong-gateway
```

### 3.2. Restart Services

```bash
# Restart tất cả
docker compose -f docker-compose.prod.yml restart

# Restart service cụ thể
docker compose -f docker-compose.prod.yml restart user-service
```

### 3.3. Update Code

```bash
cd ~/IT4990-Convenient-Shopping-System
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```

### 3.4. Backup Database

```bash
# Tạo backup
pg_dump -h <RDS_ENDPOINT> -U postgres -d postgres > backup_$(date +%Y%m%d).sql

# Restore
psql -h <RDS_ENDPOINT> -U postgres -d postgres < backup_20240101.sql
```

### 3.5. Monitor Resources

```bash
# Xem sử dụng tài nguyên
docker stats

# Xem disk usage
df -h

# Xem memory
free -h
```

---

## PHẦN 4: TROUBLESHOOTING

### Lỗi: Cannot connect to RDS

**Nguyên nhân**: Security Group chưa cho phép EC2 kết nối.

**Giải pháp**:
1. Vào RDS Security Group
2. Thêm inbound rule cho PostgreSQL (5432) từ EC2 Security Group

### Lỗi: SSL Certificate expired

**Nguyên nhân**: Certbot không tự động renew.

**Giải pháp**:
```bash
docker compose -f docker-compose.prod.yml exec certbot certbot renew --force-renewal
docker compose -f docker-compose.prod.yml restart kong-gateway
```

### Lỗi: Port 80/443 already in use

**Nguyên nhân**: Service khác đang dùng port.

**Giải pháp**:
```bash
sudo lsof -i :80
sudo lsof -i :443
# Kill process nếu cần
```

### Lỗi: CORS trên Frontend

**Nguyên nhân**: Kong Gateway chưa cấu hình CORS đúng.

**Giải pháp**:
1. Kiểm tra `kong.prod.yml` → CORS plugin
2. Thêm domain Netlify vào `origins`
3. Restart Kong Gateway

### Lỗi: WebSocket không kết nối

**Nguyên nhân**: Kong Gateway chưa hỗ trợ WebSocket đúng cách.

**Giải pháp**:
1. Kiểm tra route WebSocket trong `kong.prod.yml`
2. Đảm bảo có `protocols: [http, https]`
3. Kiểm tra timeout settings

---

## TÓM TẮT CÁC BƯỚC QUAN TRỌNG

### Backend (AWS EC2):
1. ✅ Tạo EC2 Instance (t2.medium+)
2. ✅ Cấp Elastic IP
3. ✅ Cấu hình DNS DuckDNS
4. ✅ Tạo RDS PostgreSQL
5. ✅ Cài Docker & Docker Compose
6. ✅ Lấy SSL Certificate
7. ✅ Clone code và cấu hình .env
8. ✅ Build và khởi động services
9. ✅ Chạy migrations
10. ✅ Kiểm tra health checks

### Frontend (Netlify):
1. ✅ Cấu hình VITE_API_BASE_URL
2. ✅ Build production
3. ✅ Deploy lên Netlify (CLI/GitHub/Manual)
4. ✅ Cấu hình Environment Variables
5. ✅ Kiểm tra CORS và WebSocket

---

## LIÊN HỆ VÀ HỖ TRỢ

Nếu gặp vấn đề, kiểm tra:
- Logs của các services
- Security Groups trên AWS
- DNS propagation
- SSL certificate status
- Network connectivity

**Chúc bạn deploy thành công! 🚀**

