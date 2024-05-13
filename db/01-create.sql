-- Create database
CREATE DATABASE surveydb WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';

-- Create admin user
CREATE USER "admin";
ALTER USER "admin" WITH PASSWORD 'admin';
ALTER USER "admin" WITH SUPERUSER;
ALTER DATABASE surveydb OWNER TO "admin";

-- Create SURVEY user
CREATE USER "survey_user";
ALTER USER "survey_user" WITH PASSWORD 'survey_user';

-- Create VO user
CREATE USER "gavo";
ALTER USER "gavo" WITH PASSWORD 'gavo';
CREATE USER "gavoadmin";
ALTER USER "gavoadmin" WITH PASSWORD 'gavoadmin';
CREATE USER "untrusted";
ALTER USER "untrusted" WITH PASSWORD 'untrusted';
