# Development of microservices with ASP.NET Core on Linux/Debian

This document provides instructions to setup ASP.NET Core environment with Visual Studio Code on Linux/Debian. The application implements communications with gRPC for microservices, React integration (Vite), and Docker deployment on Azure services.

**Last Updated**: August 2025

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting up ASP.NET Core on Linux/Debian](#setting-up-aspnet-core-on-linuxdebian)
- [VS Code Configuration](#vs-code-configuration)
- [Debugging C# ASP.NET Code](#debugging-c-aspnet-code-with-vs-code)
- [Creating ASP.NET Core with React Application Utilizing Vite](#creating-aspnet-core-with-react-application-utilizing-vite)
- [gRPC Microservices Development](#grpc-microservices-development)
- [Data Flow and Architecture](#data-flow-and-architecture)
- [Development Environment Setup](#development-environment-setup)
- [Production Deployment](#production-deployment)
- [Docker and Azure Deployment](#docker-and-azure-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have the following:

- **Operating System**: Linux/Debian 11 or later
- **Hardware**: Minimum 8GB RAM, 20GB disk space
- **Network**: Internet connection for package downloads
- **User Privileges**: sudo access for package installation

## Setting up ASP.NET Core on Linux/Debian

### 1. Install .NET SDK 8.0

#### Method 1: Using Microsoft Package Repository (Recommended)

```bash
# Download and install Microsoft package repository configuration
wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Update package list
sudo apt update

# Install dependencies and .NET SDK
sudo apt install -y apt-transport-https dotnet-sdk-8.0
```

#### Method 2: For Debian 11

```bash
# For Debian 11 users
wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

sudo apt update
sudo apt install -y apt-transport-https dotnet-sdk-8.0
```

### 2. Verify Installation

```bash
# Check .NET version
dotnet --version

# List installed SDKs
dotnet --list-sdks

# List installed runtimes
dotnet --list-runtimes
```

### 3. Install Node.js (for React development)

```bash
# Install Node.js LTS
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

## VS Code Configuration

### 1. Install Visual Studio Code

```bash
# Download and install VS Code
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'

sudo apt update
sudo apt install code
```

### 2. Install Essential Extensions

Launch VS Code and install the following extensions:

- **C# (Microsoft)**: `ms-dotnettools.csharp`
- **C# Dev Kit**: `ms-dotnettools.csdevkit`
- **IntelliCode for C# Dev Kit**: `ms-dotnettools.vscodeintellicode-csharp`
- **ES7+ React/Redux/React-Native snippets**: `dsznajder.es7-react-js-snippets`
- **TypeScript Hero**: `rbbit.typescript-hero`
- **Docker**: `ms-azuretools.vscode-docker`
- **Azure App Service**: `ms-azuretools.vscode-azureappservice`

```bash
# Install extensions via command line
code --install-extension ms-dotnettools.csharp
code --install-extension ms-dotnettools.csdevkit
code --install-extension ms-dotnettools.vscodeintellicode-csharp
code --install-extension dsznajder.es7-react-js-snippets
code --install-extension rbbit.typescript-hero
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-azuretools.vscode-azureappservice
```

## Debugging C# ASP.NET Code with VS Code

### 1. Project Setup for Debugging

Create a new ASP.NET Core project:

```bash
# Create a new web API project
dotnet new webapi -n MyWebApi
cd MyWebApi

# Open in VS Code
code .
```

### 2. Generate Debug Assets

When you open an ASP.NET Core project in VS Code, you'll be prompted to add required assets for build and debug:

1. Click **"Yes"** when prompted to add required assets
2. Alternatively, use Command Palette (`Ctrl+Shift+P`) → ".NET: Generate Assets for Build and Debug"

This creates a `.vscode` folder with:
- `launch.json`: Debug configuration
- `tasks.json`: Build tasks

### 3. Configure Debugging

The generated `launch.json` will contain:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": ".NET Core Launch (web)",
            "type": "coreclr",
            "request": "launch",
            "preLaunchTask": "build",
            "program": "${workspaceFolder}/bin/Debug/net8.0/MyWebApi.dll",
            "args": [],
            "cwd": "${workspaceFolder}",
            "stopAtEntry": false,
            "serverReadyAction": {
                "action": "openExternally",
                "pattern": "\\bNow listening on:\\s+(https?://\\S+)"
            },
            "env": {
                "ASPNETCORE_ENVIRONMENT": "Development"
            },
            "sourceFileMap": {
                "/Views": "${workspaceFolder}/Views"
            }
        }
    ]
}
```

### 4. Debug Your Application

1. Set breakpoints by clicking on line numbers
2. Press `F5` or go to Run and Debug view (`Ctrl+Shift+D`)
3. Select configuration and click the green play button

### 5. Debug Features

- **Breakpoints**: Click on line numbers to set/remove
- **Watch Variables**: Add variables to watch panel
- **Call Stack**: View execution stack
- **Debug Console**: Execute expressions during debugging
- **Step Controls**: Step over (`F10`), step into (`F11`), step out (`Shift+F11`)

## Creating ASP.NET Core with React Application Utilizing Vite

### Overview

This section covers creating a modern React + ASP.NET Core application using **Vite** as the build tool for React development. Vite provides fast hot module replacement (HMR), optimized builds, and an excellent development experience.

### 1. Create React + ASP.NET Core Project with Vite

#### Method 1: Using .NET CLI Template (Recommended)

```bash
# Create a new React + ASP.NET Core project with Vite
dotnet new react -n ReactWithASP
cd ReactWithASP

# The template automatically uses Vite for React development
# Project structure:
# ReactWithASP.Server/     - ASP.NET Core backend
# reactwithasp.client/     - React frontend with Vite
```

#### Method 2: Manual Setup with Vite

If you want to set up manually or understand the process:

```bash
# Create ASP.NET Core Web API
dotnet new webapi -n ReactWithASP.Server
cd ReactWithASP.Server

# Create React app with Vite in separate project
cd ..
npm create vite@latest reactwithasp.client -- --template react-ts
cd reactwithasp.client

# Install dependencies
npm install

# Return to root and create solution
cd ..
dotnet new sln -n ReactWithASP
dotnet sln add ReactWithASP.Server/ReactWithASP.Server.csproj
```

### 2. Project Structure Analysis

```
ReactWithASP/
├── ReactWithASP.Server/          # ASP.NET Core Backend
│   ├── Controllers/
│   │   └── WeatherForecastController.cs
│   ├── Program.cs
│   ├── appsettings.json
│   ├── appsettings.Development.json
│   └── Properties/
│       └── launchSettings.json
├── reactwithasp.client/          # React Frontend with Vite
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── components/
│   ├── public/
│   │   └── vite.svg
│   ├── package.json
│   ├── vite.config.js            # Vite configuration
│   ├── tsconfig.json             # TypeScript configuration
│   ├── eslint.config.js          # ESLint configuration
│   └── index.html
└── ReactWithASP.sln              # Solution file
```

### 3. Vite Configuration for ASP.NET Core Integration

#### Essential Vite Configuration (vite.config.js)

```javascript
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  // Default port from ASP.NET Core HTTPS development
  const target = env.ASPNETCORE_HTTPS_PORT 
    ? `https://localhost:${env.ASPNETCORE_HTTPS_PORT}` 
    : env.ASPNETCORE_URLS 
    ? env.ASPNETCORE_URLS.split(';')[0] 
    : 'https://localhost:7042';

  return {
    plugins: [react()],
    server: {
      port: 5173,  // Vite dev server port
      proxy: {
        // Proxy API calls to ASP.NET Core backend
        '/api': {
          target: target,
          secure: false,           // Allow self-signed certificates
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        },
        '/weatherforecast': {
          target: target,
          secure: false,
          changeOrigin: true
        }
      },
      // Configure HTTPS for Vite dev server
      https: false  // Set to true if you need HTTPS on frontend
    },
    build: {
      outDir: 'dist',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
          },
        },
      },
    },
    optimizeDeps: {
      include: ['react', 'react-dom'],
    },
  };
});
```

#### Vite Configuration with Hot Reload

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { readFileSync } from 'fs';
import { join } from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: 'localhost',
    proxy: {
      '/api': {
        target: 'https://localhost:7042',
        secure: false,
        changeOrigin: true,
      }
    },
    hmr: {
      overlay: true,
    },
    // Optional: Custom middleware for development
    middlewares: [
      // Add custom middleware here if needed
    ]
  },
  css: {
    devSourcemap: true,
  },
  build: {
    sourcemap: true,
    outDir: 'dist',
  },
  define: {
    // Define global constants
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
});
```

### 4. Configure Development Environment

#### Backend Configuration (Program.cs)

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure CORS for Vite React frontend
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(
            "http://localhost:5173",    // Vite dev server default port
            "https://localhost:5173",   // Vite dev server HTTPS
            "http://localhost:3000",    // Alternative React port
            "https://localhost:3000")   // Alternative React HTTPS
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();
app.UseCors();
app.UseAuthorization();
app.MapControllers();

// Serve static files for production (Vite build output)
app.UseDefaultFiles();
app.UseStaticFiles();

// Fallback routing for SPA (important for client-side routing)
app.MapFallbackToFile("/index.html");

app.Run();
```

#### Sample Weather Controller (Controllers/WeatherForecastController.cs)

```csharp
using Microsoft.AspNetCore.Mvc;

namespace ReactWithASP.Server.Controllers;

[ApiController]
[Route("api/[controller]")]
public class WeatherForecastController : ControllerBase
{
    private static readonly string[] Summaries = new[]
    {
        "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", 
        "Balmy", "Hot", "Sweltering", "Scorching"
    };

    private readonly ILogger<WeatherForecastController> _logger;

    public WeatherForecastController(ILogger<WeatherForecastController> logger)
    {
        _logger = logger;
    }

    [HttpGet]
    public IEnumerable<WeatherForecast> Get()
    {
        return Enumerable.Range(1, 5).Select(index => new WeatherForecast
        {
            Date = DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
            TemperatureC = Random.Shared.Next(-20, 55),
            Summary = Summaries[Random.Shared.Next(Summaries.Length)]
        })
        .ToArray();
    }

    [HttpGet("{id}")]
    public ActionResult<WeatherForecast> GetById(int id)
    {
        if (id < 1 || id > 5)
        {
            return NotFound();
        }

        return new WeatherForecast
        {
            Date = DateOnly.FromDateTime(DateTime.Now.AddDays(id)),
            TemperatureC = Random.Shared.Next(-20, 55),
            Summary = Summaries[Random.Shared.Next(Summaries.Length)]
        };
    }
}

public record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}
```

#### Frontend Configuration and React Components

##### Main React Component (src/App.jsx)

```jsx
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const [forecasts, setForecasts] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        populateWeatherData();
    }, []);

    const populateWeatherData = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/weatherforecast');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            setForecasts(data);
        } catch (error) {
            console.error('Error fetching weather data:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const refreshData = () => {
        populateWeatherData();
    };

    if (loading) {
        return (
            <div className="loading">
                <p>Loading weather data...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="error">
                <p>Error loading weather data: {error}</p>
                <button onClick={refreshData}>Retry</button>
            </div>
        );
    }

    return (
        <div className="App">
            <header className="App-header">
                <h1>Weather Forecast</h1>
                <p>This component demonstrates fetching data from the ASP.NET Core server.</p>
                <button onClick={refreshData} className="refresh-btn">
                    Refresh Data
                </button>
            </header>
            
            <main className="weather-container">
                {forecasts && forecasts.length > 0 ? (
                    <table className="weather-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Temp. (C)</th>
                                <th>Temp. (F)</th>
                                <th>Summary</th>
                            </tr>
                        </thead>
                        <tbody>
                            {forecasts.map((forecast, index) => (
                                <tr key={index}>
                                    <td>{forecast.date}</td>
                                    <td>{forecast.temperatureC}</td>
                                    <td>{forecast.temperatureF}</td>
                                    <td>{forecast.summary}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No weather data available.</p>
                )}
            </main>
        </div>
    );
}

export default App;
```

##### Enhanced CSS Styling (src/App.css)

```css
.App {
    text-align: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.App-header {
    background-color: #282c34;
    padding: 30px;
    color: white;
    border-radius: 8px;
    margin-bottom: 30px;
}

.App-header h1 {
    margin: 0 0 10px 0;
    font-size: 2.5em;
}

.App-header p {
    margin: 15px 0;
    font-size: 1.1em;
    opacity: 0.9;
}

.refresh-btn {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 12px 24px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 10px 2px;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.refresh-btn:hover {
    background-color: #45a049;
}

.weather-container {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.weather-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.weather-table th,
.weather-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.weather-table th {
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 0.9em;
    letter-spacing: 0.5px;
}

.weather-table tr:nth-child(even) {
    background-color: #f8f8f8;
}

.weather-table tr:hover {
    background-color: #f0f0f0;
}

.loading, .error {
    padding: 40px;
    text-align: center;
    font-size: 1.2em;
}

.error {
    color: #d32f2f;
    background-color: #ffebee;
    border-radius: 8px;
    margin: 20px 0;
}

.error button {
    margin-top: 15px;
    background-color: #d32f2f;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}

.error button:hover {
    background-color: #b71c1c;
}

@media (max-width: 768px) {
    .App {
        padding: 10px;
    }
    
    .weather-table {
        font-size: 0.9em;
    }
    
    .weather-table th,
    .weather-table td {
        padding: 8px 10px;
    }
}
```

### 5. Package.json Configuration for Vite

```json
{
  "name": "reactwithasp.client",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx,ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "eslint": "^8.57.0",
    "eslint-plugin-react": "^7.34.3",
    "eslint-plugin-react-hooks": "^4.6.2",
    "eslint-plugin-react-refresh": "^0.4.7",
    "vite": "^5.3.4"
  }
}
```

### 6. Development Workflow with Vite

#### Running the Application

#### Option 1: Start Both Projects Together (Recommended)

```bash
# From the root directory (ReactWithASP/)
dotnet run --project ReactWithASP.Server

# This automatically starts:
# - ASP.NET Core backend on https://localhost:7042
# - Vite dev server on http://localhost:5173
# - Hot reload enabled for both frontend and backend
```

#### Option 2: Start Projects Separately

```bash
# Terminal 1 - Start ASP.NET Core Backend
cd ReactWithASP/ReactWithASP.Server
dotnet watch run
# Backend runs on https://localhost:7042

# Terminal 2 - Start Vite React Frontend
cd ReactWithASP/reactwithasp.client
npm run dev
# Frontend runs on http://localhost:5173 with HMR enabled
```

#### Option 3: Production Build and Serve

```bash
# Build React app for production
cd reactwithasp.client
npm run build

# The build output goes to 'dist' folder
# ASP.NET Core will serve these static files in production

# Run ASP.NET Core in production mode
cd ../ReactWithASP.Server
dotnet run --configuration Release
```

### 7. Vite Development Features

#### Hot Module Replacement (HMR)

Vite provides near-instantaneous hot module replacement:

```javascript
// In vite.config.js - HMR configuration
export default defineConfig({
  plugins: [react()],
  server: {
    hmr: {
      port: 5174,        // Custom HMR port
      overlay: true,     // Show error overlay
    },
  },
});
```

#### Environment Variables

Create environment files for different configurations:

##### .env.development
```bash
VITE_API_BASE_URL=https://localhost:7042
VITE_APP_TITLE=Development Environment
VITE_ENABLE_DEBUG=true
```

##### .env.production
```bash
VITE_API_BASE_URL=https://api.yourapp.com
VITE_APP_TITLE=Production App
VITE_ENABLE_DEBUG=false
```

##### Using Environment Variables in React

```jsx
// src/config/api.js
const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'https://localhost:7042',
  appTitle: import.meta.env.VITE_APP_TITLE || 'React + ASP.NET App',
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
};

export default config;

// Usage in components
import config from './config/api';

const fetchWeatherData = async () => {
  const response = await fetch(`${config.apiBaseUrl}/api/weatherforecast`);
  return response.json();
};
```

### 8. Advanced Vite Configuration

#### Code Splitting and Lazy Loading

```jsx
// src/components/LazyComponent.jsx
import React, { Suspense, lazy } from 'react';

const WeatherChart = lazy(() => import('./WeatherChart'));

function App() {
  return (
    <div>
      <Suspense fallback={<div>Loading chart...</div>}>
        <WeatherChart />
      </Suspense>
    </div>
  );
}
```

#### Vite Build Optimization

```javascript
// vite.config.js - Production optimizations
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['axios', 'lodash'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});
```

### 9. Debugging with Vite and VS Code

#### VS Code Launch Configuration (.vscode/launch.json)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": ".NET Core Launch (web)",
      "type": "coreclr",
      "request": "launch",
      "preLaunchTask": "build",
      "program": "${workspaceFolder}/ReactWithASP.Server/bin/Debug/net8.0/ReactWithASP.Server.dll",
      "args": [],
      "cwd": "${workspaceFolder}/ReactWithASP.Server",
      "stopAtEntry": false,
      "serverReadyAction": {
        "action": "openExternally",
        "pattern": "\\bNow listening on:\\s+(https?://\\S+)"
      },
      "env": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      },
      "sourceFileMap": {
        "/Views": "${workspaceFolder}/Views"
      }
    },
    {
      "name": "Launch Chrome for React",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/reactwithasp.client/src",
      "sourceMaps": true,
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    }
  ],
  "compounds": [
    {
      "name": "Launch Full Stack",
      "configurations": [".NET Core Launch (web)", "Launch Chrome for React"]
    }
  ]
}
```

#### VS Code Tasks Configuration (.vscode/tasks.json)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "build",
      "command": "dotnet",
      "type": "process",
      "args": ["build", "${workspaceFolder}/ReactWithASP.Server/ReactWithASP.Server.csproj"],
      "problemMatcher": "$msCompile"
    },
    {
      "label": "start-backend",
      "command": "dotnet",
      "type": "process",
      "args": ["run", "--project", "${workspaceFolder}/ReactWithASP.Server"],
      "isBackground": true,
      "problemMatcher": {
        "owner": "dotnet",
        "pattern": "$msCompile",
        "background": {
          "activeOnStart": true,
          "beginsPattern": "^\\s*Now listening on:",
          "endsPattern": "^\\s*Application started\\."
        }
      }
    },
    {
      "label": "start-frontend",
      "command": "npm",
      "type": "shell",
      "args": ["run", "dev"],
      "options": {
        "cwd": "${workspaceFolder}/reactwithasp.client"
      },
      "isBackground": true,
      "problemMatcher": {
        "owner": "vite",
        "pattern": [
          {
            "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
            "file": 1,
            "line": 2,
            "column": 3,
            "severity": 4,
            "message": 5
          }
        ],
        "background": {
          "activeOnStart": true,
          "beginsPattern": "^\\s*VITE.*ready in",
          "endsPattern": "^\\s*Local:.*"
        }
      }
    }
  ]
}
```

### 10. Production Deployment with Vite

#### Building for Production

```bash
# Build React app with Vite
cd reactwithasp.client
npm run build

# Vite creates optimized build in 'dist' folder
# - Minified JavaScript and CSS
# - Asset optimization
# - Tree shaking
# - Code splitting
```

#### ASP.NET Core Project Configuration for Production

Update the `.csproj` file to include the React build:

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <SpaRoot>../reactwithasp.client/</SpaRoot>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.SpaProxy" Version="8.0.*" />
  </ItemGroup>

  <!-- Include React build output -->
  <ItemGroup>
    <DistFiles Include="$(SpaRoot)dist/**" />
    <ResolvedFileToPublish Include="@(DistFiles->'%(FullPath)')" Exclude="@(ResolvedFileToPublish)">
      <RelativePath>wwwroot/%(RecursiveDir)%(Filename)%(Extension)</RelativePath>
      <CopyToPublishDirectory>PreserveNewest</CopyToPublishDirectory>
      <ExcludeFromSingleFile>true</ExcludeFromSingleFile>
    </ResolvedFileToPublish>
  </ItemGroup>

  <!-- Build React app during publish -->
  <Target Name="PublishRunWebpack" AfterTargets="ComputeFilesToPublish">
    <Exec WorkingDirectory="$(SpaRoot)" Command="npm ci" />
    <Exec WorkingDirectory="$(SpaRoot)" Command="npm run build" />
  </Target>

</Project>
```

### 11. Troubleshooting Vite + ASP.NET Core

#### Issues and Solutions

##### Issue 1: Proxy Errors
**Problem**: API calls failing with proxy errors

**Solution**:
```javascript
// In vite.config.js, ensure correct target URL
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://localhost:7042',  // Match ASP.NET Core port
        secure: false,                     // Allow self-signed certs
        changeOrigin: true,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Sending Request:', req.method, req.url);
          });
        },
      }
    }
  }
});
```

##### Issue 2: CORS Issues
**Problem**: CORS errors when calling API

**Solution** (in ASP.NET Core Program.cs):
```csharp
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(
            "http://localhost:5173",    // Vite dev server
            "https://localhost:5173"    // Vite dev server HTTPS
        )
        .AllowAnyHeader()
        .AllowAnyMethod()
        .AllowCredentials();
    });
});
```

##### Issue 3: Build Path Issues
**Problem**: Static files not serving correctly

**Solution**:
```csharp
// In Program.cs, ensure correct order
app.UseDefaultFiles();
app.UseStaticFiles();
app.MapFallbackToFile("/index.html");  // Must be last
```

### 12. Performance Optimization

#### Vite Bundle Analysis

```bash
# Install bundle analyzer
npm install --save-dev rollup-plugin-visualizer

# Add to vite.config.js
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
    }),
  ],
});

# Build and analyze
npm run build
```

#### React Performance with Vite

```jsx
// Use React.memo for component optimization
import React, { memo } from 'react';

const WeatherCard = memo(({ forecast }) => (
  <div className="weather-card">
    <h3>{forecast.date}</h3>
    <p>{forecast.summary}</p>
    <span>{forecast.temperatureC}°C</span>
  </div>
));

// Use React.lazy for code splitting
const LazyChart = lazy(() => import('./components/WeatherChart'));
```

## gRPC Microservices Development

### 1. Create gRPC Service Project

```bash
# Create gRPC service
dotnet new grpc -n GrpcGreeterService
cd GrpcGreeterService

# Open in VS Code
code .
```

### 2. Define Service Contracts (Protocol Buffers)

Create or modify `Protos/greet.proto`:

```protobuf
syntax = "proto3";

option csharp_namespace = "GrpcGreeterService";

package greet;

// The greeting service definition
service Greeter {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply);
  
  // Sends multiple greetings
  rpc SayHelloToMany (stream HelloRequest) returns (stream HelloReply);
  
  // Get server info
  rpc GetServerInfo (Empty) returns (ServerInfo);
}

// The request message containing the user's name
message HelloRequest {
  string name = 1;
  string message = 2;
}

// The response message containing the greetings
message HelloReply {
  string message = 1;
  int32 timestamp = 2;
}

// Empty message
message Empty {}

// Server information
message ServerInfo {
  string version = 1;
  string environment = 2;
  int64 startup_time = 3;
}
```

### 3. Implement gRPC Service

Create `Services/GreeterService.cs`:

```csharp
using Grpc.Core;
using GrpcGreeterService;

namespace GrpcGreeterService.Services;

public class GreeterService : Greeter.GreeterBase
{
    private readonly ILogger<GreeterService> _logger;
    private static readonly DateTime _startupTime = DateTime.UtcNow;

    public GreeterService(ILogger<GreeterService> logger)
    {
        _logger = logger;
    }

    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
    {
        _logger.LogInformation("Received greeting request from {Name}", request.Name);
        
        return Task.FromResult(new HelloReply
        {
            Message = $"Hello {request.Name}! {request.Message}",
            Timestamp = (int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()
        });
    }

    public override async Task SayHelloToMany(IAsyncStreamReader<HelloRequest> requestStream,
        IServerStreamWriter<HelloReply> responseStream, ServerCallContext context)
    {
        await foreach (var request in requestStream.ReadAllAsync())
        {
            _logger.LogInformation("Streaming greeting to {Name}", request.Name);
            
            await responseStream.WriteAsync(new HelloReply
            {
                Message = $"Hello {request.Name}! {request.Message}",
                Timestamp = (int)DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            });
        }
    }

    public override Task<ServerInfo> GetServerInfo(Empty request, ServerCallContext context)
    {
        return Task.FromResult(new ServerInfo
        {
            Version = "1.0.0",
            Environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Unknown",
            StartupTime = ((DateTimeOffset)_startupTime).ToUnixTimeSeconds()
        });
    }
}
```

### 4. Configure gRPC in Program.cs

```csharp
using GrpcGreeterService.Services;

var builder = WebApplication.CreateBuilder(args);

// Add gRPC services
builder.Services.AddGrpc();

// Add health checks
builder.Services.AddGrpcHealthChecks();

var app = builder.Build();

// Configure gRPC pipeline
app.MapGrpcService<GreeterService>();
app.MapGrpcHealthChecksService();

// Enable gRPC reflection in development
if (app.Environment.IsDevelopment())
{
    app.MapGrpcReflectionService();
}

app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
```

### 5. Create gRPC Client

```bash
# Create console client project
dotnet new console -n GrpcGreeterClient
cd GrpcGreeterClient

# Add required NuGet packages
dotnet add package Grpc.Net.Client
dotnet add package Google.Protobuf
dotnet add package Grpc.Tools
```

#### Add Proto File to Client

Copy the `greet.proto` file to the client project and modify the project file:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <Protobuf Include="Protos\greet.proto" GrpcServices="Client" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="Grpc.Net.Client" Version="2.57.0" />
    <PackageReference Include="Google.Protobuf" Version="3.25.1" />
    <PackageReference Include="Grpc.Tools" Version="2.59.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
    </PackageReference>
  </ItemGroup>

</Project>
```

#### Implement Client Logic

```csharp
using Grpc.Net.Client;
using GrpcGreeterClient;

// Create gRPC channel
using var channel = GrpcChannel.ForAddress("https://localhost:7042");
var client = new Greeter.GreeterClient(channel);

try
{
    // Simple unary call
    var reply = await client.SayHelloAsync(new HelloRequest 
    { 
        Name = "World", 
        Message = "How are you?" 
    });
    Console.WriteLine($"Greeting: {reply.Message} (Timestamp: {reply.Timestamp})");

    // Get server info
    var serverInfo = await client.GetServerInfoAsync(new Empty());
    Console.WriteLine($"Server Version: {serverInfo.Version}");
    Console.WriteLine($"Environment: {serverInfo.Environment}");
    Console.WriteLine($"Startup Time: {DateTimeOffset.FromUnixTimeSeconds(serverInfo.StartupTime)}");

    Console.WriteLine("Press any key to exit...");
    Console.ReadKey();
}
catch (Exception ex)
{
    Console.WriteLine($"Error calling gRPC service: {ex.Message}");
}
```

### 6. Testing gRPC Services

#### Using grpcurl (Command Line Tool)

```bash
# Install grpcurl
sudo apt install grpcurl

# Test the service (requires gRPC reflection enabled)
grpcurl -plaintext localhost:5000 list
grpcurl -plaintext -d '{"name":"World","message":"Hello"}' localhost:5000 greet.Greeter/SayHello
```

#### Using BloomRPC GUI Tool

```bash
# Install BloomRPC
wget https://github.com/uw-labs/bloomrpc/releases/download/1.5.3/BloomRPC-1.5.3.AppImage
chmod +x BloomRPC-1.5.3.AppImage
./BloomRPC-1.5.3.AppImage
```

## Data Flow and Architecture

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  React Client   │    │  ASP.NET Core    │    │ gRPC Services    │
│  (TypeScript)   │────│    Gateway       │────│  (Microservices) │
│                 │    │                  │    │                  │
│ - UI Components │    │ - API Controllers│    │ - Business Logic │
│ - State Mgmt    │    │ - Authentication │    │ - Data Access    │
│ - HTTP Client   │    │ - Load Balancing │    │ - Proto Contracts│
└─────────────────┘    └──────────────────┘    └──────────────────┘
         │                        │                        │
         └─── HTTP/REST ──────────┘                        │
                                   └─── gRPC/HTTP2 ────────┘
```

### Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        Client Request Flow                       │
└──────────────────────────────────────────────────────────────────┘

1. User Action (React Frontend)
   │
   ├─► HTTP Request (REST API)
   │   │
   │   ├─► ASP.NET Core Controller
   │   │   │
   │   │   ├─► Authentication/Authorization
   │   │   │
   │   │   ├─► Business Logic
   │   │   │
   │   │   └─► gRPC Client Call
   │   │       │
   │   │       └─► Microservice (gRPC Server)
   │   │           │
   │   │           ├─► Data Processing
   │   │           │
   │   │           └─► Database/External APIs
   │   │
   │   └─► JSON Response
   │
   └─► Direct gRPC Call (Advanced scenarios)

┌──────────────────────────────────────────────────────────────────┐
│                     Response Flow (Reverse)                      │
└──────────────────────────────────────────────────────────────────┘

Database/APIs → gRPC Service → ASP.NET Core → React UI → User
```

### Microservices Communication Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    Service Mesh Architecture                    │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │ API Gateway │
                    │(ASP.NET Core│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
   │ User    │       │ Product   │      │ Order   │
   │ Service │       │ Service   │      │ Service │
   │ (gRPC)  │       │ (gRPC)    │      │ (gRPC)  │
   └─────────┘       └───────────┘      └─────────┘
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
   │ User    │       │ Product   │      │ Order   │
   │ Database│       │ Database  │      │ Database│
   └─────────┘       └───────────┘      └─────────┘
```

## Development Environment Setup

### 1. Local Development Workflow

#### Project Structure for Full-Stack Development

```
ProjectRoot/
├── src/
│   ├── Services/
│   │   ├── UserService/           # gRPC Microservice
│   │   ├── ProductService/        # gRPC Microservice
│   │   └── OrderService/          # gRPC Microservice
│   ├── Gateway/
│   │   └── ApiGateway/           # ASP.NET Core API Gateway
│   └── Client/
│       └── ReactApp/             # React + TypeScript Frontend
├── tests/
├── docker-compose.yml
├── docker-compose.override.yml
└── README.md
```

#### Development Commands

```bash
# Start all services in development mode
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Run individual services
# Backend API
cd src/Gateway/ApiGateway
dotnet run

# React Frontend
cd src/Client/ReactApp
npm start

# Individual microservice
cd src/Services/UserService
dotnet run
```

### 2. Environment Configuration

#### Development Environment (appsettings.Development.json)

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.AspNetCore.Hosting": "Information",
      "Microsoft.AspNetCore.Routing.EndpointMiddleware": "Information"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=DevDb;Trusted_Connection=true;"
  },
  "GrpcServices": {
    "UserService": "https://localhost:7001",
    "ProductService": "https://localhost:7002",
    "OrderService": "https://localhost:7003"
  },
  "AllowedHosts": "*",
  "Cors": {
    "AllowedOrigins": ["http://localhost:3000", "https://localhost:3001"]
  }
}
```

### 3. Hot Reload Configuration

#### ASP.NET Core Hot Reload

```bash
# Enable hot reload for backend
dotnet watch run

