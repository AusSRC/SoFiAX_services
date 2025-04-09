\connect wallabydb

GRANT ALL ON DATABASE wallabydb TO gavo;
GRANT ALL ON DATABASE wallabydb TO gavoadmin;
GRANT CONNECT ON DATABASE wallabydb TO untrusted;

GRANT ALL ON SCHEMA public TO gavo;
GRANT ALL ON SCHEMA public TO gavoadmin;
GRANT USAGE ON SCHEMA public TO untrusted;

GRANT SELECT ON ALL TABLES IN SCHEMA wallaby TO gavoadmin;
GRANT SELECT ON ALL TABLES IN SCHEMA wallaby TO gavo;
GRANT SELECT ON ALL TABLES IN SCHEMA wallaby TO untrusted;

GRANT USAGE ON SCHEMA wallaby TO gavoadmin;
GRANT USAGE ON SCHEMA wallaby TO gavo;
GRANT USAGE ON SCHEMA wallaby TO untrusted;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA wallaby to wallaby_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA wallaby to wallaby_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA wallaby to wallaby_user;

-- Required extensions
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_sphere";
