# SvelteKit Single Page Application (SPA) for Android deployment with Node.js Backend + PostgreSQL database

A Single Page Application (SPA) built with SvelteKit, Node.js backend, PostgreSQL database, and Android deployment support using Capacitor.

## Features

- **Frontend**: SvelteKit SPA with TypeScript
- **Backend**: Node.js/Express REST API
- **Database**: PostgreSQL with connection pooling
- **Authentication**: JWT-based authentication with secure password hashing
- **Security**: Helmet, CORS, rate limiting, input validation
- **Mobile**: Android deployment ready with Capacitor
- **DevOps**: Docker containerization, Nginx reverse proxy
- **Testing**: Jest test suite for backend API

## � Data Flow Architecture

This section illustrates how the SvelteKit SPA interacts with the Node.js REST API and PostgreSQL database, including authentication flow with JWT tokens.

### System Architecture

```
┌─────────────────┐    HTTP/HTTPS     ┌─────────────────┐    SQL Queries    ┌─────────────────┐
│   SvelteKit     │ ───────────────►  │   Node.js       │ ───────────────►  │   PostgreSQL    │
│   Frontend      │                   │   Express API   │                   │   Database      │
│   (Port 5173)   │ ◄───────────────  │   (Port 3000)   │ ◄───────────────  │   (Port 5432)   │
└─────────────────┘    JSON + JWT     └─────────────────┘    Result Sets    └─────────────────┘
        │                                      │
        │                                      │
        ▼                                      ▼
┌─────────────────┐                  ┌─────────────────┐
│   Capacitor     │                  │   Nginx Proxy   │
│   Android App   │                  │   (Port 80/443) │
└─────────────────┘                  └─────────────────┘
```

### Authentication Data Flow

#### 1. User Registration Flow

```
SvelteKit SPA                Node.js API               PostgreSQL DB
     │                            │                         │
     │ POST /api/auth/register    │                         │
     │ {name, email, password}    │                         │
     ├───────────────────────────►                          │
     │                            │ Hash password (bcrypt)  │
     │                            │                         │
     │                            │ INSERT INTO users       │
     │                            ├─────────────────────────►
     │                            │                         │
     │                            │ ◄─────────────────────┤ │
     │                            │ User created (user_id)  │
     │                            │                         │
     │                            │ Generate JWT token      │
     │                            │                         │
     │ ◄────────────────────────┤ │                         │
     │ 201 Created                │                         │
     │ {success: true,            │                         │
     │  data: {user, token}}      │                         │
     │                            │                         │
     │ Store token in authStore   │                         │
     │ Redirect to Dashboard      │                         │
```

#### 2. User Login Flow

```
SvelteKit SPA                Node.js API               PostgreSQL DB
     │                             │                         │
     │ POST /api/auth/login        │                         │
     │ {email, password}           │                         │
     ├───────────────────────────►                           │
     │                            │ SELECT user WHERE email │
     │                            ├─────────────────────────►
     │                            │                         │
     │                            │ ◄─────────────────────┤ │
     │                            │ User data               │
     │                            │                         │
     │                            │ Compare password        │
     │                            │ (bcrypt.compare)        │
     │                            │                         │
     │                            │ Generate JWT token      │
     │                            │ (if password valid)     │
     │                            │                         │
     │ ◄────────────────────────┤ │                         │
     │ 200 OK                     │                         │
     │ {success: true,            │                         │
     │  data: {user, token}}      │                         │
     │                            │                         │
     │ Store token in authStore   │                         │
     │ Update UI state            │                         │
```

#### 3. Authenticated API Requests Flow

```
SvelteKit SPA                Node.js API               PostgreSQL DB
     │                             │                        │
     │ GET /api/items              │                        │
     │ Authorization: Bearer <JWT> │                        │
     ├───────────────────────────►                          │
     │                            │ Verify JWT token        │
     │                            │ (middleware/auth.js)    │
     │                            │                         │
     │                            │ SELECT * FROM items     │
     │                            │ WHERE user_id = ?       │
     │                            ├───────────────────────► │
     │                            │                         │
     │                            │ ◄─────────────────────┤ │
     │                            │ Items array             │
     │                            │                         │
     │ ◄────────────────────────┤ │                         │
     │ 200 OK                     │                         │
     │ {success: true,            │                         │
     │  data: items[]}            │                         │
     │                            │                         │
     │ Update component state     │                         │
     │ Render items in UI         │                         │
```

