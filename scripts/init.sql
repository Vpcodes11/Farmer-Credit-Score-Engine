-- Initialize database schema
-- This script is run automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (handled by SQLAlchemy in production)
-- This is just for manual initialization if needed

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE fcs TO postgres;

-- Create initial admin user (password: admin123)
-- This will be created via API in production
