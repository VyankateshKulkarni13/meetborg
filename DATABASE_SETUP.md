# Database Configuration Guide

## Step 1: Create the Database

Open PowerShell and run:

```powershell
# Connect to PostgreSQL (you'll be prompted for password)
psql -U postgres

# Inside psql, run these commands:
CREATE DATABASE aimeet;
\q
```

**Alternative**: If you want a dedicated user (recommended for production):

```powershell
psql -U postgres

# Inside psql:
CREATE DATABASE aimeet;
CREATE USER aimeet_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE aimeet TO aimeet_user;
\c aimeet
GRANT ALL ON SCHEMA public TO aimeet_user;
\q
```

## Step 2: Configure .env File

The `.env` file has been created in the root directory. You need to update it:

### Required Changes:

1. **DATABASE_URL**: Replace `YOUR_POSTGRES_PASSWORD` with your actual postgres password
   
   **If using postgres user:**
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/aimeet
   ```
   
   **If using dedicated user:**
   ```
   DATABASE_URL=postgresql+asyncpg://aimeet_user:your_secure_password_here@localhost:5432/aimeet
   ```

2. **SECRET_KEY**: Generate a random secret key (at least 32 characters)
   
   You can generate one with:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **ENCRYPTION_KEY**: Generate another random key
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

## Step 3: Initialize Database Tables

```powershell
cd backend

# Activate virtual environment
.\venv\Scripts\activate

# Run database initialization
python ..\scripts\init_db.py
```

This will create the `users` table and verify the connection.

## Verification

To verify your database is set up correctly:

```powershell
# Connect to the database
psql -U postgres -d aimeet

# List tables
\dt

# You should see the 'users' table
# Exit
\q
```

## Common Issues

### Issue: "password authentication failed"
- Check your DATABASE_URL in .env has the correct password
- Make sure PostgreSQL is running

### Issue: "database 'aimeet' does not exist"
- Run the CREATE DATABASE command from Step 1

### Issue: "connection refused"
- Make sure PostgreSQL service is running
- Check if it's running on port 5432

## Next Steps

After database is configured:

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`  
3. Open http://localhost:3000