# With specific project
dotnet watch run --project src/Gateway/ApiGateway
```

#### React Hot Module Replacement

The Vite development server automatically enables HMR. Configuration in `vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    hmr: {
      overlay: true
    }
  }
});
```

## Production Deployment

### 1. Building for Production

#### React Application Build

```bash
cd ReactApp
npm run build

# This creates a 'dist' folder with optimized static files
```

#### ASP.NET Core Production Build

```bash
# Publish the application
dotnet publish -c Release -o ./publish

# Or with specific runtime
dotnet publish -c Release -r linux-x64 --self-contained -o ./publish
```

### 2. Production Configuration

#### Production appsettings (appsettings.Production.json)

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Server=prod-server;Database=ProdDb;User Id=produser;Password=***;"
  },
  "GrpcServices": {
    "UserService": "https://userservice.company.com",
    "ProductService": "https://productservice.company.com",
    "OrderService": "https://orderservice.company.com"
  },
  "AllowedHosts": "*.company.com",
  "UseHttpsRedirection": true
}
```

### 3. Reverse Proxy Configuration (Nginx)

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name myapp.company.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name myapp.company.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Serve static files (React build)
    location / {
        root /var/www/myapp/wwwroot;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection keep-alive;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # gRPC services
    location /grpc/ {
        grpc_pass grpc://localhost:7000;
        error_page 502 = /error502grpc;
    }

    location = /error502grpc {
        internal;
        default_type application/grpc;
        add_header grpc-status 14;
        add_header content-length 0;
        return 204;
    }
}
```

### 4. Systemd Service Configuration

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=MyApp ASP.NET Core Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/var/www/myapp/MyApp
Restart=on-failure
RestartSec=5
KillSignal=SIGINT
Environment=ASPNETCORE_ENVIRONMENT=Production
Environment=ASPNETCORE_URLS=http://localhost:5000

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable myapp.service
sudo systemctl start myapp.service
sudo systemctl status myapp.service
```

