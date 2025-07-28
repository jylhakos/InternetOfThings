# Open WebUI

This document helps to setup and running with Open WebUI.

> **Documentation**: For detailed setup and architecture information, see [README.md](README.md)  
> **API Testing**: For cURL examples and API validation, see [API.md](API.md)

## Steps

### Step 1: Start the backend
```bash
./start.sh start
```
Wait for all services to start (about 30-60 seconds).

### Step 2: Start Open WebUI
```bash
./open_webui.sh start
```
This will download and start Open WebUI in Docker.

### Step 3: Access the interface
1. Open your browser to: http://localhost:3001
2. Create an account (first user becomes admin)
3. Start chatting with your local LLM!

## Verification

Check that everything is working:
```bash
# Test the system
python open_webui_tests.py

# Check status
./open_webui.sh status
```
## Stopping

```bash
# Stop Open WebUI
./open_webui.sh stop

# Stop all services
./start.sh stop
```
## Tips

### Using Prompt Templates
In Open WebUI, go to the chat interface and set a system prompt:

**Questions**
```
You are a senior software engineer. Provide detailed technical explanations with examples.
```

**Writing**
```
You are a creative writer. Generate imaginative, engaging content.
```

### Model selection
Available models (choose in Open WebUI):
- **llama3.2:1b** - Fast responses, good for chat
- **llama3.2:3b** - Balanced performance
- **llama3.1:8b** - Best quality, slower

### Adjusting parameters
In Open WebUI Advanced Settings:
- **Temperature**: 0.1-1.0 (lower = more focused, higher = more creative)
- **Max Tokens**: 100-1000 (response length)

## Troubleshooting

### Open WebUI not start?
```bash
# Check Docker
docker --version

# Restart everything
./start.sh restart
./open_webui.sh restart
```

### Can't connect to API?
1. Verify FastAPI is running: `curl http://localhost:8000/health`
2. Check Open WebUI settings: API Base URL should be `http://host.docker.internal:8000/v1`
3. API Key should be: `sk-dummy-key-for-redis-queue-system`

### Slow responses?
1. Check queue status: `curl http://localhost:8000/queue_info`
2. Start more workers: `python worker.py &`
3. Use smaller model: `llama3.2:1b`

## Next

1. **Explore Templates**: `python prompt_templates_library.py`
2. **Run Tests**: `python open_webui_tests.py`
3. **Check Full Docs**: See README.md for complete documentation

