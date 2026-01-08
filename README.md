# IT4990 - Convenient Shopping System
> Outline a brief description of your project.
> Live demo [_here_](https://www.example.com). <!-- If you have the project hosted somewhere, include the link here. -->

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)
<!-- * [License](#license) -->


## General Information
- Provide general information about your project here.
- What problem does it (intend to) solve?
- What is the purpose of your project?
- Why did you undertake it?
<!-- You don't have to answer all the questions - just the ones relevant to your project. -->


## Technologies Used
- Tech 1 - version 1.0
- Tech 2 - version 2.0
- Tech 3 - version 3.0


## Features
List the ready features here:
- Awesome feature 1
- Awesome feature 2
- Awesome feature 3


## Screenshots
![Example screenshot](./img/screenshot.png)
<!-- If you have screenshots you'd like to share, include them here. -->


## Usage
How does one go about using it?
Provide various use cases and code examples here.

```bash
docker compose -f docker-compose.dev.yml up -d
```

### Simulate Production Environment Locally
To test the production setup (with SSL, Kong Gateway, and Domain routing) on your local machine (Mac/Linux), follow these steps:

**1. Create Dummy SSL Certificates**
Create the system directory structure and generate self-signed certificates.
```bash
# Create directory (requires sudo)
sudo mkdir -p /etc/letsencrypt/live/dichotienloi.com/

# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/letsencrypt/live/dichotienloi.com/privkey.pem \
  -out /etc/letsencrypt/live/dichotienloi.com/fullchain.pem \
  -subj "/CN=dichotienloi.com"
```

**2. Copy Certificates to Project Folder (Fix Permission Issues)**
Docker on MacOS has trouble mounting system folders like `/etc`. We copy certs to a local `./certs` folder.
```bash
# Create local certs folder
mkdir -p certs

# Copy certs and change ownership to current user
sudo cp /etc/letsencrypt/live/dichotienloi.com/fullchain.pem ./certs/
sudo cp /etc/letsencrypt/live/dichotienloi.com/privkey.pem ./certs/
sudo chown $USER ./certs/*.pem
```

**3. Mock Domain Name**
Trick your computer into thinking `dichotienloi.com` is your localhost.
```bash
# Open hosts file
sudo nano /etc/hosts

# Add this line at the end:
127.0.0.1 dichotienloi.com

# Check after mock domain name
# Option 1: Check file hosts content
cat /etc/hosts | grep dichotienloi.com

# Option 2: Check by ping command
ping -c 3 dichotienloi.com
```

**4. Configure Environment Variables**
Create a `.env` file from the example if you haven't already.
```bash
cp .env.example .env
```

**5. Run Production Compose**
```bash
docker compose -f docker-compose.prod.yml up -d
```

**6. Verify**
Open your browser and visit: `https://dichotienloi.com`
*   You will see a "Security Warning" (because it's a self-signed cert). Click "Advanced" -> "Proceed".
*   If you see the API response or Kong welcome page, SSL Termination is working correctly!

> **Note:** The `certbot` service will fail in logs because it cannot connect to Let's Encrypt from localhost. This is expected and can be ignored during local testing.


# Check after create certificate
sudo ls -l /etc/letsencrypt/live/dichotienloi.com/
```