## Docker and Azure Deployment

### 1. Dockerfile for ASP.NET Core + React

#### Multi-stage Dockerfile

```dockerfile
# Use the official .NET SDK image for building
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env

# Install Node.js for React build
RUN curl -sL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

# Copy solution file
COPY *.sln ./

# Copy project files
COPY src/Gateway/ApiGateway/*.csproj ./src/Gateway/ApiGateway/
COPY src/Client/ReactApp/package*.json ./src/Client/ReactApp/
COPY src/Services/UserService/*.csproj ./src/Services/UserService/

# Restore packages
RUN dotnet restore

# Install npm dependencies
WORKDIR /app/src/Client/ReactApp
RUN npm ci

# Copy all source code
WORKDIR /app
COPY . .

# Build React application
WORKDIR /app/src/Client/ReactApp
RUN npm run build

# Build .NET application
WORKDIR /app
RUN dotnet publish src/Gateway/ApiGateway -c Release -o out

# Use runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build-env /app/out .

# Copy React build to wwwroot
COPY --from=build-env /app/src/Client/ReactApp/dist ./wwwroot

EXPOSE 8080
ENTRYPOINT ["dotnet", "ApiGateway.dll"]
```

## Troubleshooting

### Issues and Solutions

#### 1. SSL Certificate Issues

