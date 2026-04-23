\set ON_ERROR_STOP on

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'user') THEN
        CREATE ROLE "user" LOGIN PASSWORD 'pass';
    ELSE
        ALTER ROLE "user" WITH LOGIN PASSWORD 'pass';
    END IF;
END
$$;

SELECT 'CREATE DATABASE course_dev_ide_migration OWNER "user"'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = 'course_dev_ide_migration'
)\gexec

GRANT ALL PRIVILEGES ON DATABASE course_dev_ide_migration TO "user";

\connect course_dev_ide_migration

GRANT USAGE, CREATE ON SCHEMA public TO "user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO "user";

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
