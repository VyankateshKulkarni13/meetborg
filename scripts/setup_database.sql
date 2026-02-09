-- AI Meeting Automation Database Setup
-- Run this script to create the database and user

-- Create database
CREATE DATABASE aimeet;

-- Create user (optional, can use postgres user)
CREATE USER aimeet_user WITH PASSWORD 'aimeet_password_2026';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE aimeet TO aimeet_user;

-- Connect to the database
\c aimeet

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO aimeet_user;

-- Done!
\echo 'Database aimeet created successfully!'
\echo 'Username: aimeet_user'
\echo 'Password: aimeet_password_2026'
\echo ''
\echo 'Update your .env file with:'
\echo 'DATABASE_URL=postgresql+asyncpg://aimeet_user:aimeet_password_2026@localhost:5432/aimeet'