**Problem**: SSL certificate errors in development

**Solution**:
```bash
# Trust the ASP.NET Core HTTPS development certificate
dotnet dev-certs https --trust

# Clear existing certificates if needed
dotnet dev-certs https --clean
dotnet dev-certs https --trust
```

#### 2. Port Conflicts

**Problem**: Port already in use errors

**Solution**:
```bash
# Find process using port
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or change port in launchSettings.json
```

### Features

1. **Lightning-Fast Development with Vite**
   - Near-instantaneous Hot Module Replacement (HMR)
   - Optimized build process with tree shaking
   - Native ES modules support
   - Built-in TypeScript support

2. **Seamless API Integration**
   - Proxy configuration for development
   - CORS setup for cross-origin requests
   - Environment-specific configurations
   - Automatic error handling and retry mechanisms

3. **Production-Ready Deployment**
   - Optimized builds with code splitting
   - Static file serving from ASP.NET Core
   - Docker containerization
   - Multi-stage build process

4. **Developer Experience Enhancements**
   - VS Code debugging configuration
   - Automated setup scripts
   - Development workflow automation
   - Comprehensive error handling

### 📁 Project Structure

```
examples/ViteReactASP/
├── setup-vite-project.sh        # Automated project setup
├── dev-workflow.sh              # Development workflow automation
├── Dockerfile                   # Production container
├── docker-compose.yml           # Multi-service orchestration
├── docker-compose.dev.yml       # Development overrides
├── Server/
│   ├── Program.cs               # Enhanced backend configuration
│   └── Controllers/             # API controllers
└── Client/
    ├── vite.config.ts           # Advanced Vite configuration
    ├── package.json             # React + TypeScript dependencies
    ├── src/
    │   ├── App.tsx              # Feature-rich React component
    │   └── App.css              # Professional styling
    └── index.html               # Entry point
```

### 🛠️  Start Commands

```bash
# 1. Run the setup script
./examples/ViteReactASP/setup-vite-project.sh

# 2. Navigate to the created project
cd ViteReactASP

# 3. Start development environment
./dev-workflow.sh dev

# 4. Open browser to http://localhost:5173
```

### 🔧 Advanced Configurations

- **Vite Proxy Setup**: Seamless API communication during development
- **Environment Variables**: Development vs. production configurations
- **Build Optimization**: Code splitting, asset optimization, and caching
- **TypeScript Integration**: Full type safety across the stack
- **Docker Support**: Containerized deployment with multi-stage builds
- **Health Checks**: Monitoring and reliability features

---

## Database Configuration with PostgreSQL

### Setting up PostgreSQL Database

#### 1. Install PostgreSQL (Local Development)

```bash
# Install PostgreSQL on Debian/Ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database user and database
sudo -u postgres psql
CREATE USER appuser WITH PASSWORD 'devpassword123';
CREATE DATABASE ViteReactAspDb OWNER appuser;
GRANT ALL PRIVILEGES ON DATABASE ViteReactAspDb TO appuser;
\q
```

#### 2. Configure ASP.NET Core for PostgreSQL

First, install the required NuGet packages:

```bash
cd Server
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package Microsoft.EntityFrameworkCore.Design
dotnet add package Microsoft.EntityFrameworkCore.Tools
```

#### 3. Create Data Models

Create `Models/Contact.cs`:

```csharp
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ViteReactASP.Server.Models
{
    public class Contact
    {
        [Key]
        public int Id { get; set; }
        
        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = string.Empty;
        
        [Required]
        [Phone]
        [MaxLength(20)]
        public string PhoneNumber { get; set; } = string.Empty;
        
        [EmailAddress]
        [MaxLength(255)]
        public string? Email { get; set; }
        
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
        
        [MaxLength(500)]
        public string? Notes { get; set; }
    }
}
```

#### 4. Create Database Context

Create `Data/ApplicationDbContext.cs`:

```csharp
using Microsoft.EntityFrameworkCore;
using ViteReactASP.Server.Models;

namespace ViteReactASP.Server.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }
        
        public DbSet<Contact> Contacts { get; set; }
        
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            
            // Configure Contact entity
            modelBuilder.Entity<Contact>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Name).IsRequired().HasMaxLength(100);
                entity.Property(e => e.PhoneNumber).IsRequired().HasMaxLength(20);
                entity.Property(e => e.Email).HasMaxLength(255);
                entity.Property(e => e.Notes).HasMaxLength(500);
                entity.HasIndex(e => e.PhoneNumber).IsUnique();
                
                // Set default values
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("CURRENT_TIMESTAMP");
                entity.Property(e => e.UpdatedAt).HasDefaultValueSql("CURRENT_TIMESTAMP");
            });
            
            // Seed data
            modelBuilder.Entity<Contact>().HasData(
                new Contact 
                { 
                    Id = 1, 
                    Name = "John Doe", 
                    PhoneNumber = "+1234567890", 
                    Email = "john.doe@example.com",
                    Notes = "Sample contact"
                },
                new Contact 
                { 
                    Id = 2, 
                    Name = "Jane Smith", 
                    PhoneNumber = "+0987654321", 
                    Email = "jane.smith@example.com",
                    Notes = "Another sample contact"
                }
            );
        }
    }
}
```

#### 5. Update Program.cs for Database Configuration

```csharp
using Microsoft.EntityFrameworkCore;
using ViteReactASP.Server.Data;
using ViteReactASP.Server.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure PostgreSQL Database
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") 
    ?? "Host=localhost;Database=ViteReactAspDb;Username=appuser;Password=devpassword123";

builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));

// Add caching services
builder.Services.AddMemoryCache();
builder.Services.AddScoped<ICacheService, CacheService>();

// Configure CORS for Vite React frontend
builder.Services.AddCors(options =>
{
    options.AddPolicy("ViteReactPolicy", policy =>
    {
        policy.WithOrigins(
            "http://localhost:5173",
            "https://localhost:5173",
            "http://localhost:4173",
            "https://localhost:4173"
        )
        .AllowAnyHeader()
        .AllowAnyMethod()
        .AllowCredentials();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();
app.UseCors("ViteReactPolicy");
app.UseAuthorization();
app.MapControllers();

// Ensure database is created and migrated
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    context.Database.EnsureCreated();
}

app.Run();
```

## Implementing Caching in ASP.NET Core

### 1. Create Cache Service Interface

Create `Services/ICacheService.cs`:

```csharp
namespace ViteReactASP.Server.Services
{
    public interface ICacheService
    {
        Task<T?> GetAsync<T>(string key) where T : class;
        Task SetAsync<T>(string key, T value, TimeSpan? expiration = null) where T : class;
        Task RemoveAsync(string key);
        Task RemovePatternAsync(string pattern);
    }
}
```

### 2. Implement Cache Service

Create `Services/CacheService.cs`:

