# Quick PostgreSQL Setup - Final Steps

## You're almost done! Follow these steps:

### Step 1: Restart PostgreSQL (Requires Admin)

Since the service is running, we need to restart it with administrator privileges:

1. **Open PowerShell as Administrator** (Right-click → "Run as Administrator")

2. **Run this command**:
   ```powershell
   Restart-Service postgresql-x64-17
   ```

### Step 2: Create Database (No Password Needed Now!)

After restarting, the "trust" method will be active. Run:

```powershell
psql -U postgres -c "CREATE DATABASE aimeet;"
```

You should see: `CREATE DATABASE` (no password prompt!)

### Step 3: Set a New Password

```powershell
psql -U postgres
```

Inside psql:
```sql
ALTER USER postgres WITH PASSWORD 'aimeet2026';
\q
```

**Remember this password: `aimeet2026`** (or choose your own)

### Step 4: Secure PostgreSQL Again (IMPORTANT!)

1. **Edit `pg_hba.conf` again** (same location as before)

2. **Change back**:
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   ```

3. **Restart PostgreSQL again** (as Administrator):
   ```powershell
   Restart-Service postgresql-x64-17
   ```

### Step 5: Update .env File

Edit `e:\AI Meeter\.env` and update this line:

```
DATABASE_URL=postgresql+asyncpg://postgres:aimeet2026@localhost:5432/aimeet
```

(Replace `aimeet2026` with your chosen password)

Also update:
```
SECRET_KEY=change-this-to-a-random-secret-key-min-32-chars
ENCRYPTION_KEY=change-this-to-another-random-key-32-chars
```

You can generate random keys with:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## After Setup is Complete:

Initialize the database tables:

```powershell
cd e:\AI Meeter\backend
.\venv\Scripts\activate
pip install asyncpg  # Make sure async driver is installed
python ..\scripts\init_db.py
```

This will create the `users` table.

---

**Let me know when you've completed these steps and I'll help you start the application!**
