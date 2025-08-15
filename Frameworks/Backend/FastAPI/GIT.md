# Git Repository Configuration - gRPC

## 📁 Repository Structure

### Files Tracked in Git (Source Files)

```
protos/
├── __init__.py                 # TRACKED - Python package init
├── auth.proto                  # TRACKED - Auth service schema
├── user.proto                  # TRACKED - User service schema
└── common.proto                # TRACKED - Common types schema

generate_grpc.sh                # TRACKED - Code generation script
```

### ❌ Files NOT Tracked (Generated Files)

```
protos/
├── auth_pb2.py                 # ❌ IGNORED - Generated message classes
├── auth_pb2_grpc.py            # ❌ IGNORED - Generated service stubs
├── user_pb2.py                 # ❌ IGNORED - Generated user messages
├── user_pb2_grpc.py            # ❌ IGNORED - Generated user stubs
├── common_pb2.py               # ❌ IGNORED - Generated common messages
└── common_pb2_grpc.py          # ❌ IGNORED - Generated common stubs
```

## 🔧 .gitignore Configuration

The `.gitignore` file contains:

```ignore
# gRPC generated files
*_pb2.py
*_pb2_grpc.py
```

This pattern excludes ALL generated Protocol Buffer Python files from version control.

## DevOps Integration

### 1. Local Development

```bash
# Clone repository
git clone <repository-url>
cd FastAPI/

# Setup environment (includes gRPC generation)
./setup-dev.sh

# Manual generation if needed
./generate_grpc.sh
```

### 2. Jenkins Pipeline

The `Jenkinsfile` now includes a dedicated stage:

```groovy
stage('Generate gRPC Code') {
    steps {
        sh '''
            source venv/bin/activate
            chmod +x generate_grpc.sh
            ./generate_grpc.sh
        '''
        // Verification step ensures all files are generated
    }
}
```

### 3. Docker Build

The `Dockerfile` generates gRPC code during build:

```dockerfile
# Copy proto files and generation script
COPY protos/ ./protos/
COPY generate_grpc.sh .

# Generate gRPC code from Protocol Buffers
RUN chmod +x generate_grpc.sh \
    && ./generate_grpc.sh
```

### 4. GitHub Actions / GitLab CI

Automated generation in CI/CD pipelines:

```yaml
- name: Generate gRPC code
  run: |
    chmod +x generate_grpc.sh
    ./generate_grpc.sh
```

## 🛡️ Safety

### 1. Pre-commit Hook

```bash
# Install the pre-commit hook
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook prevents accidental commits of generated files:

```bash
❌ ERROR: Generated gRPC files should not be committed!
The following generated files were found in your commit:
  - protos/auth_pb2.py
  - protos/auth_pb2_grpc.py
```

### 2. Build Verification

Each build process includes verification:

```bash
# Verify all expected files were generated
test -f protos/auth_pb2.py || exit 1
test -f protos/auth_pb2_grpc.py || exit 1
# ... additional checks
```

## Current Git Status

**Files staged for commit:**

- `protos/__init__.py`
- `protos/auth.proto`
- `protos/common.proto`
- `protos/user.proto`

**Files ignored by Git:**

- All `*_pb2.py` files ❌
- All `*_pb2_grpc.py` files ❌

### Repository Cleanliness

- No binary/generated files in version control
- Smaller repository size
- Cleaner diffs and history

### DevOps Friendly

- Reproducible builds across environments
- Fresh generation ensures compatibility
- No version mismatch issues

### Development Workflow

- Automatic generation in setup scripts
- Clear separation of source vs generated code
- Consistent build process

### Security & Maintenance

- No risk of committing outdated generated code
- Always uses latest protobuf compiler
- Prevents manual editing of generated files

## 🔄 Workflow

1. **Developer commits**: Only `.proto` files and `generate_grpc.sh`
2. **CI/CD builds**: Automatically run `./generate_grpc.sh`
3. **Generated files**: Created fresh for each build/deployment
4. **Git ignores**: All `*_pb2*.py` files automatically
5. **Pre-commit hook**: Prevents accidental commits

## Documentation

- **DEVOPS.md**: Comprehensive CI/CD integration guide
- **scripts/pre-commit-hook.sh**: Git safety mechanism
- **setup-dev.sh**: Complete development environment setup
- **Updated Jenkinsfile**: Includes gRPC generation stage
- **Updated Dockerfile**: Multi-stage build with gRPC generation