```csharp
using Microsoft.Extensions.Caching.Memory;
using System.Text.Json;

namespace ViteReactASP.Server.Services
{
    public class CacheService : ICacheService
    {
        private readonly IMemoryCache _memoryCache;
        private readonly ILogger<CacheService> _logger;
        private readonly HashSet<string> _cacheKeys;

        public CacheService(IMemoryCache memoryCache, ILogger<CacheService> logger)
        {
            _memoryCache = memoryCache;
            _logger = logger;
            _cacheKeys = new HashSet<string>();
        }

        public async Task<T?> GetAsync<T>(string key) where T : class
        {
            try
            {
                if (_memoryCache.TryGetValue(key, out var cachedValue))
                {
                    _logger.LogInformation("Cache hit for key: {Key}", key);
                    
                    if (cachedValue is string jsonString)
                    {
                        return JsonSerializer.Deserialize<T>(jsonString);
                    }
                    
                    return cachedValue as T;
                }

                _logger.LogInformation("Cache miss for key: {Key}", key);
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving from cache for key: {Key}", key);
                return null;
            }
        }

        public async Task SetAsync<T>(string key, T value, TimeSpan? expiration = null) where T : class
        {
            try
            {
                var options = new MemoryCacheEntryOptions();
                
                if (expiration.HasValue)
                {
                    options.SetAbsoluteExpiration(expiration.Value);
                }
                else
                {
                    options.SetAbsoluteExpiration(TimeSpan.FromMinutes(30)); // Default 30 minutes
                }

                options.RegisterPostEvictionCallback((key, value, reason, state) =>
                {
                    _cacheKeys.Remove(key.ToString() ?? "");
                    _logger.LogInformation("Cache entry evicted: {Key}, Reason: {Reason}", key, reason);
                });

                var serializedValue = JsonSerializer.Serialize(value);
                _memoryCache.Set(key, serializedValue, options);
                _cacheKeys.Add(key);
                
                _logger.LogInformation("Cache set for key: {Key}", key);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error setting cache for key: {Key}", key);
            }
        }

        public async Task RemoveAsync(string key)
        {
            try
            {
                _memoryCache.Remove(key);
                _cacheKeys.Remove(key);
                _logger.LogInformation("Cache removed for key: {Key}", key);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error removing cache for key: {Key}", key);
            }
        }

        public async Task RemovePatternAsync(string pattern)
        {
            try
            {
                var keysToRemove = _cacheKeys.Where(k => k.Contains(pattern)).ToList();
                foreach (var key in keysToRemove)
                {
                    _memoryCache.Remove(key);
                    _cacheKeys.Remove(key);
                }
                _logger.LogInformation("Removed {Count} cache entries matching pattern: {Pattern}", keysToRemove.Count, pattern);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error removing cache entries by pattern: {Pattern}", pattern);
            }
        }
    }
}
```

## CRUD Operations with ContactsController

Create `Controllers/ContactsController.cs`:

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using ViteReactASP.Server.Data;
using ViteReactASP.Server.Models;
using ViteReactASP.Server.Services;

namespace ViteReactASP.Server.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ContactsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ICacheService _cacheService;
        private readonly ILogger<ContactsController> _logger;
        private const string CACHE_KEY_PREFIX = "contact_";
        private const string CACHE_KEY_ALL = "contacts_all";

        public ContactsController(
            ApplicationDbContext context, 
            ICacheService cacheService,
            ILogger<ContactsController> logger)
        {
            _context = context;
            _cacheService = cacheService;
            _logger = logger;
        }

        // GET: api/contacts
        [HttpGet]
        public async Task<ActionResult<IEnumerable<Contact>>> GetContacts()
        {
            try
            {
                // Try to get from cache first
                var cachedContacts = await _cacheService.GetAsync<List<Contact>>(CACHE_KEY_ALL);
                if (cachedContacts != null)
                {
                    _logger.LogInformation("Retrieved {Count} contacts from cache", cachedContacts.Count);
                    return Ok(cachedContacts);
                }

                // Get from database
                var contacts = await _context.Contacts
                    .OrderBy(c => c.Name)
                    .ToListAsync();

                // Cache the results
                await _cacheService.SetAsync(CACHE_KEY_ALL, contacts, TimeSpan.FromMinutes(15));
                
                _logger.LogInformation("Retrieved {Count} contacts from database", contacts.Count);
                return Ok(contacts);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving contacts");
                return StatusCode(500, "Internal server error");
            }
        }

        // GET: api/contacts/5
        [HttpGet("{id}")]
        public async Task<ActionResult<Contact>> GetContact(int id)
        {
            try
            {
                var cacheKey = $"{CACHE_KEY_PREFIX}{id}";
                
                // Try cache first
                var cachedContact = await _cacheService.GetAsync<Contact>(cacheKey);
                if (cachedContact != null)
                {
                    _logger.LogInformation("Retrieved contact {Id} from cache", id);
                    return Ok(cachedContact);
                }

                // Get from database
                var contact = await _context.Contacts.FindAsync(id);
                if (contact == null)
                {
                    return NotFound();
                }

                // Cache the result
                await _cacheService.SetAsync(cacheKey, contact, TimeSpan.FromMinutes(30));
                
                _logger.LogInformation("Retrieved contact {Id} from database", id);
                return Ok(contact);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving contact {Id}", id);
                return StatusCode(500, "Internal server error");
            }
        }

        // POST: api/contacts
        [HttpPost]
        public async Task<ActionResult<Contact>> CreateContact(Contact contact)
        {
            try
            {
                if (!ModelState.IsValid)
                {
                    return BadRequest(ModelState);
                }

                // Check if phone number already exists
                var existingContact = await _context.Contacts
                    .FirstOrDefaultAsync(c => c.PhoneNumber == contact.PhoneNumber);
                
                if (existingContact != null)
                {
                    return Conflict("A contact with this phone number already exists");
                }

                contact.CreatedAt = DateTime.UtcNow;
                contact.UpdatedAt = DateTime.UtcNow;

                _context.Contacts.Add(contact);
                await _context.SaveChangesAsync();

                // Cache the new contact
                var cacheKey = $"{CACHE_KEY_PREFIX}{contact.Id}";
                await _cacheService.SetAsync(cacheKey, contact, TimeSpan.FromMinutes(30));
                
                // Invalidate the all contacts cache
                await _cacheService.RemoveAsync(CACHE_KEY_ALL);

                _logger.LogInformation("Created contact {Id} - {Name}", contact.Id, contact.Name);
                return CreatedAtAction(nameof(GetContact), new { id = contact.Id }, contact);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error creating contact");
                return StatusCode(500, "Internal server error");
            }
        }

        // PUT: api/contacts/5
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateContact(int id, Contact contact)
        {
            try
            {
                if (id != contact.Id)
                {
                    return BadRequest("ID mismatch");
                }

                if (!ModelState.IsValid)
                {
                    return BadRequest(ModelState);
                }

                var existingContact = await _context.Contacts.FindAsync(id);
                if (existingContact == null)
                {
                    return NotFound();
                }

                // Check if phone number is being changed and if it conflicts
                if (existingContact.PhoneNumber != contact.PhoneNumber)
                {
                    var phoneConflict = await _context.Contacts
                        .FirstOrDefaultAsync(c => c.PhoneNumber == contact.PhoneNumber && c.Id != id);
                    
                    if (phoneConflict != null)
                    {
                        return Conflict("A contact with this phone number already exists");
                    }
                }

                existingContact.Name = contact.Name;
                existingContact.PhoneNumber = contact.PhoneNumber;
                existingContact.Email = contact.Email;
                existingContact.Notes = contact.Notes;
                existingContact.UpdatedAt = DateTime.UtcNow;

                await _context.SaveChangesAsync();

                // Update cache
                var cacheKey = $"{CACHE_KEY_PREFIX}{id}";
                await _cacheService.SetAsync(cacheKey, existingContact, TimeSpan.FromMinutes(30));
                
                // Invalidate the all contacts cache
                await _cacheService.RemoveAsync(CACHE_KEY_ALL);

                _logger.LogInformation("Updated contact {Id} - {Name}", id, contact.Name);
                return Ok(existingContact);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating contact {Id}", id);
                return StatusCode(500, "Internal server error");
            }
        }

        // DELETE: api/contacts/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteContact(int id)
        {
            try
            {
                var contact = await _context.Contacts.FindAsync(id);
                if (contact == null)
                {
                    return NotFound();
                }

                _context.Contacts.Remove(contact);
                await _context.SaveChangesAsync();

                // Remove from cache
                var cacheKey = $"{CACHE_KEY_PREFIX}{id}";
                await _cacheService.RemoveAsync(cacheKey);
                
                // Invalidate the all contacts cache
                await _cacheService.RemoveAsync(CACHE_KEY_ALL);

                _logger.LogInformation("Deleted contact {Id} - {Name}", id, contact.Name);
                return NoContent();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting contact {Id}", id);
                return StatusCode(500, "Internal server error");
            }
        }

        // GET: api/contacts/search/{term}
        [HttpGet("search/{term}")]
        public async Task<ActionResult<IEnumerable<Contact>>> SearchContacts(string term)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(term))
                {
                    return BadRequest("Search term cannot be empty");
                }

                var cacheKey = $"search_{term.ToLower()}";
                
                // Try cache first
                var cachedResults = await _cacheService.GetAsync<List<Contact>>(cacheKey);
                if (cachedResults != null)
                {
                    return Ok(cachedResults);
                }

                // Search database
                var contacts = await _context.Contacts
                    .Where(c => c.Name.Contains(term) || 
                               c.PhoneNumber.Contains(term) || 
                               (c.Email != null && c.Email.Contains(term)))
                    .OrderBy(c => c.Name)
                    .ToListAsync();

                // Cache search results for shorter time
                await _cacheService.SetAsync(cacheKey, contacts, TimeSpan.FromMinutes(5));
                
                return Ok(contacts);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error searching contacts with term: {Term}", term);
                return StatusCode(500, "Internal server error");
            }
        }
    }
}
```

## Database Migrations

Run these commands to set up the database:

```bash
# Create migration
cd Server
dotnet ef migrations add InitialCreate

# Update database
dotnet ef database update

# Check database status
dotnet ef database --info
```

## cURL API Testing Examples

### Basic Contact Operations

#### 1. Get All Contacts
```bash
curl -X GET "https://localhost:7042/api/contacts" \
  -H "accept: application/json" \
  -k
```

#### 2. Create New Contact
```bash
curl -X POST "https://localhost:7042/api/contacts" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -k \
  -d '{
    "name": "Alice Johnson",
    "phoneNumber": "+1555123456",
    "email": "alice.johnson@example.com",
    "notes": "IoT project contact"
  }'
```

#### 3. Get Contact by ID
```bash
curl -X GET "https://localhost:7042/api/contacts/1" \
  -H "accept: application/json" \
  -k
