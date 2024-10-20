-- Ensure dblink extension is available
CREATE EXTENSION IF NOT EXISTS dblink;

-- Create database if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'wallabydb') THEN
        PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE wallabydb WITH TEMPLATE = template0 ENCODING = ''UTF8'' LC_COLLATE = ''en_US.utf8'' LC_CTYPE = ''en_US.utf8''');
    END IF;
END
$$;

-- Create admin user if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'admin') THEN
        CREATE USER "admin";
        ALTER USER "admin" WITH PASSWORD 'admin';
        ALTER USER "admin" WITH SUPERUSER;
    END IF;
END
$$;

-- Create wallaby user if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'wallaby_user') THEN
        CREATE USER "wallaby_user";
        ALTER USER "wallaby_user" WITH PASSWORD 'wallaby_user';
    END IF;
END
$$;

-- Create cirada user if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'cirada') THEN
        CREATE USER "cirada";
        ALTER USER "cirada" WITH PASSWORD 'cirada';
    END IF;
END
$$;

-- Create cirada user if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bucardo') THEN
        CREATE USER "bucardo";
        ALTER USER "bucardo" WITH PASSWORD 'bucardo';
    END IF;
END
$$;

-- Create VO users if they do not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gavo') THEN
        CREATE USER "gavo";
        ALTER USER "gavo" WITH PASSWORD 'gavo';
    END IF;

    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gavoadmin') THEN
        CREATE USER "gavoadmin";
        ALTER USER "gavoadmin" WITH PASSWORD 'gavoadmin';
    END IF;

    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'untrusted') THEN
        CREATE USER "untrusted";
        ALTER USER "untrusted" WITH PASSWORD 'untrusted';
    END IF;
END
$$;

-- Set the owner of the wallaby database to admin
ALTER DATABASE wallabydb OWNER TO "admin";