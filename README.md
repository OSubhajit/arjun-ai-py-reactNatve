"# GitaPath - Arjun AI

### A Spiritual AI Mobile App based on Bhagavad Gita

GitaPath is a cross-platform mobile app (Android + iOS + Web) powered by AI that lets users chat with characters from the Mahabharata — Arjun, Krishna, Bhima, and more. Built with React Native (Expo), FastAPI, and MongoDB.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Step 1 — Install Prerequisites](#step-1--install-prerequisites)
6. [Step 2 — Clone / Download the Project](#step-2--clone--download-the-project)
7. [Step 3 — Setup MongoDB Database](#step-3--setup-mongodb-database)
8. [Step 4 — Setup Backend (FastAPI)](#step-4--setup-backend-fastapi)
9. [Step 5 — Setup Frontend (Expo Mobile App)](#step-5--setup-frontend-expo-mobile-app)
10. [Step 6 — Setup Admin Dashboard](#step-6--setup-admin-dashboard)
11. [Step 7 — Create Admin Account](#step-7--create-admin-account)
12. [Step 8 — Test the App](#step-8--test-the-app)
13. [Step 9 — Build APK / IPA for Production](#step-9--build-apk--ipa-for-production)
14. [Step 10 — Deploy Backend to Production](#step-10--deploy-backend-to-production)
15. [Step 11 — Publish to Play Store / App Store](#step-11--publish-to-play-store--app-store)
16. [Step 12 — Push Code to GitHub](#step-12--push-code-to-github)
17. [Environment Variables Reference](#environment-variables-reference)
18. [API Endpoints Reference](#api-endpoints-reference)
19. [Database Schema](#database-schema)
20. [Troubleshooting](#troubleshooting)
21. [License](#license)

---

## Features

- **AI Chat** — Talk to Arjun (and premium characters: Krishna, Bhima, Draupadi, Karna) powered by GPT-5.2
- **5 Chat Modes** — General, Meditation, Decision Making, Heartbreak, Study
- **Emotion Detection** — AI senses your mood and adapts responses
- **Daily Shloka** — Get a new Bhagavad Gita verse every day
- **Voice Input/Output** — Speak to AI and listen to responses
- **JWT Authentication** — Register, Login, Forgot Password with OTP
- **Premium Subscription** — Manual UPI payment with admin verification
- **Chat History** — View, revisit, and delete past conversations
- **Admin Dashboard** — Manage users, chats, payments, feedback, analytics
- **Dark Spiritual UI** — Beautiful dark theme with saffron/gold accents

---

## Tech Stack

| Component         | Technology                          |
|-------------------|-------------------------------------|
| Mobile App        | React Native (Expo SDK 54)          |
| Navigation        | Expo Router (file-based routing)    |
| Backend API       | FastAPI (Python 3.10+)              |
| Database          | MongoDB (with Motor async driver)   |
| AI/LLM            | OpenAI GPT-5.2 via EmergentIntegrations |
| Authentication    | JWT (JSON Web Tokens)               |
| Admin Dashboard   | FastAPI + Vanilla HTML/JS/Tailwind  |
| State Management  | Zustand + React Context             |
| Animations        | React Native Reanimated             |

---

## Project Structure

```
gitapath-app/
├── backend/                    # FastAPI Main Backend
│   ├── server.py               # Main API server (runs on port 8001)
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Backend environment variables
│
├── frontend/                   # Expo React Native Mobile App
│   ├── app/                    # File-based routing (screens)
│   │   ├── (auth)/             # Auth screens
│   │   │   ├── login.tsx       # Login screen
│   │   │   ├── register.tsx    # Registration screen
│   │   │   └── forgot-password.tsx
│   │   ├── (tabs)/             # Main tab screens
│   │   │   ├── _layout.tsx     # Tab navigator layout
│   │   │   ├── chat.tsx        # AI Chat screen
│   │   │   ├── history.tsx     # Chat history screen
│   │   │   ├── profile.tsx     # User profile screen
│   │   │   └── settings.tsx    # Settings screen
│   │   ├── _layout.tsx         # Root layout (Stack navigator)
│   │   ├── index.tsx           # Welcome/splash screen
│   │   └── premium.tsx         # Premium subscription screen
│   ├── contexts/
│   │   └── AuthContext.tsx      # Authentication state management
│   ├── constants/
│   │   └── theme.ts            # App colors, fonts, spacing
│   ├── assets/                 # Images, fonts
│   ├── app.json                # Expo configuration
│   ├── package.json            # Node dependencies
│   └── .env                    # Frontend environment variables
│
├── admin-dashboard/            # Admin Dashboard
│   ├── backend/
│   │   ├── main.py             # Admin API server (runs on port 8002)
│   │   ├── seed_admin.py       # Script to create first admin user
│   │   ├── update_admin.py     # Script to update admin credentials
│   │   └── .env                # Admin backend environment variables
│   └── frontend/
│       └── index.html          # Admin Dashboard UI
│
└── README.md                   # This file
```

---

## Prerequisites

Before you begin, make sure you have these installed on your computer:

| Tool          | Version     | Download Link                                    |
|---------------|-------------|--------------------------------------------------|
| **Node.js**   | 18+ or 20+  | https://nodejs.org/en/download                  |
| **Python**    | 3.10+       | https://www.python.org/downloads                |
| **MongoDB**   | 6.0+        | https://www.mongodb.com/try/download/community  |
| **Git**       | Latest      | https://git-scm.com/downloads                   |
| **Yarn**      | 1.22+       | `npm install -g yarn` (after installing Node)    |
| **Expo CLI**  | Latest      | `npm install -g expo-cli` (after installing Node)|

### For Mobile Testing:
- **Android**: Install [Expo Go](https://play.google.com/store/apps/details?id=host.exp.exponent) on your Android phone
- **iOS**: Install [Expo Go](https://apps.apple.com/app/expo-go/id982107779) on your iPhone
- **Emulator**: Android Studio (for Android Emulator) or Xcode (for iOS Simulator, Mac only)

---

## Step 1 — Install Prerequisites

### On Windows:

```bash
# 1. Install Node.js — Download from https://nodejs.org (LTS version)
# After installation, open Command Prompt and verify:
node --version
npm --version

# 2. Install Yarn
npm install -g yarn

# 3. Install Expo CLI
npm install -g expo-cli

# 4. Install Python — Download from https://python.org
# IMPORTANT: Check \"Add Python to PATH\" during installation
# Verify:
python --version
pip --version

# 5. Install MongoDB
# Download MongoDB Community Server from https://www.mongodb.com/try/download/community
# Choose \"Complete\" installation
# Check \"Install MongoDB as a Service\" during setup
# Verify MongoDB is running:
mongosh
# Type 'exit' to leave mongosh

# 6. Install Git — Download from https://git-scm.com/downloads
git --version
```

### On macOS:

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"

# 2. Install Node.js
brew install node

# 3. Install Yarn & Expo CLI
npm install -g yarn expo-cli

# 4. Install Python
brew install python@3.12

# 5. Install MongoDB
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# 6. Git is pre-installed on macOS. Verify:
git --version
```

### On Linux (Ubuntu/Debian):

```bash
# 1. Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Install Yarn & Expo CLI
npm install -g yarn expo-cli

# 3. Install Python
sudo apt-get install -y python3 python3-pip python3-venv

# 4. Install MongoDB
# Follow: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
sudo apt-get install -y gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo \"deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse\" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# 5. Git
sudo apt-get install -y git
```

---

## Step 2 — Clone / Download the Project

### Option A: If you have the ZIP file

```bash
# 1. Extract the ZIP file to a folder
# Windows: Right-click → Extract All
# macOS/Linux:
unzip gitapath-app-clean.zip

# 2. Navigate into the project
cd app
```

### Option B: If it's on GitHub

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gitapath-arjun-ai.git
cd gitapath-arjun-ai
```

---

## Step 3 — Setup MongoDB Database

### Verify MongoDB is Running

```bash
# Check if MongoDB service is running
# Windows (PowerShell):
Get-Service MongoDB

# macOS:
brew services list | grep mongodb

# Linux:
sudo systemctl status mongod
```

### Start MongoDB (if not running)

```bash
# Windows: Open Services app → Find \"MongoDB Server\" → Start
# macOS:
brew services start mongodb-community@7.0

# Linux:
sudo systemctl start mongod
```

### Connect and Verify

```bash
# Open MongoDB shell
mongosh

# You should see a connection message. Then type:
show dbs

# Exit
exit
```

MongoDB should now be running on `mongodb://localhost:27017`.

---

## Step 4 — Setup Backend (FastAPI)

### 4.1 Navigate to Backend Folder

```bash
cd backend
```

### 4.2 Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it:
# Windows (Command Prompt):
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

# You should see (venv) at the beginning of your terminal prompt
```

### 4.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If you get errors with `bcrypt` or `cryptography`, try:
> ```bash
> pip install --upgrade pip setuptools wheel
> pip install -r requirements.txt
> ```

### 4.4 Configure Environment Variables

Create/edit the `.env` file inside the `backend/` folder:

```bash
# backend/.env
MONGO_URL=\"mongodb://localhost:27017\"
DB_NAME=\"gitapath_database\"
JWT_SECRET=\"your-super-secret-key-change-this-to-random-string\"
JWT_ALGORITHM=\"HS256\"
ACCESS_TOKEN_EXPIRE_MINUTES=10080
EMERGENT_LLM_KEY=\"YOUR_EMERGENT_LLM_KEY_HERE\"
```

#### How to get EMERGENT_LLM_KEY:
1. Go to [Emergent](https://emergentagent.com)
2. Sign in to your account
3. Click your **Profile Icon** (top right)
4. Go to **Universal Key**
5. Copy the key and paste it in `.env`

> **IMPORTANT:** The `EMERGENT_LLM_KEY` is required for the AI chat to work. Without it, the chatbot will return error messages.

### 4.5 Start the Backend Server

```bash
# Make sure you're in the backend/ folder with venv activated
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

### 4.6 Verify Backend is Running

Open a **new terminal** and run:

```bash
curl http://localhost:8001/api/health
```

Expected response:
```json
{\"status\":\"healthy\",\"service\":\"Arjun AI API\"}
```

> **Keep this terminal running** — the backend server must stay active.

---

## Step 5 — Setup Frontend (Expo Mobile App)

### 5.1 Navigate to Frontend Folder

Open a **new terminal window** (keep backend running):

```bash
cd frontend
```

### 5.2 Install Node Dependencies

```bash
yarn install
```

> This will take 2-5 minutes. It downloads all the required packages.

### 5.3 Configure Environment Variables

Create/edit the `.env` file inside the `frontend/` folder:

```bash
# frontend/.env
EXPO_PUBLIC_BACKEND_URL=\"http://YOUR_LOCAL_IP:8001\"
```

#### Find your local IP address:

```bash
# Windows:
ipconfig
# Look for \"IPv4 Address\" under your active network (e.g., 192.168.1.5)

# macOS:
ifconfig | grep \"inet \" | grep -v 127.0.0.1
# Look for something like 192.168.x.x

# Linux:
hostname -I
```

**Example:** If your IP is `192.168.1.5`, set:
```
EXPO_PUBLIC_BACKEND_URL=\"http://192.168.1.5:8001\"
```

> **Why local IP?** Your phone needs to reach your computer's backend server. `localhost` won't work from a phone — it needs your actual network IP.
>
> **For web testing only**, you can use `http://localhost:8001`.

### 5.4 Start the Expo Development Server

```bash
npx expo start
```

You will see:
```
Starting Metro Bundler
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█ ▄▄▄▄▄ █ █ ▄ ▀█ ▄▄▄▄ █
█ █   █ █▄▀ ▀▄▀█ █   █ █
...
█▄▄▄▄▄▄▄█▄▄▄▄█▄▄▄▄▄▄▄█

› Metro waiting on exp://192.168.x.x:8081

› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web
```

### 5.5 Run the App

**On your Phone (Recommended):**
1. Make sure your phone and computer are on the **same WiFi network**
2. Open **Expo Go** app on your phone
3. Scan the **QR code** shown in the terminal
4. The app will load on your phone!

**On Web Browser:**
- Press `w` in the terminal → Opens at `http://localhost:8081`

**On Android Emulator:**
1. Open Android Studio → Device Manager → Start an emulator
2. Press `a` in the Expo terminal

**On iOS Simulator (Mac only):**
1. Open Xcode → Simulator
2. Press `i` in the Expo terminal

---

## Step 6 — Setup Admin Dashboard

### 6.1 Admin Backend

Open a **new terminal** (keep other servers running):

```bash
cd admin-dashboard/backend
```

Create/edit the `.env` file:

```bash
# admin-dashboard/backend/.env
MONGO_URL=\"mongodb://localhost:27017\"
DB_NAME=\"gitapath_database\"
ADMIN_JWT_SECRET=\"your-admin-secret-key-change-this\"
```

> **IMPORTANT:** The `DB_NAME` must be the SAME as the main backend `.env` so they share the same database.

Install dependencies (if not already in a venv):

```bash
# Create new venv or use the backend one
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install fastapi motor pydantic python-jose passlib[bcrypt] python-dotenv uvicorn
```

Start the admin backend:

```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### 6.2 Admin Frontend (Dashboard UI)

Open another terminal:

```bash
cd admin-dashboard/frontend
```

Serve the HTML file:

```bash
# Python simple HTTP server
python3 -m http.server 8003
```

Now open `http://localhost:8003` in your browser to access the Admin Dashboard.

---

## Step 7 — Create Admin Account

### 7.1 Run the Admin Seed Script

```bash
cd admin-dashboard/backend

# Activate virtual environment if not already
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the seed script
python seed_admin.py
```

This creates a default admin account. Check the script for default credentials.

### 7.2 Update Admin Credentials (Optional)

Edit `admin-dashboard/backend/update_admin.py` with your desired username and password, then run:

```bash
python update_admin.py
```

### 7.3 Login to Admin Dashboard

1. Open `http://localhost:8003` in your browser
2. Enter your admin username and password
3. You now have access to:
   - User management
   - Chat monitoring
   - Payment approvals/rejections
   - Analytics
   - AI configuration
   - Feedback review

---

## Step 8 — Test the App

### 8.1 Register a New User

1. Open the app (phone or web)
2. Tap \"Begin Your Journey\" on the welcome screen
3. Tap \"Create Account\"
4. Enter name, email, and password
5. You should be redirected to the main chat screen

### 8.2 Test AI Chat

1. Go to the Chat tab
2. Type \"What is dharma?\" and send
3. Arjun should respond with spiritual guidance
4. Try different modes: Meditation, Decision, Heartbreak, Study

### 8.3 Test Premium Subscription

1. Go to Profile tab
2. Tap \"Upgrade to Premium\" or navigate to Premium screen
3. Select a plan → Enter a UPI Transaction ID
4. Submit → Payment goes to \"Pending\"
5. In Admin Dashboard → Payments tab → Approve the payment
6. User is now Premium and can access all characters

### 8.4 Test Admin Dashboard

1. Open `http://localhost:8003`
2. Login with admin credentials
3. Check: Users list, Chat history, Analytics, Feedback, Payments

---

## Step 9 — Build APK / IPA for Production

### 9.1 Install EAS CLI (Expo Application Services)

```bash
npm install -g eas-cli
```

### 9.2 Login to Expo

```bash
# Create an account at https://expo.dev if you don't have one
eas login
```

### 9.3 Configure EAS Build

```bash
cd frontend
eas build:configure
```

This creates an `eas.json` file. Modify it:

```json
{
  \"cli\": {
    \"version\": \">= 15.0.0\"
  },
  \"build\": {
    \"development\": {
      \"developmentClient\": true,
      \"distribution\": \"internal\"
    },
    \"preview\": {
      \"distribution\": \"internal\",
      \"android\": {
        \"buildType\": \"apk\"
      }
    },
    \"production\": {
      \"android\": {
        \"buildType\": \"app-bundle\"
      },
      \"ios\": {
        \"buildConfiguration\": \"Release\"
      }
    }
  },
  \"submit\": {
    \"production\": {}
  }
}
```

### 9.4 Update app.json for Production

Before building, update `frontend/app.json`:

```json
{
  \"expo\": {
    \"name\": \"GitaPath - Arjun AI\",
    \"slug\": \"gitapath-arjun-ai\",
    \"version\": \"1.0.0\",
    \"ios\": {
      \"bundleIdentifier\": \"com.yourcompany.gitapath\",
      \"buildNumber\": \"1\"
    },
    \"android\": {
      \"package\": \"com.yourcompany.gitapath\",
      \"versionCode\": 1
    }
  }
}
```

> **IMPORTANT:** Change `com.yourcompany.gitapath` to your own unique package name.

### 9.5 Update Frontend .env for Production

```bash
# frontend/.env — Change to your deployed backend URL
EXPO_PUBLIC_BACKEND_URL=\"https://your-deployed-backend.com\"
```

### 9.6 Build Android APK (for testing)

```bash
cd frontend
eas build --platform android --profile preview
```

- This builds an APK file in the cloud (takes 10-20 minutes)
- After build completes, you'll get a **download link** for the APK
- Download and install on any Android phone

### 9.7 Build Android App Bundle (for Play Store)

```bash
eas build --platform android --profile production
```

- Generates an `.aab` file (required for Play Store)
- Download from the link provided after build

### 9.8 Build iOS IPA (requires Mac + Apple Developer Account)

```bash
eas build --platform ios --profile production
```

- You need an [Apple Developer Account](https://developer.apple.com) ($99/year)
- EAS handles code signing automatically
- Generates `.ipa` file for App Store

---

## Step 10 — Deploy Backend to Production

### Option A: Deploy on Railway (Easiest)

1. Go to [Railway.app](https://railway.app)
2. Create a new project
3. Add a **MongoDB** service (or use MongoDB Atlas)
4. Add a **Python** service:
   - Connect your GitHub repo
   - Set root directory to `backend`
   - Set start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Railway dashboard:
   ```
   MONGO_URL=mongodb+srv://your-atlas-url
   DB_NAME=gitapath_database
   JWT_SECRET=your-secret-key
   EMERGENT_LLM_KEY=your-key
   ```
6. Railway gives you a public URL like `https://gitapath-backend.up.railway.app`

### Option B: Deploy on Render

1. Go to [Render.com](https://render.com)
2. Create a new **Web Service**
3. Connect your GitHub repo
4. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as above)

### Option C: Deploy on AWS/GCP/DigitalOcean (Advanced)

```bash
# On your server:
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx

# Clone your repo
git clone https://github.com/YOUR_USERNAME/gitapath-arjun-ai.git
cd gitapath-arjun-ai/backend

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with gunicorn for production
pip install gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Setup Nginx reverse proxy (optional but recommended)
# Setup SSL with Let's Encrypt (required for mobile apps)
```

### MongoDB Atlas (Cloud Database — Recommended for Production)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user with password
4. Whitelist your server IP (or 0.0.0.0/0 for all)
5. Get the connection string: `mongodb+srv://username:password@cluster.mongodb.net/gitapath_database`
6. Update your `MONGO_URL` environment variable

---

## Step 11 — Publish to Play Store / App Store

### Google Play Store

1. Create a [Google Play Developer Account](https://play.google.com/console) ($25 one-time)
2. Create a new app in Play Console
3. Upload the `.aab` file (from Step 9.7)
4. Fill in:
   - App name: \"GitaPath - Arjun AI\"
   - Short description: \"Chat with Arjun from Bhagavad Gita\"
   - Full description
   - Screenshots (phone + tablet)
   - App icon (512x512)
   - Feature graphic (1024x500)
   - Privacy policy URL
   - Content rating questionnaire
5. Set pricing: Free (with in-app premium)
6. Submit for review (takes 1-7 days)

### Apple App Store

1. Create an [Apple Developer Account](https://developer.apple.com) ($99/year)
2. Open [App Store Connect](https://appstoreconnect.apple.com)
3. Create a new app
4. Upload using EAS Submit:
   ```bash
   eas submit --platform ios
   ```
5. Fill in app metadata, screenshots, description
6. Submit for review (takes 1-3 days)

---

## Step 12 — Push Code to GitHub

### 12.1 Create a GitHub Repository

1. Go to [github.com](https://github.com) → Sign in
2. Click **\"+\"** → **New Repository**
3. Name: `gitapath-arjun-ai`
4. Keep it **Private** (recommended for now)
5. Don't initialize with README (we already have one)
6. Click **Create Repository**

### 12.2 Initialize Git and Push

```bash
# Navigate to the project root folder
cd app  # or wherever your project is

# Initialize git
git init

# Create .gitignore file
cat > .gitignore << 'EOF'
# Node
node_modules/
.expo/
.metro-cache/
dist/
web-build/

# Python
__pycache__/
*.pyc
venv/
.venv/

# Environment variables (IMPORTANT — never push these!)
.env
backend/.env
frontend/.env
admin-dashboard/backend/.env

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Build
*.apk
*.aab
*.ipa

# Test files
test_result.md
backend_test.py
test_reports/
EOF

# Add all files
git add .

# Create first commit
git commit -m \"Initial commit: GitaPath Arjun AI - Full Stack Mobile App\"

# Connect to GitHub (replace with YOUR repository URL)
git remote add origin https://github.com/YOUR_USERNAME/gitapath-arjun-ai.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 12.3 Verify on GitHub

1. Go to `https://github.com/YOUR_USERNAME/gitapath-arjun-ai`
2. You should see all your files uploaded
3. Make sure `.env` files are NOT visible (gitignore should hide them)

### 12.4 Future Updates

```bash
# After making changes:
git add .
git commit -m \"Description of changes\"
git push
```

---

## Environment Variables Reference

### backend/.env

| Variable                      | Description                        | Required |
|-------------------------------|------------------------------------|----------|
| `MONGO_URL`                   | MongoDB connection string          | Yes      |
| `DB_NAME`                     | Database name                      | Yes      |
| `JWT_SECRET`                  | Secret key for JWT token signing   | Yes      |
| `JWT_ALGORITHM`               | JWT algorithm (use HS256)          | Yes      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: 10080 = 7 days) | Yes  |
| `EMERGENT_LLM_KEY`           | AI API key from Emergent platform  | Yes      |

### frontend/.env

| Variable                     | Description                        | Required |
|------------------------------|------------------------------------|----------|
| `EXPO_PUBLIC_BACKEND_URL`    | Backend server URL                 | Yes      |

### admin-dashboard/backend/.env

| Variable            | Description                        | Required |
|---------------------|------------------------------------|----------|
| `MONGO_URL`         | MongoDB connection string (same DB)| Yes      |
| `DB_NAME`           | Database name (must match backend) | Yes      |
| `ADMIN_JWT_SECRET`  | Separate JWT secret for admin auth | Yes      |

---

## API Endpoints Reference

### Main Backend (Port 8001)

| Method | Endpoint                        | Description                  | Auth Required |
|--------|---------------------------------|------------------------------|---------------|
| GET    | `/api/health`                   | Health check                 | No            |
| POST   | `/api/auth/register`            | Register new user            | No            |
| POST   | `/api/auth/login`               | Login user                   | No            |
| POST   | `/api/auth/forgot-password`     | Request password reset OTP   | No            |
| POST   | `/api/auth/reset-password`      | Reset password with OTP      | No            |
| GET    | `/api/profile`                  | Get user profile             | Yes           |
| PUT    | `/api/profile`                  | Update user profile          | Yes           |
| POST   | `/api/chat/send`                | Send message to AI           | Yes           |
| GET    | `/api/chat/history`             | Get chat history             | Yes           |
| DELETE | `/api/chat/history/{chat_id}`   | Delete a chat                | Yes           |
| GET    | `/api/premium/status`           | Get premium status           | Yes           |
| POST   | `/api/premium/verify-payment`   | Submit UPI payment           | Yes           |
| POST   | `/api/premium/select-character` | Select premium character     | Yes           |
| GET    | `/api/daily-shloka`             | Get daily Gita verse         | Yes           |
| POST   | `/api/feedback`                 | Submit feedback              | Yes           |

### Admin Backend (Port 8002)

| Method | Endpoint                                 | Description              | Auth Required |
|--------|------------------------------------------|--------------------------|---------------|
| GET    | `/api/admin/health`                      | Health check             | No            |
| POST   | `/api/admin/login`                       | Admin login              | No            |
| GET    | `/api/admin/overview`                    | Dashboard stats          | Yes           |
| GET    | `/api/admin/users`                       | List all users           | Yes           |
| GET    | `/api/admin/users/{id}`                  | Get user details         | Yes           |
| DELETE | `/api/admin/users/{id}`                  | Delete user              | Yes (super)   |
| GET    | `/api/admin/chats`                       | List all chats           | Yes           |
| DELETE | `/api/admin/chats/{id}`                  | Delete chat              | Yes           |
| GET    | `/api/admin/analytics`                   | 7-day analytics          | Yes           |
| GET    | `/api/admin/feedback`                    | List feedback            | Yes           |
| GET    | `/api/admin/payments`                    | List payments            | Yes           |
| PUT    | `/api/admin/payments/{id}/approve`       | Approve payment          | Yes (super)   |
| PUT    | `/api/admin/payments/{id}/reject`        | Reject payment           | Yes (super)   |
| GET    | `/api/admin/revenue-stats`               | Revenue statistics       | Yes           |
| GET    | `/api/admin/ai-config`                   | Get AI configuration     | Yes           |
| PUT    | `/api/admin/ai-config`                   | Update AI configuration  | Yes (super)   |

---

## Database Schema

### users collection

```json
{
  \"_id\": \"ObjectId\",
  \"name\": \"string\",
  \"email\": \"string (unique)\",
  \"password\": \"string (bcrypt hashed)\",
  \"created_at\": \"datetime\",
  \"total_chats\": \"int\",
  \"current_streak\": \"int\",
  \"longest_streak\": \"int\",
  \"last_activity_date\": \"datetime\",
  \"is_premium\": \"boolean\",
  \"premium_expires\": \"datetime or null\",
  \"selected_character\": \"string (arjun/krishna/bhima/draupadi/karna)\"
}
```

### chats collection

```json
{
  \"_id\": \"ObjectId\",
  \"user_id\": \"ObjectId (ref: users)\",
  \"message\": \"string\",
  \"response\": \"string\",
  \"mode\": \"string (general/meditation/decision/heartbreak/study)\",
  \"character\": \"string\",
  \"emotion_detected\": \"string\",
  \"timestamp\": \"datetime\"
}
```

### payments collection

```json
{
  \"_id\": \"ObjectId\",
  \"user_id\": \"ObjectId (ref: users)\",
  \"user_email\": \"string\",
  \"user_name\": \"string\",
  \"plan\": \"string\",
  \"amount\": \"int\",
  \"transaction_id\": \"string\",
  \"payment_method\": \"string (manual_upi)\",
  \"status\": \"string (pending/approved/rejected)\",
  \"submitted_at\": \"datetime\",
  \"verified_at\": \"datetime or null\",
  \"verified_by\": \"string or null\"
}
```

### admins collection

```json
{
  \"_id\": \"ObjectId\",
  \"username\": \"string\",
  \"password\": \"string (bcrypt hashed)\",
  \"role\": \"string (super_admin/admin)\"
}
```

### feedback collection

```json
{
  \"_id\": \"ObjectId\",
  \"user_id\": \"string\",
  \"user_name\": \"string\",
  \"user_email\": \"string\",
  \"type\": \"string (issue/feedback)\",
  \"message\": \"string\",
  \"contact_preference\": \"string\",
  \"status\": \"string\",
  \"timestamp\": \"datetime\"
}
```

---

## Troubleshooting

### \"MongoDB connection failed\"
- Make sure MongoDB is running: `sudo systemctl start mongod` (Linux) or `brew services start mongodb-community` (macOS)
- Check if port 27017 is open: `mongosh` should connect

### \"Cannot connect to backend from phone\"
- Make sure phone and computer are on the **same WiFi**
- Use your computer's **local IP** (not `localhost`) in `frontend/.env`
- Check if firewall is blocking port 8001
- Windows: Allow Python through Windows Firewall

### \"AI chat not responding / 500 error\"
- Check if `EMERGENT_LLM_KEY` is set correctly in `backend/.env`
- Get the key from Emergent: Profile → Universal Key

### \"Expo Go can't load the app\"
- Check the Expo dev server is running (`npx expo start`)
- Make sure phone and computer are on the same network
- Try pressing `r` in the Expo terminal to reload
- Try `npx expo start --clear` to clear cache

### \"pip install fails\"
- Make sure virtual environment is activated
- Try upgrading pip: `pip install --upgrade pip`
- On Windows, try running terminal as Administrator

### \"Build failed on EAS\"
- Check `app.json` has valid `bundleIdentifier` (iOS) and `package` (Android)
- Make sure you're logged in: `eas login`
- Check build logs on [expo.dev](https://expo.dev)

### \"Admin dashboard shows empty\"
- Make sure the admin backend is running on port 8002
- Make sure `DB_NAME` in admin `.env` matches the main backend
- Run `seed_admin.py` to create the admin account

---

## Quick Start Summary (TL;DR)

```bash
# Terminal 1 — Start MongoDB (if not running as service)
mongod

# Terminal 2 — Start Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Edit .env with your EMERGENT_LLM_KEY
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3 — Start Frontend
cd frontend
yarn install
# Edit .env with your backend IP
npx expo start

# Terminal 4 — Start Admin Backend (optional)
cd admin-dashboard/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 5 — Start Admin Frontend (optional)
cd admin-dashboard/frontend
python3 -m http.server 8003

# Open Expo Go on phone → Scan QR code → Done!
```

---

## License

This project is proprietary. All rights reserved.

---

**Built with love and spiritual wisdom** ☸️

*\"You have the right to perform your duty, but you are not entitled to the fruits of your actions.\" — Bhagavad Gita 2.47*
"