```

#### 4. Update Contact
```bash
curl -X PUT "https://localhost:7042/api/contacts/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -k \
  -d '{
    "id": 1,
    "name": "Alice Johnson Updated",
    "phoneNumber": "+1555123456",
    "email": "alice.updated@example.com",
    "notes": "Updated IoT project contact"
  }'
```

#### 5. Search Contacts
```bash
curl -X GET "https://localhost:7042/api/contacts/search/Alice" \
  -H "accept: application/json" \
  -k
```

#### 6. Delete Contact
```bash
curl -X DELETE "https://localhost:7042/api/contacts/1" \
  -H "accept: application/json" \
  -k
```

### Advanced Testing with Multiple Contacts

#### Bulk Create Script
```bash
#!/bin/bash
# Create multiple contacts for testing

BASE_URL="https://localhost:7042/api/contacts"

contacts=(
  '{"name": "Bob Smith", "phoneNumber": "+1555987654", "email": "bob@example.com"}'
  '{"name": "Carol Davis", "phoneNumber": "+1555456789", "email": "carol@example.com"}'
  '{"name": "David Wilson", "phoneNumber": "+1555321654", "email": "david@example.com"}'
  '{"name": "Emma Brown", "phoneNumber": "+1555654321", "email": "emma@example.com"}'
)

for contact in "${contacts[@]}"; do
  echo "Creating contact: $contact"
  curl -X POST "$BASE_URL" \
    -H "Content-Type: application/json" \
    -k -s \
    -d "$contact" | jq '.'
  echo "---"
done
```

## Caching Use Cases

### 1. Performance Optimization
- **Scenario**: Frequently accessed contact lists
- **Benefit**: Reduces database load by 60-80% for repeated queries
- **Implementation**: Cache contact lists for 15 minutes

### 2. Search Results Caching
- **Scenario**: Common search terms (e.g., names, phone prefixes)
- **Benefit**: Instant response for repeated searches
- **Implementation**: Cache search results for 5 minutes

### 3. Individual Contact Caching
- **Scenario**: Contact details viewed multiple times
- **Benefit**: Immediate load times for popular contacts
- **Implementation**: Cache individual contacts for 30 minutes

### 4. Cache Invalidation Strategy
- **Create/Update/Delete**: Invalidate related cache entries
- **Bulk Operations**: Clear pattern-matched cache keys
- **Time-based**: Automatic expiration based on data volatility

### Testing Cache Performance

```bash
# Test cache hit/miss
echo "First request (cache miss):"
time curl -X GET "https://localhost:7042/api/contacts" -k -s | jq 'length'

echo "Second request (cache hit):"
time curl -X GET "https://localhost:7042/api/contacts" -k -s | jq 'length'

# Create new contact (invalidates cache)
curl -X POST "https://localhost:7042/api/contacts" \
  -H "Content-Type: application/json" \
  -k -s \
  -d '{"name": "Cache Test", "phoneNumber": "+1555999999"}' > /dev/null

echo "Third request after cache invalidation:"
time curl -X GET "https://localhost:7042/api/contacts" -k -s | jq 'length'
```

## Configuration Files

### appsettings.json Configuration

Create or update `Server/appsettings.json`:

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.EntityFrameworkCore.Database.Command": "Information"
    }
  },
  "AllowedHosts": "*",
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=ViteReactAspDb;Username=appuser;Password=devpassword123",
    "Redis": "localhost:6379"
  },
  "CacheSettings": {
    "DefaultExpirationMinutes": 30,
    "ContactCacheMinutes": 30,
    "SearchCacheMinutes": 5,
    "ContactListCacheMinutes": 15
  },
  "ApiSettings": {
    "MaxPageSize": 100,
    "DefaultPageSize": 20,
    "EnableDetailedErrors": true
  }
}
```

### appsettings.Development.json

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "System": "Information",
      "Microsoft": "Information",
      "Microsoft.EntityFrameworkCore.Database.Command": "Information"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=ViteReactAspDb_Dev;Username=appuser;Password=devpassword123"
  },
  "CacheSettings": {
    "DefaultExpirationMinutes": 5,
    "ContactCacheMinutes": 5,
    "SearchCacheMinutes": 2,
    "ContactListCacheMinutes": 3
  }
}
```

### Docker Environment Configuration

Update `docker-compose.yml` to include database configuration:

```yaml
version: '3.8'

services:
  # ASP.NET Core Application
  vite-react-asp:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - ASPNETCORE_URLS=http://+:8080
      - ConnectionStrings__DefaultConnection=Host=postgres;Database=ViteReactAspDb;Username=appuser;Password=devpassword123
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - app-network

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ViteReactAspDb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: devpassword123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d ViteReactAspDb"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - app-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass devpassword123
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

## Complete Testing Workflow

### 1. Automated Testing Script

Create `test-api.sh`:

```bash
#!/bin/bash

BASE_URL="https://localhost:7042"
API_URL="$BASE_URL/api/contacts"

echo " Testing ASP.NET Core API with PostgreSQL and Caching"
echo "========================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_passed=0
test_failed=0

run_test() {
    local test_name="$1"
    local curl_command="$2"
    local expected_status="$3"
    
    echo -n "Testing $test_name... "
    
    response=$(eval $curl_command)
    status_code=$(echo "$response" | tail -n1)
    
    if [[ "$status_code" -eq "$expected_status" ]]; then
        echo -e "${GREEN}PASSED${NC}"
        ((test_passed++))
    else
        echo -e "${RED}FAILED${NC} (Expected: $expected_status, Got: $status_code)"
        ((test_failed++))
    fi
}

# Test 1: Health Check
run_test "Health Check" \
    "curl -k -s -w '%{http_code}' -o /dev/null '$BASE_URL/health'" \
    200

# Test 2: Get All Contacts (initially empty or seeded)
run_test "Get All Contacts" \
    "curl -k -s -w '%{http_code}' -o /dev/null '$API_URL'" \
    200

# Test 3: Create New Contact
contact_data='{"name": "John Test", "phoneNumber": "+1555000001", "email": "john.test@example.com", "notes": "Test contact"}'
run_test "Create New Contact" \
    "curl -k -s -w '%{http_code}' -o /dev/null -X POST '$API_URL' -H 'Content-Type: application/json' -d '$contact_data'" \
    201

# Test 4: Get Contact by ID (assuming ID 1 exists)
run_test "Get Contact by ID" \
    "curl -k -s -w '%{http_code}' -o /dev/null '$API_URL/1'" \
    200

# Test 5: Search Contacts
run_test "Search Contacts" \
    "curl -k -s -w '%{http_code}' -o /dev/null '$API_URL/search/John'" \
    200

# Test 6: Update Contact
update_data='{"id": 1, "name": "John Updated", "phoneNumber": "+1555000001", "email": "john.updated@example.com"}'
run_test "Update Contact" \
    "curl -k -s -w '%{http_code}' -o /dev/null -X PUT '$API_URL/1' -H 'Content-Type: application/json' -d '$update_data'" \
    200

# Test 7: Test Caching Performance
echo ""
echo " Testing Cache Performance:"
echo "First request (cache miss):"
time curl -k -s "$API_URL" | jq 'length' 2>/dev/null || echo "Response received"

echo "Second request (cache hit - should be faster):"
time curl -k -s "$API_URL" | jq 'length' 2>/dev/null || echo "Response received"

# Summary
echo ""
echo "========================================================="
echo "Test Results Summary:"
echo -e "${GREEN}Passed: $test_passed${NC}"
echo -e "${RED}Failed: $test_failed${NC}"

if [[ $test_failed -eq 0 ]]; then
    echo -e "${GREEN}All tests passed! 🎉${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check the output above.${NC}"
    exit 1
fi
```

### 2. Load Testing with cURL

```bash
#!/bin/bash
# Load test script to verify caching effectiveness

echo " Load Testing API with Cache Analysis"
echo "======================================="

API_URL="https://localhost:7042/api/contacts"
REQUESTS=50
CONCURRENT=10

# Create multiple contacts first
echo "Creating test data..."
for i in {1..10}; do
    curl -k -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"Load Test User $i\", \"phoneNumber\": \"+155500000$i\"}" > /dev/null
done

echo "Running load test..."

# Function to make requests and measure time
make_request() {
    start_time=$(date +%s.%3N)
    curl -k -s "$API_URL" > /dev/null
    end_time=$(date +%s.%3N)
    echo "scale=3; $end_time - $start_time" | bc
}

# Run sequential requests to measure cache effectiveness
total_time=0
for i in $(seq 1 $REQUESTS); do
    response_time=$(make_request)
    total_time=$(echo "scale=3; $total_time + $response_time" | bc)
    echo "Request $i: ${response_time}s"
done

average_time=$(echo "scale=3; $total_time / $REQUESTS" | bc)
echo ""
echo "Average response time: ${average_time}s"
echo "Total time for $REQUESTS requests: ${total_time}s"
```

## Azure Cloud Deployment

This section covers deploying your React + ASP.NET Core application to Microsoft Azure cloud platform, including security configuration and resource allocation.

### Prerequisites - Azure Tools Installation

#### 1. Install Azure CLI

```bash
# For Debian/Ubuntu Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version

# Alternative: Install via package manager
sudo apt-get update
sudo apt-get install ca-certificates curl apt-transport-https lsb-release gnupg
curl -sL https://packages.microsoft.com/keys/microsoft.asc | \
    gpg --dearmor | \
    sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
    sudo tee /etc/apt/sources.list.d/azure-cli.list
sudo apt-get update
sudo apt-get install azure-cli
```

#### 2. Install Azure Developer CLI (azd)

```bash
# Install Azure Developer CLI
curl -fsSL https://aka.ms/install-azd.sh | bash

# Verify installation
azd version
```

#### 3. Install Docker (if not already installed)

```bash
# Install Docker
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt install docker-ce

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 4. Install Terraform (Optional - for Infrastructure as Code)

```bash
# Install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### Azure Login and Subscription Setup

#### 1. Login to Azure

```bash
# Interactive login
az login

# Login with specific tenant (if required)
az login --tenant TENANT_ID

# List available subscriptions
az account list --output table

# Set active subscription
az account set --subscription "Your Subscription Name"
```

#### 2. Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="rg-vite-react-asp"
LOCATION="East US"

# Create resource group
az group create \
    --name $RESOURCE_GROUP \
    --location "$LOCATION"
```

### Deployment Option 1: Azure App Service (Recommended for beginners)

#### 1. Create App Service Plan

```bash
# Variables for App Service
APP_SERVICE_PLAN="plan-vite-react-asp"
WEB_APP_NAME="webapp-vite-react-asp-$(date +%s)"  # Unique name

