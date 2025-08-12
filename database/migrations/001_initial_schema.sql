-- OncoHotspot Initial Schema Migration
-- Version: 001
-- Description: Create initial database schema for cancer mutation analysis

-- Create database and use it
CREATE DATABASE IF NOT EXISTS oncohotspot;
USE oncohotspot;

-- Migration metadata table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description VARCHAR(255),
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Apply the main schema
SOURCE ../schemas/oncohotspot_schema.sql;

-- Record this migration
INSERT INTO schema_migrations (version, description) 
VALUES ('001', 'Initial database schema creation');

-- Create sample data for development
SOURCE ../seeds/sample_data.sql;