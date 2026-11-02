-- Create the database, users and schema. Run by init.sh with psql variables.
-- The survey and VO users are only created when their passwords are given.

CREATE DATABASE :"dbname" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';

-- Admin user
CREATE USER :"admin_user" WITH SUPERUSER PASSWORD :'admin_password';
ALTER DATABASE :"dbname" OWNER TO :"admin_user";

-- SURVEY user
\if :{?survey_password}
CREATE USER "survey_user" WITH PASSWORD :'survey_password';
\endif

-- VO users
\if :{?vo_feed_password}
CREATE USER "gavo" WITH PASSWORD :'vo_trusted_password';
CREATE USER "gavoadmin" WITH PASSWORD :'vo_feed_password';
CREATE USER "untrusted" WITH PASSWORD :'vo_untrusted_password';
\endif

\connect :"dbname"

CREATE SCHEMA :"schema" AUTHORIZATION :"admin_user";

-- Required extensions
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_sphere";