### HTTP Methods and Endpoints

#### Authentication Endpoints
```
POST   /api/auth/register    - Create new user account
POST   /api/auth/login       - Authenticate user and get JWT
POST   /api/auth/logout      - Invalidate session (client-side token removal)
GET    /api/auth/me          - Get current user profile (requires JWT)
```

#### Data Endpoints (Protected)
```
GET    /api/items           - Fetch user's items
POST   /api/items           - Create new item
PUT    /api/items/:id       - Update existing item
DELETE /api/items/:id       - Delete item
```

### JWT Token Flow

#### Token Structure
```javascript
// JWT Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// JWT Payload
{
  "userId": 123,
  "email": "user@example.com",
  "iat": 1640995200,    // Issued at
  "exp": 1641081600     // Expires at (24h later)
}
```

#### Token Lifecycle

```
1. User Login/Register
   ├─► Server generates JWT with user info
   ├─► Token sent to client in response
   └─► Client stores token in Svelte store

2. API Requests
   ├─► Axios interceptor adds "Authorization: Bearer <token>"
   ├─► Server middleware verifies token
   ├─► If valid: continue to route handler
   └─► If invalid: return 401 Unauthorized

3. Token Expiration
   ├─► Server returns 401 when token expired
   ├─► Axios interceptor catches 401 response
   ├─► Client clears auth store
   └─► Redirects user to login page
```

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Items table (example data)
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Security Implementation

#### Password Security
```javascript
// Registration: Hash password with bcrypt
const saltRounds = 12;
const hashedPassword = await bcrypt.hash(password, saltRounds);

// Login: Compare plaintext with hash
const isValidPassword = await bcrypt.compare(password, hashedPassword);
```

#### JWT Security
```javascript
// Generate token
const token = jwt.sign(
    { userId: user.id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: '24h' }
);

// Verify token (middleware)
const decoded = jwt.verify(token, process.env.JWT_SECRET);
```

#### API Security Middleware
- **Helmet**: Security headers
- **CORS**: Cross-origin request filtering
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Sanitize request data
- **SQL Injection Prevention**: Parameterized queries

## 📁 Project Structure

```
├── src/                          # SvelteKit frontend source
│   ├── lib/
│   │   ├── components/          # Svelte components
│   │   │   ├── LoginForm.svelte
│   │   │   ├── RegisterForm.svelte
│   │   │   └── Dashboard.svelte
│   │   ├── stores/             # Svelte stores
│   │   │   └── auth.ts
│   │   └── api.ts              # API client
│   ├── routes/                 # SvelteKit routes
│   │   ├── +layout.svelte
│   │   └── +page.svelte
│   └── app.css                 # Global styles
├── backend/                    # Node.js backend
│   ├── src/
│   │   ├── config/            # Database configuration
│   │   ├── middleware/        # Express middleware
│   │   ├── routes/           # API routes
│   │   └── server.js         # Main server file
│   ├── tests/                # Test files
│   └── Dockerfile           # Backend container config
├── nginx/                   # Nginx configuration
├── docker-compose.yml      # Multi-container setup
├── capacitor.config.ts     # Capacitor mobile config
└── README.md
```

## 🛠️ Development Setup

### Prerequisites

Install the following tools:

- **Node.js** (v18 or higher)
- **npm** or **yarn**
- **PostgreSQL** (v12 or higher)
- **Docker** & **Docker Compose** (for containerized deployment)
- **Android Studio** (for Android development)

### Architecture Overview

This SvelteKit SPA follows a modular architecture with clear separation of concerns:

