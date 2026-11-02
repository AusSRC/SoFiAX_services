#!/bin/bash
# Initialise the database on first startup (empty data directory) using
# environment variables (see server/.env.example).
set -eu

SQL_DIR="${SQL_DIR:-/sql}"

# Required
: "${MODULES:?MODULES is not set}"
: "${DATABASE_ADMIN_PASSWORD:?DATABASE_ADMIN_PASSWORD is not set}"

# Optional: the survey user (DATABASE_SURVEY_PASSWORD) and the users of the VO service
# (VO_FEED_PASSWORD, VO_TRUSTED_PASSWORD, VO_UNTRUSTED_PASSWORD) are created if their passwords are set
OPTIONAL_USERS=()
if [ -n "${DATABASE_SURVEY_PASSWORD:-}" ]; then
    OPTIONAL_USERS+=(-v survey_password="${DATABASE_SURVEY_PASSWORD}")
fi
if [ -n "${VO_FEED_PASSWORD:-}${VO_TRUSTED_PASSWORD:-}${VO_UNTRUSTED_PASSWORD:-}" ]; then
    : "${VO_FEED_PASSWORD:?VO_FEED_PASSWORD is not set}"
    : "${VO_TRUSTED_PASSWORD:?VO_TRUSTED_PASSWORD is not set}"
    : "${VO_UNTRUSTED_PASSWORD:?VO_UNTRUSTED_PASSWORD is not set}"
    OPTIONAL_USERS+=(
        -v vo_feed_password="${VO_FEED_PASSWORD}"
        -v vo_trusted_password="${VO_TRUSTED_PASSWORD}"
        -v vo_untrusted_password="${VO_UNTRUSTED_PASSWORD}"
    )
fi

# Modules to install (comma separated). The names used before the modules were
# restructured are still accepted.
REQUESTED="$(echo "${MODULES}" | tr -d '[:space:]' | tr ',' '\n' | sed \
    -e 's/^metadata$/core/' \
    -e 's/^wallaby_operations$/wallaby/' \
    -e 's/^wallaby_kinematics$/wallaby/' \
    -e 's/^dingo_gama$/dingo/')"
has_module() {
    echo "${REQUESTED}" | grep -qx "$1"
}
for m in ${REQUESTED}; do
    if [ ! -f "${SQL_DIR}/modules/$m.sql" ]; then
        echo "MODULES: unknown module $m" >&2
        exit 1
    fi
done
if ! has_module core; then
    echo "MODULES: core is required" >&2
    exit 1
fi
if has_module wallaby && ! has_module operations; then
    echo "MODULES: wallaby requires operations" >&2
    exit 1
fi
# Modules are installed in this order
MODULE_NAMES=""
for m in core operations wallaby dingo; do
    if has_module "$m"; then
        MODULE_NAMES="${MODULE_NAMES} $m"
    fi
done

psql -v ON_ERROR_STOP=1 --no-psqlrc --quiet --username "${POSTGRES_USER:-postgres}" --dbname postgres \
    -v dbname="${DATABASE_NAME:-surveydb}" \
    -v schema="${DATABASE_SCHEMA:-survey}" \
    -v admin_user="${DATABASE_ADMIN_USERNAME:-admin}" \
    -v admin_password="${DATABASE_ADMIN_PASSWORD}" \
    "${OPTIONAL_USERS[@]}" \
    -f "${SQL_DIR}/create.sql"

install-modules ${MODULE_NAMES}
