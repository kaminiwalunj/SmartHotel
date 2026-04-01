# SmartHotel Configuration Guide

This guide explains how to configure the modernized SmartHotel application for both local development and Azure deployment.

## Overview of Changes

The application has been refactored to use **environment variables** instead of hardcoded configuration values. This enables:

✅ Safe deployment across multiple environments (dev, staging, production)  
✅ Secrets management via Azure Key Vault  
✅ Container-ready configuration (Docker, Kubernetes, Azure Container Apps)  
✅ No sensitive data in source code or version control  
✅ Compliance with Azure best practices  

---

## Local Development Setup

### 1. Create `.env` File

Copy the template and customize for your environment:

```bash
cp .env.example .env
```

### 2. Configure `.env` for Local Development

Edit `.env` with appropriate values:

```env
# Generate a secure secret key (one-time setup)
# Run: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-generated-secret-key-here

# Use local SQLite database
DATABASE_PATH=hotel.db

# Enable debug mode for development
FLASK_DEBUG=True

# Local development host/port
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Run Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

---

## Azure Deployment Configuration

### Option A: Azure App Service (Recommended)

#### 1. Create App Service

```bash
az appservice plan create --name SmartHotelPlan --resource-group myResourceGroup --sku B1 --is-linux
az webapp create --resource-group myResourceGroup --plan SmartHotelPlan --name smarthotelapp --runtime "PYTHON|3.11"
```

#### 2. Set Environment Variables in Azure

```bash
# Set SECRET_KEY (generate a new secure key)
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name smarthotelapp \
  --settings SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Enable production mode
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name smarthotelapp \
  --settings FLASK_DEBUG=False

# Use local SQLite (or replace with Azure SQL connection string)
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name smarthotelapp \
  --settings DATABASE_PATH="/home/site/wwwroot/hotel.db"
```

#### 3. Deploy Application

```bash
# Using Git deployment
az webapp deployment source config-zip \
  --resource-group myResourceGroup \
  --name smarthotelapp \
  --src <path-to-zipped-app>

# Or using GitHub Actions (recommended for CI/CD)
```

---

### Option B: Azure Container Apps (Cloud-Native)

#### 1. Create Container Image

Create a `Dockerfile` in the root directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

#### 2. Build and Push to Azure Container Registry

```bash
# Create container registry
az acr create --resource-group myResourceGroup --name smarthotelregistry --sku Basic

# Build image
az acr build --registry smarthotelregistry --image smarthotel:latest .

# Create container app environment
az containerapp env create \
  --name smarthotel-env \
  --resource-group myResourceGroup \
  --location eastus

# Deploy container app
az containerapp create \
  --name smarthotel \
  --resource-group myResourceGroup \
  --environment smarthotel-env \
  --image smarthotelregistry.azurecr.io/smarthotel:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    SECRET_KEY="<your-secret-key>" \
    FLASK_DEBUG=False \
    DATABASE_PATH="hotel.db"
```

---

## Environment Variables Reference

### Required Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | Flask session signing key (CRITICAL) | Auto-generated hex string |

### Optional Variables (with Defaults)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_PATH` | `hotel.db` | Path to SQLite database or connection string |
| `FLASK_DEBUG` | `False` | Enable debug mode (NEVER in production) |
| `FLASK_HOST` | `127.0.0.1` | Server bind address |
| `FLASK_PORT` | `5000` | Server port (overridden by `PORT` in Azure) |
| `PORT` | (none) | Azure App Service automatically sets this |

---

## Azure Key Vault Integration (Recommended for Production)

For production deployments, use Azure Key Vault instead of storing secrets in App Configuration:

### 1. Create Key Vault

```bash
az keyvault create \
  --resource-group myResourceGroup \
  --name smarthotel-vault \
  --location eastus \
  --enable-purge-protection
```

### 2. Store Secrets

```bash
# Store application secret key
az keyvault secret set \
  --vault-name smarthotel-vault \
  --name FLASK-SECRET-KEY \
  --value "$(python -c 'import secrets; print(secrets.token_hex(32))')"

# Store database connection string (if using Azure SQL)
az keyvault secret set \
  --vault-name smarthotel-vault \
  --name DATABASE-CONNECTION \
  --value "mssql+pyodbc://user:password@server.database.windows.net/smarthotel?driver=ODBC+Driver+17+for+SQL+Server"
```

### 3. Configure Managed Identity

Enable Managed Identity on your App Service and grant Key Vault access:

```bash
# Enable system-assigned identity
az webapp identity assign \
  --resource-group myResourceGroup \
  --name smarthotelapp

# Grant Key Vault access
az keyvault set-policy \
  --name smarthotel-vault \
  --object-id <managed-identity-object-id> \
  --secret-permissions get
```

### 4. Reference Key Vault in App Service

Use Key Vault references in application settings:

```bash
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name smarthotelapp \
  --settings SECRET_KEY="@Microsoft.KeyVault(VaultName=smarthotel-vault;SecretName=FLASK-SECRET-KEY)"
```

---

## Database Configuration

### SQLite (Development/Testing)

```env
DATABASE_PATH=hotel.db
```

### Azure SQL Database (Production)

```env
# Connection string format
DATABASE_PATH=mssql+pyodbc://username:password@server.database.windows.net/dbname?driver=ODBC+Driver+17+for+SQL+Server
```

Requires updating `get_db()` function in `app.py` to use SQLAlchemy ORM instead of sqlite3.

---

## Security Best Practices

### ✅ Always Do

- [ ] Use different `SECRET_KEY` values for each environment
- [ ] Store secrets in Azure Key Vault (production)
- [ ] Never commit `.env` files to version control
- [ ] Rotate secrets regularly
- [ ] Use HTTPS for all connections
- [ ] Enable FLASK_DEBUG=False in production

### ❌ Never Do

- [ ] Hardcode secrets in source code
- [ ] Share `.env` files via email or chat
- [ ] Use same secrets across environments
- [ ] Enable debug mode in production
- [ ] Run with `host='0.0.0.0'` unless in container

---

## Troubleshooting

### Application won't start - "CRITICAL: SECRET_KEY environment variable not set"

**Solution:** Ensure `SECRET_KEY` is set in `.env` (development) or App Settings (Azure)

```bash
# Generate a key if needed
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database file not found in production

**Solution:** Use absolute path or ensure write permissions. For production, migrate to Azure SQL Database.

### Application running on wrong port

**Solution:** Azure App Service automatically sets `PORT` environment variable. Your application respects this via:

```python
if 'PORT' in os.environ:
    port = int(os.environ['PORT'])
```

---

## Next Steps

After configuration, the following modernization phases are recommended:

1. **Phase 2:** Add health checks (`/health` and `/ready` endpoints)
2. **Phase 3:** Implement containerization with Docker
3. **Phase 4:** Migrate to proper logging framework
4. **Phase 5:** Add password hashing and CSRF protection
5. **Phase 6:** Implement pagination and input validation

---

## References

- [Azure App Service Configuration](https://docs.microsoft.com/en-us/azure/app-service/configure-common)
- [Azure Key Vault Security](https://docs.microsoft.com/en-us/azure/key-vault/general/security-best-practices)
- [Flask Configuration](https://flask.palletsprojects.com/en/2.3.x/config/)
- [12-Factor App - Config](https://12factor.net/config)