#### Frontend Architecture (SvelteKit SPA)
- **Single Page Application**: Built with SvelteKit using `@sveltejs/adapter-static` for SPA mode
- **Component-Based**: Modular Svelte components for Login, Register, and Dashboard functionality
- **State Management**: Svelte stores for authentication and application state
- **API Integration**: Axios-based API client with JWT token management
- **Mobile-Ready**: Capacitor integration for native Android deployment

#### Purpose of `src/lib/index.ts`

The `index.ts` file serves as the main entry point for the `$lib` alias in SvelteKit. It's designed to:

- **Barrel Export Pattern**: Centralizes exports from the lib directory for cleaner imports
- **Export commonly used utilities**: Components, API functions, stores, and TypeScript types
- **Provide a clean import interface**: Enables `import { LoginForm, authStore, authApi } from '$lib'` instead of multiple import statements
- **Act as public API**: Defines what's publicly available from your library
- **Improve Developer Experience**: Better auto-completion and easier refactoring

**Example Usage:**
```typescript
// Instead of multiple imports:
import { authStore } from '$lib/stores/auth';
import LoginForm from '$lib/components/LoginForm.svelte';
import { authApi } from '$lib/api';

// Use single barrel import:
import { authStore, LoginForm, authApi } from '$lib';
```

**What it exports:**
- **Components**: `LoginForm`, `RegisterForm`, `Dashboard`
- **State Management**: `authStore` for authentication state
- **API Layer**: `authApi`, `dataApi` for backend communication
- **Utilities**: `formatDate`, `isValidEmail`, `debounce`, `storage` helpers
- **Types**: `LoginCredentials`, `RegisterCredentials`, `ApiResponse` interfaces

#### Backend Architecture (Node.js/Express)
- **RESTful API**: Express.js server with structured routes
- **JWT Authentication**: Secure token-based authentication
- **Database Integration**: PostgreSQL with connection pooling
- **Security Middleware**: Helmet, CORS, rate limiting, input validation
- **Error Handling**: Centralized error handling and logging

### 1. Clone and Install Dependencies

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
npm install
cd ..
```

### 2. Database Setup

#### Option A: Local PostgreSQL

```bash
# Create database
createdb sveltekit_spa

# Set environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your database credentials
```

#### Option B: Docker PostgreSQL

```bash
# Start PostgreSQL container
docker run --name postgres-spa \
  -e POSTGRES_DB=sveltekit_spa \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15-alpine
```

### 3. Environment Configuration

Create `backend/.env` file:

```bash
# Copy example environment file
cp backend/.env.example backend/.env
```

Edit the `.env` file with your configuration:

```env
NODE_ENV=development
PORT=3000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sveltekit_spa
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h

# CORS
FRONTEND_URL=http://localhost:5173
```

### 4. Start Development Servers

#### Terminal 1: Backend Server
```bash
cd backend
npm run dev
# Server will start on http://localhost:3000
```

#### Terminal 2: Frontend Development Server
```bash
npm run dev
# Frontend will start on http://localhost:5173
```

The application will be available at http://localhost:5173

## Android Deployment with Capacitor

### Overview

Capacitor is a cross-platform native runtime that allows you to deploy your SvelteKit SPA as a native Android application. Capacitor acts as a bridge between your web application and native Android APIs, enabling features like camera access, file system operations, and native UI components.

### Prerequisites for Ubuntu Linux

Before deploying to Android, ensure you have the following installed on your Ubuntu system:

#### 1. Java Development Kit (JDK)

```bash
# Install OpenJDK 17 (recommended for Android development)
sudo apt update
sudo apt install openjdk-17-jdk

# Verify installation
java -version
javac -version

# Set JAVA_HOME environment variable
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
source ~/.bashrc
```

#### 2. Android Studio Installation

```bash
# Download Android Studio (or use snap)
sudo snap install android-studio --classic

