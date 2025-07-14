-- Initialize the database with required tables
CREATE DATABASE IF NOT EXISTS microservices_db;

\c microservices_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Insert demo user (password is 'demo123' hashed with bcrypt)
INSERT INTO users (username, email, password_hash, phone) 
VALUES (
    'demo',
    'demo@example.com',
    '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LwfBR8nvHzfU6PQNe',
    '+1234567890'
) ON CONFLICT (email) DO NOTHING;