# Create App Service Plan (B1 Basic tier)
az appservice plan create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_SERVICE_PLAN \
    --location "$LOCATION" \
    --sku B1 \
    --is-linux
```

#### 2. Create Web App

```bash
# Create web app with .NET 8 runtime
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $WEB_APP_NAME \
    --runtime "DOTNETCORE:8.0"
```

#### 3. Configure Application Settings

```bash
# Set application settings
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        ASPNETCORE_ENVIRONMENT="Production" \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE="false" \
        WEBSITE_HTTPLOGGING_RETENTION_DAYS="3"
```

#### 4. Deploy Application

##### Option A: Deploy using Azure CLI

```bash
# Build and publish the application
dotnet publish -c Release -o ./publish

# Create deployment package
cd publish
zip -r ../app.zip .
cd ..

# Deploy to Azure
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --src app.zip
```

##### Option B: Deploy using GitHub Actions

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Build and deploy ASP.NET Core app to Azure Web App

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  AZURE_WEBAPP_NAME: webapp-vite-react-asp    # Replace with your app name
  AZURE_WEBAPP_PACKAGE_PATH: '.'
  DOTNET_VERSION: '8.0.x'

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up .NET Core
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: Client/package-lock.json

      - name: Install React dependencies
        run: |
          cd Client
          npm ci

      - name: Build React application
        run: |
          cd Client
          npm run build

      - name: Build ASP.NET Core app
        run: dotnet build --configuration Release

      - name: dotnet publish
        run: dotnet publish -c Release -o ${{env.DOTNET_ROOT}}/myapp

      - name: Upload artifact for deployment job
        uses: actions/upload-artifact@v3
        with:
          name: .net-app
          path: ${{env.DOTNET_ROOT}}/myapp

  deploy:
    permissions:
      contents: none
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: 'Production'
      url: ${{ steps.deploy-to-webapp.outputs.webapp-url }}

    steps:
      - name: Download artifact from build job
        uses: actions/download-artifact@v3
        with:
          name: .net-app

      - name: Deploy to Azure Web App
        id: deploy-to-webapp
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          slot-name: 'Production'
          package: .
          publish-profile: ${{ secrets.AZUREAPPSERVICE_PUBLISHPROFILE }}
```

### Deployment Option 2: Azure Container Instances (ACI)

#### 1. Create Azure Container Registry

```bash
# Variables
ACR_NAME="acrvitereactasp$(date +%s)"
IMAGE_NAME="vite-react-asp"

# Create Azure Container Registry
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
```

#### 2. Build and Push Docker Image

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build image (from project root directory)
docker build -t $IMAGE_NAME .

# Tag image
docker tag $IMAGE_NAME $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Push image
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest
```

#### 3. Deploy to Azure Container Instances

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Create container instance
az container create \
    --resource-group $RESOURCE_GROUP \
    --name "aci-vite-react-asp" \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
    --registry-login-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --dns-name-label "vite-react-asp-$(date +%s)" \
    --ports 8080 \
    --memory 1.5 \
    --cpu 1
```

### Deployment Option 3: Azure Kubernetes Service (AKS) - Production Scale

#### 1. Create AKS Cluster

```bash
# Variables
AKS_CLUSTER_NAME="aks-vite-react-asp"
NODE_COUNT=2

# Create AKS cluster
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME \
    --node-count $NODE_COUNT \
    --node-vm-size Standard_DS2_v2 \
    --attach-acr $ACR_NAME \
    --generate-ssh-keys

# Get AKS credentials
az aks get-credentials \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME
```

#### 2. Create Kubernetes Deployment Manifests

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vite-react-asp-deployment
  labels:
    app: vite-react-asp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vite-react-asp
  template:
    metadata:
      labels:
        app: vite-react-asp
    spec:
      containers:
      - name: vite-react-asp
        image: acrvitereactasp.azurecr.io/vite-react-asp:latest
        ports:
        - containerPort: 8080
        env:
        - name: ASPNETCORE_ENVIRONMENT
          value: "Production"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: vite-react-asp-service
spec:
  selector:
    app: vite-react-asp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

#### 3. Deploy to AKS

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s-deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods

# Get external IP
kubectl get service vite-react-asp-service
```

### Database Configuration for Azure

#### 1. Azure SQL Database

```bash
# Variables
SQL_SERVER_NAME="sqlserver-vite-react-asp-$(date +%s)"
SQL_DATABASE_NAME="db-vite-react-asp"
ADMIN_USERNAME="sqladmin"
ADMIN_PASSWORD="YourStrongP@ssw0rd123!"

# Create SQL Server
az sql server create \
    --resource-group $RESOURCE_GROUP \
    --name $SQL_SERVER_NAME \
    --location "$LOCATION" \
    --admin-user $ADMIN_USERNAME \
    --admin-password $ADMIN_PASSWORD

# Create SQL Database
az sql db create \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name $SQL_DATABASE_NAME \
    --service-objective Basic

# Configure firewall (allow Azure services)
az sql server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name "AllowAzureServices" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Get connection string
az sql db show-connection-string \
    --client ado.net \
    --name $SQL_DATABASE_NAME \
    --server $SQL_SERVER_NAME
```

#### 2. Azure Database for PostgreSQL

```bash
# Variables
POSTGRES_SERVER_NAME="postgres-vite-react-asp-$(date +%s)"
POSTGRES_DATABASE_NAME="postgres"
ADMIN_USERNAME="postgresadmin"
ADMIN_PASSWORD="YourStrongP@ssw0rd123!"

# Create PostgreSQL server
az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $POSTGRES_SERVER_NAME \
    --location "$LOCATION" \
    --admin-user $ADMIN_USERNAME \
    --admin-password $ADMIN_PASSWORD \
    --sku-name Standard_B1ms \
    --storage-size 32 \
    --version 14

# Create database
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_SERVER_NAME \
    --database-name $POSTGRES_DATABASE_NAME
```

### Security Configuration

#### 1. Enable HTTPS and SSL

```bash
# For App Service - HTTPS is enabled by default
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --https-only true

# Upload SSL certificate (optional custom domain)
az webapp config ssl upload \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --certificate-file /path/to/certificate.pfx \
    --certificate-password "certificate-password"
```

#### 2. Configure Azure Active Directory Authentication

```bash
# Create Azure AD app registration
az ad app create \
    --display-name "ViteReactAspApp" \
    --homepage "https://$WEB_APP_NAME.azurewebsites.net" \
    --identifier-uris "https://$WEB_APP_NAME.azurewebsites.net"

# Configure App Service authentication
az webapp auth config-version upgrade \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME

# Enable Azure AD authentication
az webapp auth microsoft update \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --client-id "your-client-id" \
    --client-secret "your-client-secret" \
    --tenant-id "your-tenant-id"
```

#### 3. Configure Key Vault for Secrets Management

```bash
# Variables
KEY_VAULT_NAME="kv-vite-react-asp-$(date +%s)"

# Create Key Vault
az keyvault create \
    --resource-group $RESOURCE_GROUP \
    --name $KEY_VAULT_NAME \
    --location "$LOCATION" \
    --sku Standard

# Store database connection string in Key Vault
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "DatabaseConnectionString" \
    --value "Server=$SQL_SERVER_NAME.database.windows.net;Database=$SQL_DATABASE_NAME;User Id=$ADMIN_USERNAME;Password=$ADMIN_PASSWORD;"

# Grant App Service access to Key Vault
WEB_APP_PRINCIPAL_ID=$(az webapp identity assign \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query principalId \
    --output tsv)

az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $WEB_APP_PRINCIPAL_ID \
    --secret-permissions get
```

### Resource Scaling and Performance

#### 1. Auto Scaling Configuration

```bash
# Create autoscale profile for App Service Plan
az monitor autoscale create \
    --resource-group $RESOURCE_GROUP \
    --resource $APP_SERVICE_PLAN \
    --resource-type Microsoft.Web/serverfarms \
    --name "autoscale-vite-react-asp" \
    --min-count 1 \
    --max-count 5 \
    --count 2

# Add CPU-based scale rule
az monitor autoscale rule create \
    --resource-group $RESOURCE_GROUP \
    --autoscale-name "autoscale-vite-react-asp" \
    --condition "Percentage CPU > 75 avg 5m" \
    --scale out 1

az monitor autoscale rule create \
    --resource-group $RESOURCE_GROUP \
    --autoscale-name "autoscale-vite-react-asp" \
    --condition "Percentage CPU < 25 avg 5m" \
    --scale in 1
```

#### 2. CDN Configuration for Static Assets

```bash
# Variables
CDN_PROFILE_NAME="cdn-vite-react-asp"
CDN_ENDPOINT_NAME="cdn-endpoint-$(date +%s)"

# Create CDN profile
az cdn profile create \
    --resource-group $RESOURCE_GROUP \
    --name $CDN_PROFILE_NAME \
    --sku Standard_Microsoft

# Create CDN endpoint
az cdn endpoint create \
    --resource-group $RESOURCE_GROUP \
    --profile-name $CDN_PROFILE_NAME \
    --name $CDN_ENDPOINT_NAME \
    --origin $WEB_APP_NAME.azurewebsites.net \
    --origin-host-header $WEB_APP_NAME.azurewebsites.net
```

### Monitoring and Logging

#### 1. Application Insights Setup

```bash
# Variables
APP_INSIGHTS_NAME="appi-vite-react-asp"

# Create Application Insights
az extension add --name application-insights
az monitor app-insights component create \
    --app $APP_INSIGHTS_NAME \
    --location "$LOCATION" \
    --resource-group $RESOURCE_GROUP \
    --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app $APP_INSIGHTS_NAME \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey \
    --output tsv)

# Configure App Service with Application Insights
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY" \
        APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSTRUMENTATION_KEY"
```

#### 2. Log Analytics Workspace

```bash
# Variables
LOG_ANALYTICS_WORKSPACE="law-vite-react-asp"

# Create Log Analytics workspace
az monitor log-analytics workspace create \
    --resource-group $RESOURCE_GROUP \
    --workspace-name $LOG_ANALYTICS_WORKSPACE \
    --location "$LOCATION"
```

### Environment-Specific Configuration

#### Development Environment (appsettings.Development.json)

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=ViteReactAspDev;Trusted_Connection=true;TrustServerCertificate=true"
  },
  "ApplicationInsights": {
    "InstrumentationKey": ""
  }
}
```