# Alternative: Manual installation
# Download from https://developer.android.com/studio
# Extract and run: ./android-studio/bin/studio.sh
```

#### 3. Android SDK Setup

After installing Android Studio:

1. **Open Android Studio**
2. **Go to**: File → Settings → Appearance & Behavior → System Settings → Android SDK
3. **Install required SDK versions**:
   - Android 13 (API Level 33) - recommended
   - Android 12 (API Level 31)
   - Android SDK Build-Tools (latest version)
   - Android SDK Platform-Tools
   - Android SDK Tools

4. **Set environment variables**:

```bash
# Add to ~/.bashrc
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export ANDROID_SDK_ROOT=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/emulator' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/build-tools/34.0.0' >> ~/.bashrc
source ~/.bashrc
```

#### 4. Verify Android Setup

```bash
# Check ADB (Android Debug Bridge)
adb version

# List connected devices
adb devices

# Check SDK manager
sdkmanager --list
```

### Capacitor Installation and Configuration

#### 1. Install Capacitor Dependencies

```bash
# Install Capacitor CLI and core
npm install @capacitor/core @capacitor/cli

# Install Android platform
npm install @capacitor/android

# Install additional plugins (optional)
npm install @capacitor/app @capacitor/haptics @capacitor/keyboard @capacitor/status-bar
```

#### 2. Initialize Capacitor

```bash
# Initialize Capacitor (if not already done)
npx capacitor init "SvelteKit SPA" "com.example.sveltekit.spa"
```

#### 3. Configure Capacitor

Edit `capacitor.config.ts`:

```typescript
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.example.sveltekit.spa',
  appName: 'SvelteKit SPA',
  webDir: 'build',
  server: {
    androidScheme: 'https',
    // For development with live reload
    // url: 'http://10.0.2.2:5173', // Use this IP for Android emulator
    // cleartext: true
  },
  android: {
    buildOptions: {
      keystorePath: undefined,
      keystorePassword: undefined,
      keystoreAlias: undefined,
      keystoreAliasPassword: undefined,
      releaseType: 'APK'
    }
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 3000,
      launchAutoHide: true,
      backgroundColor: "#ffffffff",
      androidSplashResourceName: "splash",
      androidScaleType: "CENTER_CROP",
      showSpinner: true,
      androidSpinnerStyle: "large",
      iosSpinnerStyle: "small",
      spinnerColor: "#999999",
      splashFullScreen: true,
      splashImmersive: true,
    },
  },
};

export default config;
```

### Android Development Workflow

#### 1. Build SvelteKit Application

```bash
# Build the SvelteKit app for production
npm run build

# Verify build directory exists and contains files
ls -la build/
```

#### 2. Add Android Platform

```bash
# Add Android platform (only run once)
npx capacitor add android

# This creates the android/ directory with native Android project
```

#### 3. Sync Web Assets to Android

```bash
# Copy web assets to native Android project
npx capacitor sync android

# Alternative: sync and copy
npx capacitor copy android
```

#### 4. Development Options

##### Option A: Android Studio Development

```bash
# Open Android project in Android Studio
npx capacitor open android
```

In Android Studio:
- **Build the project**: Build → Make Project
- **Run on emulator**: Run → Run 'app'
- **Debug**: Set breakpoints and use Android debugger
- **Generate APK**: Build → Build Bundle(s) / APK(s) → Build APK(s)

##### Option B: Command Line (CLI) Development

```bash
# Build APK from command line
cd android
./gradlew assembleDebug

# Install APK to connected device
adb install app/build/outputs/apk/debug/app-debug.apk

# View logs
adb logcat
```

### Device Connection and USB Debugging

#### 1. Enable Developer Options on Android Device

1. **Go to**: Settings → About Phone
2. **Tap "Build Number" 7 times** to enable Developer Options
3. **Go to**: Settings → Developer Options
4. **Enable "USB Debugging"**
5. **Enable "Install via USB"** (if available)

#### 2. Connect Device via USB

```bash
# Connect Android device via USB cable
# Check if device is recognized
adb devices

# If device is not listed, try:
lsusb  # Check if USB device is detected

# Restart ADB server
adb kill-server
adb start-server
adb devices
```

#### 3. Install USB Rules (if device not recognized)

```bash
# Create udev rules for Android devices
sudo nano /etc/udev/rules.d/51-android.rules

