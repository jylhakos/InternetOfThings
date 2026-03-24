# Azure Functions LLM Inference

This example demonstrates how to deploy LLM inference orchestration using Azure Functions.

## Important Notes

Azure Functions has similar limitations to AWS Lambda:
- Maximum execution time: 10 minutes (Consumption plan) or 30 minutes (Premium plan)
- Limited memory and CPU
- Cold start latency
- No direct GPU support

**Best Use Cases**:
- Orchestration and routing to Azure OpenAI or Azure ML endpoints
- Preprocessing and postprocessing
- Integration layer
- Small-scale inference with lightweight models

## Architecture

```
HTTP(S) → Azure Functions → Azure OpenAI Service / Azure ML Endpoint
```

## Prerequisites

- Azure Account with active subscription
- Azure CLI installed
- Azure Functions Core Tools installed
- Python 3.11+

## Setup

1. **Install Azure Functions Core Tools**:
   ```bash
   # On Linux
   wget -q https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb
   sudo dpkg -i packages-microsoft-prod.deb
   sudo apt-get update
   sudo apt-get install azure-functions-core-tools-4
   
   # On macOS
   brew tap azure/functions
   brew install azure-functions-core-tools@4
   ```

2. **Install Azure CLI**:
   ```bash
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   ```

3. **Login to Azure**:
   ```bash
   az login
   ```

4. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Configuration

Create a `local.settings.json` file:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/",
    "AZURE_OPENAI_KEY": "your-api-key",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-4",
    "AZURE_ML_ENDPOINT": "",
    "AZURE_ML_KEY": ""
  },
  "Host": {
    "CORS": "*"
  }
}
```

## Local Testing

```bash
# Start function locally
func start

# Test in another terminal
curl -X POST http://localhost:7071/api/inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is machine learning?",
    "max_tokens": 150,
    "temperature": 0.7
  }'
```

## Deployment

### Create Azure Resources

```bash
# Set variables
RESOURCE_GROUP="llm-functions-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="llmfunctionsstorage"
FUNCTION_APP="llm-inference-func"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create function app (Consumption plan)
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux
```

### Deploy Function

```bash
# Deploy function code
func azure functionapp publish $FUNCTION_APP

# Configure app settings
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
    AZURE_OPENAI_KEY="your-api-key" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

### Test Deployed Function

```bash
# Get function URL
FUNCTION_URL=$(az functionapp function show \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --function-name inference \
  --query "invokeUrlTemplate" -o tsv)

FUNCTION_KEY=$(az functionapp keys list \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --query "functionKeys.default" -o tsv)

# Test
curl -X POST "${FUNCTION_URL}?code=${FUNCTION_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain Azure Functions",
    "max_tokens": 200
  }'
```

## Premium Plan (for better performance)

For production workloads, consider Premium plan:

```bash
# Create Premium plan
az functionapp plan create \
  --resource-group $RESOURCE_GROUP \
  --name llm-premium-plan \
  --location $LOCATION \
  --sku EP1 \
  --is-linux

# Create function app with Premium plan
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --plan llm-premium-plan \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux
```

Premium plan benefits:
- No cold starts
- Longer execution time
- More CPU and memory
- VNet integration

## Monitoring

### View Logs

```bash
# Stream logs
func azure functionapp logstream $FUNCTION_APP

# View Application Insights
az monitor app-insights component show \
  --app $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP
```

### Metrics

Monitor in Azure Portal:
- Function execution count
- Function execution time
- Errors and exceptions
- HTTP response codes

## Cost Optimization

- Use Consumption plan for variable workloads
- Use Premium plan for predictable workloads
- Enable Application Insights sampling
- Use Azure OpenAI provisioned throughput for high volume

## Clean Up

```bash
az group delete --name $RESOURCE_GROUP --yes
```

## Alternative: Container-based Functions

For more control, use custom container:

```dockerfile
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot
```

Deploy:
```bash
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --name $FUNCTION_APP \
  --storage-account $STORAGE_ACCOUNT \
  --plan llm-premium-plan \
  --deployment-container-image-name your-registry.azurecr.io/llm-function:latest
```
