#!/bin/bash
# Create the tables of the given modules (files in /sql/modules) and update the
# privileges. Run by init.sh on first startup. To add a module to an existing
# database: docker exec survey_db install-modules <module> [<module> ...]
set -eu

DATABASE_NAME="${DATABASE_NAME:-surveydb}"
DATABASE_SCHEMA="${DATABASE_SCHEMA:-survey}"
DATABASE_ADMIN_USERNAME="${DATABASE_ADMIN_USERNAME:-admin}"
SQL_DIR="${SQL_DIR:-/sql}"

run_psql() {
    psql -v ON_ERROR_STOP=1 --no-psqlrc --quiet --username "${POSTGRES_USER:-postgres}" --dbname "${DATABASE_NAME}" "$@"
}

for m in "$@"; do
    if [ ! -f "${SQL_DIR}/modules/$m.sql" ]; then
        echo "MODULES: unknown module $m" >&2
        exit 1
    fi
done

# Tables are created in the schema and owned by the admin user
for m in "$@"; do
    echo "Installing module $m"
    PGOPTIONS="-c search_path=${DATABASE_SCHEMA},public -c role=${DATABASE_ADMIN_USERNAME}" \
        run_psql --single-transaction -f "${SQL_DIR}/modules/$m.sql"
done

run_psql -v dbname="${DATABASE_NAME}" -v schema="${DATABASE_SCHEMA}" -f "${SQL_DIR}/privileges.sql"