# Add these lines (replace XXXX with your device vendor ID):
SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev" # Google
SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", MODE="0666", GROUP="plugdev" # Samsung
SUBSYSTEM=="usb", ATTR{idVendor}=="22b8", MODE="0666", GROUP="plugdev" # Motorola

# Set permissions and reload rules
sudo chmod a+r /etc/udev/rules.d/51-android.rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to plugdev group
sudo usermod -a -G plugdev $USER
```

### Live Reload Development

For faster development, you can use live reload:

#### 1. Configure Live Reload

```typescript
// capacitor.config.ts
const config: CapacitorConfig = {
  // ... other config
  server: {
    url: 'http://192.168.1.100:5173', // Replace with your local IP
    cleartext: true
  }
};
```

#### 2. Start Development Servers

```bash
# Terminal 1: Start SvelteKit dev server
npm run dev -- --host

# Terminal 2: Start backend server
cd backend && npm run dev

# Terminal 3: Sync and run Android app
npx capacitor sync android
npx capacitor run android
```

### Building for Production

#### 1. Prepare Production Build

```bash
# Build SvelteKit app
npm run build

# Update Capacitor config for production
# Remove server.url from capacitor.config.ts

# Sync to Android
npx capacitor sync android
```

#### 2. Generate Signed APK

```bash
# Open Android Studio
npx capacitor open android

# In Android Studio:
# Build → Generate Signed Bundle / APK
# Follow the wizard to create/use keystore
```

#### 3. Command Line APK Generation

```bash
# Navigate to android directory
cd android

# Build release APK
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk
```

### Troubleshooting Common Issues

#### ADB Device Not Found

```bash
# Check USB connection
lsusb

# Restart ADB
adb kill-server
sudo adb start-server
adb devices

# Check device authorization
# (Accept prompt on device)
```

#### Gradle Build Errors

```bash
# Clean and rebuild
cd android
./gradlew clean
./gradlew assembleDebug
```

#### Capacitor Sync Issues

```bash
# Clear Capacitor cache
npx capacitor sync android --force

# Reinstall Capacitor
npm uninstall @capacitor/android
npm install @capacitor/android
npx capacitor add android
```

#### Memory Issues

```bash
# Increase Gradle memory
echo "org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8" >> android/gradle.properties
```

### Development Baseline

1. **Always build SvelteKit first** before syncing to Android
2. **Use Android emulator** for initial development and testing
3. **Test on real devices** before production release
4. **Enable USB debugging** only during development
5. **Use HTTPS in production** for Capacitor apps
6. **Test different Android versions** and screen sizes
7. **Optimize images and assets** for mobile devices
8. **Handle network connectivity** changes gracefully

### Useful Commands

```bash
# Development workflow
npm run build                    # Build SvelteKit app
npx capacitor sync android       # Sync to Android
npx capacitor open android       # Open in Android Studio
npx capacitor run android        # Build and run on device

# Device management
adb devices                      # List connected devices
adb logcat                       # View device logs
adb install app-debug.apk        # Install APK manually

# Android project
cd android && ./gradlew assembleDebug    # Build debug APK
cd android && ./gradlew clean            # Clean build
```

This comprehensive setup enables you to develop, test, and deploy your SvelteKit SPA as a native Android application using Capacitor on Ubuntu Linux.

## 🐳 Docker Deployment

### Full Stack with Docker Compose

```bash
# Create production environment file
cp .env.example .env
# Edit .env with production values

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000
- **Nginx Proxy**: http://localhost (routes to frontend and API)
- **PostgreSQL**: localhost:5432

## RESTful API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Items Management
- `GET /api/items` - Get user's items (paginated)
- `POST /api/items` - Create new item
- `GET /api/items/:id` - Get specific item
- `PUT /api/items/:id` - Update item
- `DELETE /api/items/:id` - Delete item

### System
- `GET /health` - Health check

## 🔐 Security Features

- **JWT Authentication** with secure token generation
- **Password Hashing** using bcryptjs
- **Rate Limiting** to prevent abuse
- **CORS Configuration** for cross-origin requests
- **Input Validation** using express-validator
- **Security Headers** via Helmet
- **SQL Injection Protection** using parameterized queries

---
