# 🚀 AWS EC2 Deployment Guide: Convenient Shopping System

This document provides a comprehensive, step-by-step guide to deploying the **Convenient Shopping System** on AWS EC2. It covers infrastructure setup, server configuration, SSL automation, and application deployment.

## 🏗 Architecture Overview

We use a **Zero-Downtime SSL Renewal** architecture using the "Challenge Routing" pattern.

```text
User (HTTPS) --> [ AWS EC2 (Elastic IP) ] --> [ Kong Gateway (Port 8443) ] --> [ Microservices ]
User (HTTP)  --> [ AWS EC2 (Elastic IP) ] --> [ Kong Gateway (Port 80) ]
                                                      |
                                                      | (/.well-known/acme-challenge/*)
                                                      v
                                              [ ACME Challenge Service ] <--- [ Certbot Auto-Renew ]
```

- **Kong Gateway**: Handles all incoming traffic, SSL termination, and routing.
- **Certbot**: Automatically renews SSL certificates (Let's Encrypt) and shares them with Kong.
- **ACME Challenge**: A lightweight Nginx service dedicated to solving Let's Encrypt HTTP-01 challenges.
- **Microservices**: Running in Docker containers, accessible only via the Gateway.

## 📋 Phase 1: AWS Infrastructure Preparation

### 1.1. Database (AWS RDS) - **Required**
The `docker-compose.prod.yml` **does not** include a PostgreSQL container. You must provide an external database.
*   **Service**: AWS RDS for PostgreSQL.
*   **Version**: PostgreSQL 16 (or compatible).
*   **Network**: Ensure it is in the same VPC as your EC2 instance or publicly accessible (less secure).
*   **Security Group**: Allow Inbound traffic on port `5432` from your EC2 Instance's Private IP (or Security Group ID).
*   **Credentials to save**:
    *   Endpoint (Host)
    *   Username (e.g., `postgres`)
    *   Password
    *   Database Name (e.g., `shopping_db`)

### 1.2. EC2 Instance
*   **OS**: Ubuntu 24.04 LTS (Recommended) or 22.04 LTS.
*   **Instance Type**: `t3.medium` or `t3.large` (Required for Java/Kafka/Elasticsearch workloads). `t2.micro` is **not** sufficient.
*   **Storage**: At least 20GB gp3 root volume.

### 1.3. Elastic IP (Static IP)
*   Allocate an **Elastic IP** in the AWS Console.
*   Associate it with your EC2 instance. This ensures your IP doesn't change on reboot.

### 1.4. DNS Configuration
*   Go to your DNS Provider (GoDaddy, Namecheap, Route53, etc.).
*   Create an **A Record** for your domain (e.g., `dichotienloi.com`) pointing to the **Elastic IP**.
*   (Optional) Create a CNAME or A Record for `www.dichotienloi.com` pointing to the same IP.

### 1.5. Security Group (Firewall)
Configure the Inbound Rules for your EC2 instance:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | My IP | Restrict to your personal IP for security |
| HTTP | TCP | 80 | 0.0.0.0/0 | For ACME Challenge & HTTP->HTTPS Redirect |
| HTTPS| TCP | 443 | 0.0.0.0/0 | Main API Traffic |


## 🛠 Phase 2: Server Setup & Configuration

Connect to your server via SSH.

### 2.1. Connect via SSH

**For MacOS / Linux:**
```bash
chmod 400 path/to/your-key.pem
ssh -i path/to/your-key.pem ubuntu@<YOUR_ELASTIC_IP>
```

**For Windows (PowerShell):**
```powershell
# Ensure you have read-only access to the key file
ssh -i path\to\your-key.pem ubuntu@<YOUR_ELASTIC_IP>
```

### 2.2. Create Swap File (Crucial for Stability)
Services like Kafka and Java apps can consume significant RAM. A swap file prevents "Out of Memory" crashes.

```bash
# 1. Allocate 2GB swap file
sudo fallocate -l 2G /swapfile

# 2. Set permissions
sudo chmod 600 /swapfile

# 3. Mark as swap space
sudo mkswap /swapfile

# 4. Enable swap
sudo swapon /swapfile

# 5. Make permanent (add to fstab)
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 6. Verify
free -h
```

### 2.3. Install Docker & Docker Compose

```bash
# 1. Add Docker's official GPG key (Digital signature to verify software authenticity):
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources (so we can install the official Docker version):
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages:
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Grant Docker permission to current user (avoids sudo)
sudo usermod -aG docker $USER

# Apply group changes immediately
newgrp docker
```

## 🔐 Phase 3: SSL Bootstrap (First Time Only)

**Why do we need this step?**
There is a "Chicken and Egg" problem:
1.  **Kong Gateway** needs the certificate files to exist *before* it can start. If they are missing, Kong crashes.
2.  The **Certbot container** (inside Docker) relies on Kong to route the verification traffic.
3.  **Solution:** We use `certbot` on the Host machine *once* to generate the initial certificates. This allows Kong to start up successfully. Afterward, the internal Certbot container takes over for automatic renewals.

```bash
# 1. Install Certbot on Host
sudo apt-get update && sudo apt-get install -y certbot

# 2. Generate Certificate (Replace 'dichotienloi.duckdns.org' with your domain)
# This spins up a temporary web server on port 80 to validate ownership.
sudo certbot certonly --standalone -d dichotienloi.duckdns.org

# 3. Verify certificates exist
sudo ls -l /etc/letsencrypt/live/dichotienloi.duckdns.org/
```
*Note: Make sure to replace `dichotienloi.duckdns.org` with your actual domain throughout this guide.*


## 🚀 Phase 4: Application Deployment

### 4.1. Clone Repository
```bash
git clone https://github.com/your-username/convenient-shopping-system.git
cd convenient-shopping-system
```

### 4.2. Configure Environment Variables
Create the production `.env` file.

```bash
cp .env.example .env
nano .env
```

**Critical Variables to Update in `.env`:**
```ini
# Database (RDS Info)
DB_HOST=your-rds-endpoint.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Kong Configuration
KONG_CONFIG_FILE=./api-gateway/kong.prod.yml

# SSL Paths (Must match the domain you registered)
SSL_CERT_FILE=/etc/letsencrypt/live/dichotienloi.com/fullchain.pem
SSL_KEY_FILE=/etc/letsencrypt/live/dichotienloi.com/privkey.pem

# Security (Generate strong keys!)
JWT_RSA_PRIVATE_KEY="...paste your private key..."
JWT_RSA_PUBLIC_KEY="...paste your public key..."
```
*Tip: You can generate the RSA keys locally using `python3 scripts/generate_rsa_keys.py` inside the `user-service` folder and copy them here.*

### 4.3. Update Docker Compose Volumes
Open `docker-compose.prod.yml` and ensure the volume mapping for `certbot` and `kong-gateway` matches your domain.

```bash
nano docker-compose.prod.yml
```
*Usually, if you use the `SSL_CERT_FILE` variable in `.env` correctly as shown above, you don't need to edit the compose file. The compose file uses `${SSL_CERT_FILE}`.*

### 4.4. Start the Application
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 4.5. Verification
1.  **Check Containers**: `docker compose -f docker-compose.prod.yml ps` (All should be `Up`).
2.  **Check Logs**: `docker compose -f docker-compose.prod.yml logs -f` (Look for errors).
3.  **Public Access**: Open `https://dichotienloi.com`. You should see the API response or 404 from Kong (but with a valid Lock icon 🔒).
4.  **ACME Challenge**: Visit `http://dichotienloi.com/.well-known/acme-challenge/test`. It should be handled by Nginx (likely 404 if file doesn't exist, but NOT a connection error).


## 🔄 Phase 5: Maintenance & Monitoring

### Automatic SSL Renewal
The `certbot` container is configured to check for renewal every 12 hours.
- If a certificate is within 30 days of expiry, it renews it.
- It saves the new cert to `/etc/letsencrypt/live/...`.
- Since Kong mounts these files as volumes, you **must reload Kong** to pick up the new certificate (unless you implement a script to trigger it).

**Manual Renewal Test:**
```bash
docker compose -f docker-compose.prod.yml exec certbot certbot renew --force-renewal
docker compose -f docker-compose.prod.yml restart kong-gateway
```

### Updating the App
To deploy new code:
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build <service_name>
# Example: docker compose -f docker-compose.prod.yml up -d --build user-service
```
