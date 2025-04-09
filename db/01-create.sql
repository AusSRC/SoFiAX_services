-- Create database
CREATE DATABASE wallabydb WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';

-- Create admin user
CREATE USER "admin";
ALTER USER "admin" WITH PASSWORD 'admin';
ALTER USER "admin" WITH SUPERUSER;
ALTER DATABASE wallabydb OWNER TO "admin";

-- Create SURVEY user
CREATE USER "wallaby_user";
ALTER USER "wallaby_user" WITH PASSWORD 'wallaby_user';

-- Create VO user
CREATE USER "gavo";
ALTER USER "gavo" WITH PASSWORD 'gavo';
CREATE USER "gavoadmin";
ALTER USER "gavoadmin" WITH PASSWORD 'gavoadmin';
CREATE USER "untrusted";
ALTER USER "untrusted" WITH PASSWORD 'untrusted';
