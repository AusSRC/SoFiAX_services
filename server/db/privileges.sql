-- Privileges on the tables of the installed modules. Run by install-modules.sh
-- with psql variables, after the module tables have been created.

-- VO users, if they were created
SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gavo') AS has_vo_users \gset
\if :has_vo_users
GRANT ALL ON DATABASE :"dbname" TO gavo;
GRANT ALL ON DATABASE :"dbname" TO gavoadmin;
GRANT CONNECT ON DATABASE :"dbname" TO untrusted;

GRANT ALL ON SCHEMA public TO gavo;
GRANT ALL ON SCHEMA public TO gavoadmin;
GRANT USAGE ON SCHEMA public TO untrusted;

GRANT SELECT ON ALL TABLES IN SCHEMA :"schema" TO gavoadmin;
GRANT SELECT ON ALL TABLES IN SCHEMA :"schema" TO gavo;
GRANT SELECT ON ALL TABLES IN SCHEMA :"schema" TO untrusted;

GRANT USAGE ON SCHEMA :"schema" TO gavoadmin;
GRANT USAGE ON SCHEMA :"schema" TO gavo;
GRANT USAGE ON SCHEMA :"schema" TO untrusted;
\endif

-- SURVEY user, if it was created
SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'survey_user') AS has_survey_user \gset
\if :has_survey_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA :"schema" to survey_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA :"schema" to survey_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA :"schema" to survey_user;
\endif
