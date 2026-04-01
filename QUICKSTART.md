# SmartHotel - Quick Start Guide

## First Time Setup (Local Development)

### Step 1: Generate a Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output for the next step.

### Step 2: Create `.env` File

Create a file named `.env` in the project root with:

```env
SECRET_KEY=<paste-the-generated-key-here>
DATABASE_PATH=hotel.db
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### Step 3: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

Open your browser to: **http://127.0.0.1:5000**

**Demo Credentials:**
- Username: `admin`
- Password: `admin123`

---

## For Azure Deployment

See [CONFIGURATION.md](CONFIGURATION.md) for detailed Azure deployment instructions.

---

## Key Changes Made

✅ **Removed hardcoded secrets** - Now uses environment variables  
✅ **Added configuration validation** - App fails safely if SECRET_KEY is missing  
✅ **Made debug mode configurable** - Can't accidentally enable in production  
✅ **Azure-ready startup** - Respects Azure's `PORT` environment variable  
✅ **Added `.gitignore`** - Prevents `.env` from being committed  
✅ **Added `requirements.txt`** - Proper dependency management  

---

## Important Security Notes

⚠️ **NEVER**:
- Commit `.env` to version control
- Share SECRET_KEY via email or chat
- Enable `FLASK_DEBUG=True` in production
- Use the same SECRET_KEY across environments

✅ **Always**:
- Generate a unique SECRET_KEY for each environment
- Store production secrets in Azure Key Vault
- Use HTTPS in production
- Rotate secrets regularly

---

## Troubleshooting

### "SECRET_KEY environment variable not set"

Create a `.env` file with a generated SECRET_KEY (see Step 1-2 above).

### "ModuleNotFoundError: No module named 'dotenv'"

Run: `pip install -r requirements.txt`

### Port already in use

Change `FLASK_PORT` in `.env` to an available port (e.g., 5001).

---

For more detailed configuration options, see [CONFIGURATION.md](CONFIGURATION.md)
