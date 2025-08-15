# DevOps: gRPC Code Generation

## Overview

This document explains how to handle gRPC Protocol Buffer code generation in DevOps pipelines. The generated Python files are **excluded from Git** and must be generated during the build process.

## 📁 Repository Structure

### Files Tracked in Git:

```
protos/
├── __init__.py                 # Tracked (empty init file)
├── auth.proto                  # Tracked (Protocol Buffer schema)
├── user.proto                  # Tracked (User service schema)
├── common.proto                # Tracked (Common types schema)
generate_grpc.sh                # Tracked (Code generation script)
```

### Files Generated (NOT in Git):

```
protos/
├── auth_pb2.py                 # ❌ Generated (ignored by .gitignore)
├── auth_pb2_grpc.py            # ❌ Generated (ignored by .gitignore)
├── user_pb2.py                 # ❌ Generated (ignored by .gitignore)
├── user_pb2_grpc.py            # ❌ Generated (ignored by .gitignore)
├── common_pb2.py               # ❌ Generated (ignored by .gitignore)
└── common_pb2_grpc.py          # ❌ Generated (ignored by .gitignore)
```

## 🔧 Local Development Setup

### Prerequisites

```bash
# Install gRPC tools in virtual environment
python3 -m venv venv
source venv/bin/activate
pip install grpcio grpcio-tools protobuf
```

### Generate gRPC Code

```bash
# Method 1: Use the provided script
./generate_grpc.sh

# Method 2: Manual generation
python -m grpc_tools.protoc \
    --proto_path=protos \
    --python_out=protos \
    --grpc_python_out=protos \
    protos/*.proto
```

### Verification

```bash
# Verify generated files exist
ls -la protos/*_pb2*.py

# Should show:
# auth_pb2.py, auth_pb2_grpc.py
# user_pb2.py, user_pb2_grpc.py
# common_pb2.py, common_pb2_grpc.py
```

