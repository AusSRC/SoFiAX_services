-- Create the database, users and schema. Run by init.sh with psql variables.

CREATE DATABASE :"dbname" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';

-- Admin user
CREATE USER :"admin_user" WITH SUPERUSER PASSWORD :'admin_password';
ALTER DATABASE :"dbname" OWNER TO :"admin_user";

-- SURVEY user
CREATE USER "survey_user" WITH PASSWORD :'survey_password';

-- VO users
CREATE USER "gavo" WITH PASSWORD :'vo_trusted_password';
CREATE USER "gavoadmin" WITH PASSWORD :'vo_feed_password';
CREATE USER "untrusted" WITH PASSWORD :'vo_untrusted_password';

\connect :"dbname"

CREATE SCHEMA :"schema" AUTHORIZATION :"admin_user";

-- Required extensions
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_sphere";
