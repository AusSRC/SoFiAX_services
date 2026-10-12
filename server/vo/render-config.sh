#!/bin/sh
# Render the DaCHS configuration files from the templates in $VO_TEMPLATES
# using environment variables (see .env.example in the repository root).
set -eu

TEMPLATES="${VO_TEMPLATES:-/templates}"
GAVO_ROOT="${GAVO_ROOT:-/var/gavo}"
GAVO_INPUTS="${GAVO_INPUTS:-${GAVO_ROOT}/inputs}"
GAVO_SETTINGS="${GAVO_SETTINGS:-/etc/gavo.rc}"

# Required
: "${PROJECT:?PROJECT is not set}"
: "${MODULES:?MODULES is not set}"
: "${DATABASE_ADMIN_PASSWORD:?DATABASE_ADMIN_PASSWORD is not set}"
: "${VO_FEED_PASSWORD:?VO_FEED_PASSWORD is not set}"
: "${VO_TRUSTED_PASSWORD:?VO_TRUSTED_PASSWORD is not set}"
: "${VO_UNTRUSTED_PASSWORD:?VO_UNTRUSTED_PASSWORD is not set}"

# Optional
export DATABASE_HOST="${DATABASE_HOST:-database}"
export DATABASE_PORT="${DATABASE_PORT:-5432}"
export DATABASE_NAME="${DATABASE_NAME:-surveydb}"
export DATABASE_ADMIN_USERNAME="${DATABASE_ADMIN_USERNAME:-admin}"
export DATABASE_SCHEMA="${DATABASE_SCHEMA:-survey}"
export DATABASE_ADMIN_USERNAME="${DATABASE_ADMIN_USERNAME:-admin}"
export SERVER_URL="${SERVER_URL:-https://localhost}"
export VO_TITLE="${VO_TITLE:-${PROJECT}}"
export VO_SHORT_NAME="${VO_SHORT_NAME:-${PROJECT}}"
export VO_DESCRIPTION="${VO_DESCRIPTION:-${PROJECT} survey}"
export VO_REFERENCE_URL="${VO_REFERENCE_URL:-https://aussrc.org/}"
export VO_CREATION_DATE="${VO_CREATION_DATE:-2020-04-24}"
export VO_CONTACT_NAME="${VO_CONTACT_NAME:-AusSRC}"
export VO_CONTACT_EMAIL="${VO_CONTACT_EMAIL:-}"
export VO_CONTACT_ADDRESS="${VO_CONTACT_ADDRESS:-}"

# Only these variables are substituted, any other "$" in a template is kept
VARS='
    $PROJECT
    $DATABASE_HOST $DATABASE_PORT $DATABASE_NAME $DATABASE_SCHEMA
    $DATABASE_ADMIN_USERNAME $DATABASE_ADMIN_PASSWORD
    $VO_FEED_PASSWORD $VO_TRUSTED_PASSWORD $VO_UNTRUSTED_PASSWORD
    $SERVER_URL
    $VO_TITLE $VO_SHORT_NAME $VO_DESCRIPTION $VO_REFERENCE_URL $VO_CREATION_DATE
    $VO_CONTACT_NAME $VO_CONTACT_EMAIL $VO_CONTACT_ADDRESS
'

render() {
    mkdir -p "$(dirname "$2")"
    envsubst "$VARS" < "${TEMPLATES}/$1" > "$2"
}

# Write "key: value" (or "key = value") only if the value is set
setting() {
    if [ -n "$3" ]; then echo "$1$2 $3"; fi
}

for f in dsn feed trustedquery untrustedquery defaultmeta.txt; do
    render "$f" "${GAVO_ROOT}/etc/$f"
done
render gavo.rc "${GAVO_SETTINGS}"

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
    if [ ! -f "${TEMPLATES}/modules/$m.rd" ]; then
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

# Assemble vo.rd from the modules
RD="${GAVO_INPUTS}/survey/vo.rd"
mkdir -p "$(dirname "${RD}")"
{
    cat "${TEMPLATES}/header.rd"
    for m in ${MODULE_NAMES}; do
        echo
        cat "${TEMPLATES}/modules/$m.rd"
    done
    echo
    cat "${TEMPLATES}/footer.rd"
} | envsubst "$VARS" > "${RD}"

setting sslmode " =" "${DATABASE_SSLMODE:-}" >> "${GAVO_ROOT}/etc/dsn"

# Optional server tuning, DaCHS defaults apply to anything not set
{
    setting sqlTimeout : "${VO_SQL_TIMEOUT:-}"
    setting maxUploadSize : "${VO_MAX_UPLOAD_SIZE:-}"
    echo
    echo "[async]"
    setting defaultExecTime : "${VO_DEFAULT_EXEC_TIME:-}"
    setting defaultExecTimeSync : "${VO_DEFAULT_EXEC_TIME_SYNC:-}"
    setting maxTAPRunning : "${VO_MAX_TAP_RUNNING:-}"
    setting maxUserUWSRunningDefault : "${VO_MAX_USER_UWS_RUNNING:-}"
    setting hardMAXREC : "${VO_HARD_MAXREC:-}"
    echo
    echo "[db]"
    setting indexWorkMem : "${VO_INDEX_WORK_MEM:-}"
} >> "${GAVO_SETTINGS}"