## CI/CD Pipeline Integration

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.12'
        VENV_PATH = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh """
                    python3 -m venv ${VENV_PATH}
                    source ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Generate gRPC Code') {
            steps {
                sh """
                    source ${VENV_PATH}/bin/activate
                    chmod +x generate_grpc.sh
                    ./generate_grpc.sh
                """
            }
        }

        stage('Verify gRPC Generation') {
            steps {
                sh """
                    # Verify all expected files were generated
                    test -f protos/auth_pb2.py
                    test -f protos/auth_pb2_grpc.py
                    test -f protos/user_pb2.py
                    test -f protos/user_pb2_grpc.py
                    test -f protos/common_pb2.py
                    test -f protos/common_pb2_grpc.py
                    echo "✅ All gRPC files generated successfully"
                """
            }
        }

        stage('Run Tests') {
            steps {
                sh """
                    source ${VENV_PATH}/bin/activate
                    python -m pytest tests/ -v
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    # Generate gRPC code in Docker build
                    docker build -t fastapi-grpc:${BUILD_NUMBER} .
                """
            }
        }
    }

    post {
        always {
            // Clean up generated files if needed
            sh """
                rm -f protos/*_pb2.py
                rm -f protos/*_pb2_grpc.py
            """
        }
    }
}
```

### GitHub Actions Example

```yaml
name: Build and Test gRPC Services

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Generate gRPC code
        run: |
          chmod +x generate_grpc.sh
          ./generate_grpc.sh

      - name: Verify gRPC generation
        run: |
          test -f protos/auth_pb2.py || exit 1
          test -f protos/auth_pb2_grpc.py || exit 1
          test -f protos/user_pb2.py || exit 1
          test -f protos/user_pb2_grpc.py || exit 1
          echo " gRPC code generation verified"

      - name: Run tests
        run: |
          python -m pytest tests/ -v --cov=services/

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
```

### GitLab CI

```yaml
stages:
  - setup
  - generate
  - test
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.12"

setup:
  stage: setup
  image: python:${PYTHON_VERSION}
  script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install --upgrade pip
    - pip install -r requirements.txt
  artifacts:
    paths:
      - venv/
    expire_in: 1 hour

generate_grpc:
  stage: generate
  image: python:${PYTHON_VERSION}
  dependencies:
    - setup
  script:
    - source venv/bin/activate
    - chmod +x generate_grpc.sh
    - ./generate_grpc.sh
    - ls -la protos/*_pb2*.py # Verify generation
  artifacts:
    paths:
      - protos/*_pb2.py
      - protos/*_pb2_grpc.py
    expire_in: 1 hour

test:
  stage: test
  image: python:${PYTHON_VERSION}
  dependencies:
    - generate_grpc
  script:
    - source venv/bin/activate
    - python -m pytest tests/ -v --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
```

## 🐳 Docker Integration

### Multi-stage Dockerfile

```dockerfile
# Build stage - Generate gRPC code
FROM python:3.12-slim as grpc-builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files and generation script
COPY protos/ protos/
COPY generate_grpc.sh .

# Generate gRPC code
RUN chmod +x generate_grpc.sh && ./generate_grpc.sh

# Runtime stage
FROM python:3.12-slim as runtime

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy generated gRPC files from builder stage
COPY --from=grpc-builder /app/protos/*_pb2.py protos/
COPY --from=grpc-builder /app/protos/*_pb2_grpc.py protos/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000 50051
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Build

```yaml
version: "3.8"

services:
  fastapi-app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - AUTH_SERVICE_HOST=auth-service
    depends_on:
      - redis
      - auth-service

  auth-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "50051:50051"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
    command: ["python", "services/auth_service.py"]

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Build Verification Scripts

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Checking for generated gRPC files..."

# Check if any generated files are staged
if git diff --cached --name-only | grep -E "_pb2\.py|_pb2_grpc\.py"; then
    echo "❌ Error: Generated gRPC files should not be committed!"
    echo "Files found:"
    git diff --cached --name-only | grep -E "_pb2\.py|_pb2_grpc\.py"
    echo ""
    echo "Please run: git reset HEAD protos/*_pb2*.py"
    echo "Generated files are automatically created during build."
    exit 1
fi

echo "No generated gRPC files in commit."
```

### Build Validation Script

```bash
#!/bin/bash
# scripts/validate-grpc-build.sh

set -e

echo "🔧 Validating gRPC Build Process..."

# Check if proto files exist
echo "Checking protocol buffer files..."
for proto in protos/*.proto; do
    if [[ -f "$proto" ]]; then
        echo " Found: $proto"
    else
        echo "  ❌ Missing: $proto"
        exit 1
    fi
done

# Check if generation script exists
if [[ -f "generate_grpc.sh" ]]; then
    echo " Found: generate_grpc.sh"
else
    echo "❌ Missing: generate_grpc.sh"
    exit 1
fi

# Test generation
echo "🔨 Testing gRPC code generation..."
./generate_grpc.sh

# Verify generated files
echo "Verifying generated files..."
expected_files=(
    "protos/auth_pb2.py"
    "protos/auth_pb2_grpc.py"
    "protos/user_pb2.py"
    "protos/user_pb2_grpc.py"
    "protos/common_pb2.py"
    "protos/common_pb2_grpc.py"
)

for file in "${expected_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo " Generated: $file"
    else
        echo "  ❌ Missing: $file"
        exit 1
    fi
done

echo " gRPC build validation successful!"
```

## Issues and Solutions

### Issue 1: Missing Dependencies

```bash
# Error: ModuleNotFoundError: No module named 'grpc_tools'
# Solution:
pip install grpcio-tools

# Or in requirements.txt:
grpcio-tools>=1.59.0
```

### Issue 2: Import Path Issues

```bash
# Error: ImportError: No module named 'protos.auth_pb2'
# Solution: Ensure __init__.py exists in protos/
touch protos/__init__.py

# Or fix import paths in generated files:
sed -i 's/import auth_pb2/from . import auth_pb2/g' protos/auth_pb2_grpc.py
```

### Issue 3: Permission Issues

```bash
# Error: Permission denied: ./generate_grpc.sh
# Solution:
chmod +x generate_grpc.sh
```

### Issue 4: Docker Build Fails

```bash
# Error: Proto files not found in Docker
# Solution: Ensure COPY commands include proto files before generation
COPY protos/ protos/
COPY generate_grpc.sh .
RUN ./generate_grpc.sh
```

## Build Performance

1. **Cache Generated Files** in CI/CD:

   ```yaml
   # GitHub Actions
   - uses: actions/cache@v3
     with:
       path: protos/*_pb2*.py
       key: grpc-${{ hashFiles('protos/*.proto') }}
   ```

2. **Parallel Generation**:

   ```bash
   # Generate multiple proto files in parallel
   python -m grpc_tools.protoc --proto_path=protos --python_out=protos --grpc_python_out=protos protos/auth.proto &
   python -m grpc_tools.protoc --proto_path=protos --python_out=protos --grpc_python_out=protos protos/user.proto &
   wait
   ```

3. **Incremental Builds**:
   ```bash
   # Only regenerate if proto files changed
   if [[ protos/*.proto -nt protos/auth_pb2.py ]]; then
       ./generate_grpc.sh
   fi
   ```

## 🔐 Security Considerations

1. **No Sensitive Data** in proto files (they're committed to Git)
2. **Generate in Secure Environment** (avoid untrusted proto files)
3. **Validate Generated Code** before deployment
4. **Version Lock** gRPC tools to prevent supply chain attacks

## References

- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