#### Production Environment (appsettings.Production.json)

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.EntityFrameworkCore": "Error"
    },
    "ApplicationInsights": {
      "LogLevel": {
        "Default": "Information"
      }
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "@Microsoft.KeyVault(SecretUri=https://your-keyvault.vault.azure.net/secrets/DatabaseConnectionString/)"
  },
  "ApplicationInsights": {
    "InstrumentationKey": "your-instrumentation-key"
  },
  "AllowedHosts": ["yourdomain.com", "*.azurewebsites.net"]
}
```

### Cost Management and Optimization

#### 1. Resource Tagging for Cost Tracking

```bash
# Apply cost center tags
az group update \
    --name $RESOURCE_GROUP \
    --tags \
        Environment="Production" \
        Project="ViteReactAsp" \
        CostCenter="IT" \
        Owner="DevTeam"

# Tag individual resources
az webapp update \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --tags \
        Environment="Production" \
        Tier="Web"
```

#### 2. Budget Alerts

```bash
# Create budget (requires billing account scope)
az consumption budget create \
    --budget-name "ViteReactAsp-Budget" \
    --amount 100 \
    --time-grain Monthly \
    --category Cost \
    --resource-group-filter $RESOURCE_GROUP
```

### Backup and Disaster Recovery

#### 1. Database Backup Configuration

```bash
# Configure automated backups for SQL Database (enabled by default)
az sql db show \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name $SQL_DATABASE_NAME \
    --query "{Name:name, Status:status, BackupRetentionPeriod:backupRetentionPeriod}"
```

#### 2. App Service Backup

```bash
# Create storage account for backups
STORAGE_ACCOUNT_NAME="stbackup$(date +%s | tail -c 10)"

az storage account create \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku Standard_LRS

# Configure App Service backup (requires Premium tier)
# Note: Upgrade to Premium tier first if needed
az appservice plan update \
    --resource-group $RESOURCE_GROUP \
    --name $APP_SERVICE_PLAN \
    --sku P1V2
```

### Deployment Validation and Testing

#### 1. Health Check Endpoints

Add to your ASP.NET Core application:

```csharp
// In Program.cs
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = async (context, report) =>
    {
        var result = JsonSerializer.Serialize(new
        {
            status = report.Status.ToString(),
            checks = report.Entries.Select(entry => new
            {
                name = entry.Key,
                status = entry.Value.Status.ToString(),
                exception = entry.Value.Exception?.Message,
                duration = entry.Value.Duration.ToString()
            })
        });
        context.Response.ContentType = MediaTypeNames.Application.Json;
        await context.Response.WriteAsync(result);
    }
});
```

#### 2. Load Testing with Azure Load Testing

```bash
# Create Azure Load Testing resource
az extension add --name load

az load test create \
    --name "loadtest-vite-react-asp" \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION"
```

### CI/CD Pipeline Configuration

#### Azure DevOps YAML Pipeline

Create `azure-pipelines.yml`:

```yaml
trigger:
- main

variables:
  buildConfiguration: 'Release'
  azureSubscription: 'your-service-connection'
  webAppName: 'webapp-vite-react-asp'

stages:
- stage: Build
  displayName: Build stage
  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: 'ubuntu-latest'

    steps:
    - task: UseDotNet@2
      displayName: 'Use .NET Core sdk'
      inputs:
        packageType: 'sdk'
        version: '8.0.x'

    - task: NodeTool@0
      displayName: 'Install Node.js'
      inputs:
        versionSpec: '18.x'

    - task: Npm@1
      displayName: 'npm install'
      inputs:
        workingDir: 'Client'
        command: 'ci'

    - task: Npm@1
      displayName: 'npm build'
      inputs:
        workingDir: 'Client'
        command: 'custom'
        customCommand: 'run build'

    - task: DotNetCoreCLI@2
      displayName: 'Build project'
      inputs:
        command: 'build'
        projects: '**/*.csproj'
        arguments: '--configuration $(buildConfiguration)'

    - task: DotNetCoreCLI@2
      displayName: 'Publish project'
      inputs:
        command: 'publish'
        publishWebProjects: true
        arguments: '--configuration $(buildConfiguration) --output $(Build.ArtifactStagingDirectory)'

    - task: PublishBuildArtifacts@1
      displayName: 'Publish artifacts'
      inputs:
        pathtoPublish: '$(Build.ArtifactStagingDirectory)'
        artifactName: 'drop'

- stage: Deploy
  displayName: Deploy stage
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: Deploy
    displayName: Deploy
    environment: 'production'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            displayName: 'Deploy Azure Web App'
            inputs:
              azureSubscription: $(azureSubscription)
              appName: $(webAppName)
              package: '$(Pipeline.Workspace)/drop/**/*.zip'
```

### Deployment Script

Create `deploy-to-azure.sh`:

```bash
#!/bin/bash

# Azure Deployment Script for Vite + React + ASP.NET Core
set -e

# Configuration
RESOURCE_GROUP="rg-vite-react-asp"
LOCATION="East US"
APP_SERVICE_PLAN="plan-vite-react-asp"
WEB_APP_NAME="webapp-vite-react-asp-$(date +%s)"
SQL_SERVER_NAME="sqlserver-vite-react-asp-$(date +%s)"
SQL_DATABASE_NAME="db-vite-react-asp"
KEY_VAULT_NAME="kv-vite-react-asp-$(date +%s)"
ADMIN_USERNAME="sqladmin"
ADMIN_PASSWORD="YourStrongP@ssw0rd123!"

echo " Starting Azure deployment..."

# Login and set subscription
echo " Logging into Azure..."
az login
az account set --subscription "Your Subscription Name"

# Create resource group
echo " Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Create App Service Plan
echo "⚡ Creating App Service Plan..."
az appservice plan create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_SERVICE_PLAN \
    --location "$LOCATION" \
    --sku B1 \
    --is-linux

# Create Web App
echo " Creating Web App..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $WEB_APP_NAME \
    --runtime "DOTNETCORE:8.0"

# Create SQL Database
echo " Creating SQL Database..."
az sql server create \
    --resource-group $RESOURCE_GROUP \
    --name $SQL_SERVER_NAME \
    --location "$LOCATION" \
    --admin-user $ADMIN_USERNAME \
    --admin-password $ADMIN_PASSWORD

az sql db create \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name $SQL_DATABASE_NAME \
    --service-objective Basic

# Configure firewall
az sql server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name "AllowAzureServices" \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Create Key Vault
echo "🔐 Creating Key Vault..."
az keyvault create \
    --resource-group $RESOURCE_GROUP \
    --name $KEY_VAULT_NAME \
    --location "$LOCATION" \
    --sku Standard

# Store connection string in Key Vault
CONNECTION_STRING="Server=$SQL_SERVER_NAME.database.windows.net;Database=$SQL_DATABASE_NAME;User Id=$ADMIN_USERNAME;Password=$ADMIN_PASSWORD;Encrypt=true;TrustServerCertificate=false;Connection Timeout=30;"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "DatabaseConnectionString" \
    --value "$CONNECTION_STRING"

# Configure Web App settings
echo "⚙️ Configuring Web App..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        ASPNETCORE_ENVIRONMENT="Production" \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE="false"

# Enable managed identity and grant Key Vault access
WEB_APP_PRINCIPAL_ID=$(az webapp identity assign \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --query principalId \
    --output tsv)

az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $WEB_APP_PRINCIPAL_ID \
    --secret-permissions get

# Build and deploy
echo "🔨 Building application..."
dotnet publish -c Release -o ./publish

echo " Creating deployment package..."
cd publish
zip -r ../app.zip .
cd ..

echo " Deploying to Azure..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --src app.zip

echo " Deployment completed."
echo " Your application is available at: https://$WEB_APP_NAME.azurewebsites.net"
echo " Resource Group: $RESOURCE_GROUP"
echo " Database Server: $SQL_SERVER_NAME.database.windows.net"
echo "🔐 Key Vault: https://$KEY_VAULT_NAME.vault.azure.net"

# Cleanup
rm -f app.zip
rm -rf publish

echo "Deployment script completed."
```

### Post-Deployment Checklist

1. **Verify Application Health**
   ```bash
   curl https://your-app.azurewebsites.net/health
   ```

2. **Check Application Insights**
   - Monitor application performance
   - Review error logs
   - Set up alerts for critical issues

3. **Configure Custom Domain** (Optional)
   ```bash
   az webapp config hostname add \
       --webapp-name $WEB_APP_NAME \
       --resource-group $RESOURCE_GROUP \
       --hostname yourdomain.com
   ```

4. **Set up SSL Certificate**
   ```bash
   az webapp config ssl create \
       --resource-group $RESOURCE_GROUP \
       --name $WEB_APP_NAME \
       --hostname yourdomain.com
   ```

5. **Configure Backup Strategy**
   - Database automated backups
   - Application files backup
   - Configuration backup

### Troubleshooting Azure Deployment Issues

#### Issue 1: Database Connection Failures

**Solution**: Check firewall rules and connection strings
```bash
# Add your IP to SQL firewall
MY_IP=$(curl -s https://api.ipify.org)
az sql server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server $SQL_SERVER_NAME \
    --name "MyIP" \
    --start-ip-address $MY_IP \
    --end-ip-address $MY_IP
```

#### Issue 2: Application Not Starting

**Solution**: Check logs and configuration
```bash
# Stream logs
az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP

# Check application settings
az webapp config appsettings list \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP
```

#### Issue 3: Static Files Not Loading

**Solution**: Ensure proper build configuration and static file serving

### Security Best Practices Summary

1. **Always use HTTPS** in production
2. **Store secrets in Key Vault**, not configuration files
3. **Enable Azure AD authentication** for administrative access
4. **Configure network security groups** to restrict access
5. **Enable diagnostic logging** and monitoring
6. **Regular security updates** and patches
7. **Implement proper CORS policies**
8. **Use managed identities** instead of service principals when possible

### Cost Optimization

1. **Start with lower tiers** (B1, S1) and scale as needed
2. **Use Azure Reserved Instances** for long-term deployments
3. **Enable auto-scaling** to handle variable loads efficiently
4. **Monitor and optimize database** query performance
5. **Use CDN** for static content delivery
6. **Implement proper caching strategies**
7. **Regular cost analysis** using Azure Cost Management

### Resources

- [ASP.NET Core Documentation](https://docs.microsoft.com/aspnet/core)
- [React Documentation](https://react.dev)
- [gRPC Documentation](https://grpc.io/docs)
- [.NET Community](https://dotnet.microsoft.com/community)
- [Azure Documentation](https://docs.microsoft.com/azure)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service)

---
