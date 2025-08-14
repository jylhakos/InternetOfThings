# .gitignore Configuration Guide

This document explains the comprehensive .gitignore setup for the IoT Vite project and provides guidance for maintaining clean Git repositories.

## 📁 Files Overview

- **`.gitignore`** - Main gitignore file for the Vite project
- **`.gitignore.template`** - Template that can be copied to other parts of the IoT project

## 🚫 What's Excluded

### 1. **Development Dependencies**
- `node_modules/` - All Node.js dependencies
- Package manager logs (`npm-debug.log*`, `yarn-debug.log*`, etc.)
- Package manager stores and caches

### 2. **IDE and Editor Files (COMPLETE EXCLUSION)**
- `.vscode/` - Complete Visual Studio Code settings folder
- `.idea/` - JetBrains IDEs (IntelliJ, WebStorm, etc.)
- `.vs/` - Visual Studio
- Temporary editor files (`*.swp`, `*.swo`, `*~`)
- Sublime Text, Atom, Brackets configurations

### 3. **Build Outputs and Generated Files**
- `dist/`, `build/`, `out/` - Build directories
- `*.tsbuildinfo` - TypeScript build info
- Auto-generated files (`auto-imports.d.ts`, `components.d.ts`)

### 4. **Binary Files and Executables**
- Platform executables (`.exe`, `.bin`, `.dmg`, `.pkg`, `.deb`, `.rpm`, `.msi`, `.app`)
- Compiled libraries (`.so`, `.dylib`, `.dll`, `.lib`, `.a`)
- Object files (`.o`, `.obj`, `.elf`)
- Archive files (`.tar`, `.zip`, `.rar`, `.7z`, `.gz`)

### 5. **IoT and Hardware Specific**
- **Microcontroller firmware**: `*.hex`, `*.ino.bin`, `*.ino.elf`
- **Arduino/ESP32/ESP8266**: `libraries/`, `hardware/`, `*.fqbn`
- **PlatformIO**: `.pio/`, `.platformio/`
- **Raspberry Pi**: `*.img`, `*.iso`, `boot/`, `rootfs/`
- **Circuit design**: `*.pcb~`, `*.sch~`, `*.brd~`, `*.kicad_pcb-bak`
- **3D models**: `*.stl`, `*.step`, `*.stp`, `*.iges`

### 6. **Language-Specific Compiled Files**
- **Python**: `*.pyc`, `__pycache__/`, `*.py[cod]`
- **Java**: `*.class`, `*.jar`, `*.war`, `*.ear`
- **C/C++**: `*.out`, `*.gch`, `*.pch`
- **Rust**: `target/`, `Cargo.lock`
- **Go**: Various Go-specific files

### 7. **Security and Sensitive Data**
- Environment files (`.env*`)
- Certificate files (`*.pem`, `*.key`, `*.crt`)
- API keys and secrets (`*.secret`, `.secrets/`)
- IoT configuration (`mqtt-config.json`, `broker-config.json`)

### 8. **Operating System Files**
- **macOS**: `.DS_Store`, `._*`, `.Spotlight-V100`, `.Trashes`
- **Windows**: `Thumbs.db`, `ehthumbs.db`, `desktop.ini`, `$RECYCLE.BIN/`
- **Linux**: Various temporary files

### 9. **Cache and Temporary Files**
- `.cache/`, `.vite/`, `.temp/`, `.tmp/`
- Build tool caches (`.parcel-cache/`, `.rpt2_cache/`)
- Linting caches (`.eslintcache`, `.prettiercache`)

### 10. **Cloud and Deployment**
- `.vercel/`, `.netlify/`, `.aws/`, `.gcp/`, `.heroku/`
- Cloud configuration files (`aws-exports.js`, `gcp-key.json`)

## ✅ What's Included

The following files are **intentionally tracked** in Git:

### Configuration Files
- `package.json` - Project dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite configuration
- `eslint.config.js` - ESLint configuration
- `.prettierrc.json` - Prettier configuration

### Documentation
- `README.md` - Project documentation
- Source code and assets in `src/`

### Development Setup
- `Dockerfile`, `docker-compose.yml` - Container configuration
- `.github/workflows/` - CI/CD pipelines
- `build.sh` - Build scripts

### VS Code Extensions (Optional)
If you want to share VS Code extensions, you can add:
```
!.vscode/extensions.json
```

## 🔧 Customization

### Including Package Lock Files
If you want to track package lock files, comment out these lines:
```gitignore
# package-lock.json
# yarn.lock
# pnpm-lock.yaml
```

### Including Docker Files
If you don't want to track Docker files, uncomment:
```gitignore
# Dockerfile*
# docker-compose*.yml
# .dockerignore
```

### Project-Specific Exclusions
Add your specific exclusions at the end of the .gitignore file:
```gitignore
# Project-specific
custom-config/
data-dumps/
experimental/
```

## Best Practices

### 1. **Repository Root**
Copy the `.gitignore.template` to your repository root for project-wide coverage.

### 2. **Subdirectory Gitignore**
For specific subdirectories, create focused .gitignore files:
```bash
# In Arduino project folder
*.hex
*.ino.bin
libraries/

# In Python project folder
__pycache__/
*.pyc
venv/
```

### 3. **Check Ignored Files**
Use these commands to verify what's being ignored:
```bash
# List ignored files
git ls-files --others --ignored --exclude-standard

# Check if a specific file is ignored
git check-ignore -v filename

# Show what would be added
git add --dry-run .
```

### 4. **Clean Existing Repository**
If you're adding this to an existing repository that already tracks unwanted files:
```bash
# Remove files from Git but keep locally
git rm --cached -r node_modules/
git rm --cached -r .vscode/
git rm --cached -r dist/

# Commit the removal
git commit -m "Remove ignored files from tracking"
```

### 5. **Global Gitignore**
Create a global gitignore for user-specific exclusions:
```bash
# Set up global gitignore
git config --global core.excludesfile ~/.gitignore_global

# Add personal exclusions
echo ".DS_Store" >> ~/.gitignore_global
echo "*.log" >> ~/.gitignore_global
```

## Verification Checklist

Before committing, ensure:

- No `node_modules/` directories are tracked
- No `.vscode/` or `.idea/` folders are committed
- No binary files (`.exe`, `.bin`, `.so`, `.dll`) are included
- No environment files with secrets (`.env.local`, `*.secret`)
- No build outputs (`dist/`, `build/`, `*.tsbuildinfo`)
- No temporary files (`*.tmp`, `*.log`, `*~`)
- No OS-specific files (`.DS_Store`, `Thumbs.db`)

## Monitoring

Use Git hooks or CI/CD to monitor for accidentally committed files:
```bash
# Pre-commit hook example
#!/bin/bash
if git diff --cached --name-only | grep -E '\.(exe|bin|so|dll|log)$'; then
    echo "Error: Binary or log files detected!"
    exit 1
fi
```

