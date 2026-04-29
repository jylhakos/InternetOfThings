# Compose for Agents

## One-Command Setup

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh
```

## Manual Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install uv
uv sync
```

### 3. Download Database

```bash
wget https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite -O Chinook.db
```

### 4. Run with Docker Compose

```bash
docker compose up
```

## VS Code Setup

1. Open Command Palette: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Select: `Python: Select Interpreter`
3. Choose: `./venv/bin/python`

## Common Commands

```bash
# View agent logs
docker compose logs -f agent

# Stop services
docker compose down

# Clean up everything
docker compose down -v

# Rebuild containers
docker compose up --build
```

## Troubleshooting

### Virtual Environment Not Activating

```bash
# Make sure you're in the project directory
cd "CODING-AND-DEVELOPMENT/Docker Compose for Agents"

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Docker Compose Errors

```bash
# Check Docker is running
docker ps

# Check Docker Compose version (need 2.38.1+)
docker compose version

# Pull latest images
docker compose pull
```

### GPU Not Detected

- Enable GPU support in Docker Desktop settings
- Install NVIDIA drivers (Linux/Windows)
- Or use Docker Offload as alternative

### Database Import Fails

```bash
# Ensure Chinook.db is downloaded
ls -lh Chinook.db

# Check PostgreSQL logs
docker compose logs database
```

## Customization

### Change the Question

Edit `compose.yaml`:

```yaml
agent:
  environment:
    - QUESTION=Your question here
```

### Use Different Model

Edit `compose.yaml`:

```yaml
agent:
  environment:
    - MODEL_NAME=llama3.1
```

### Use OpenAI API

```bash
echo "sk-your-key" > secret.openai-api-key
docker compose -f compose.yaml -f compose.openai.yaml up
```
