#!/bin/bash
# Run the web application tests against a throwaway database.
#
#   web/tests/run.sh [pytest arguments]
#
# A PostgreSQL container is started from server/db with its data in memory, on a
# private network without internet access and without published ports. The tests
# run in a one-off container built from web/. Everything is removed afterwards.
# Nothing is shared with a deployment: names are prefixed with sofiax_test, and
# the tests refuse to run against any database other than sofiax_test.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUN="sofiax_test_$$"
NETWORK="${RUN}_network"
DATABASE="${RUN}_db"
DATABASE_NAME="sofiax_test"
MODULES="core,metadata,operations"

cleanup() {
    docker rm -f "${DATABASE}" > /dev/null 2>&1 || true
    docker network rm "${NETWORK}" > /dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Building images"
docker build -q -t sofiax_test_db "${ROOT}/server/db" > /dev/null
docker build -q -t sofiax_test_web "${ROOT}/web" > /dev/null
# The web image with the test requirements
docker build -q -t sofiax_test_runner -f - "${ROOT}/web/tests" > /dev/null << 'DOCKERFILE'
FROM sofiax_test_web
COPY requirements.txt /tmp/test-requirements.txt
RUN pip install --no-cache-dir -r /tmp/test-requirements.txt
DOCKERFILE

echo "Starting database"
docker network create --internal "${NETWORK}" > /dev/null
docker run -d --name "${DATABASE}" \
    --network "${NETWORK}" --network-alias database \
    --tmpfs /var/lib/postgresql/data \
    -e MODULES="${MODULES}" \
    -e DATABASE_NAME="${DATABASE_NAME}" \
    -e DATABASE_SCHEMA=survey \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=test \
    -e DATABASE_ADMIN_PASSWORD=test \
    -e DATABASE_SURVEY_PASSWORD=test \
    -e VO_FEED_PASSWORD=test \
    -e VO_TRUSTED_PASSWORD=test \
    -e VO_UNTRUSTED_PASSWORD=test \
    sofiax_test_db > /dev/null

# The database only accepts TCP connections once it has been initialised
for i in $(seq 1 90); do
    if docker exec "${DATABASE}" pg_isready -q -h 127.0.0.1 -U postgres -d "${DATABASE_NAME}" 2> /dev/null; then
        break
    fi
    if [ "$(docker inspect -f '{{.State.Running}}' "${DATABASE}" 2> /dev/null)" != "true" ] || [ "$i" = 90 ]; then
        echo "Database failed to start" >&2
        docker logs "${DATABASE}" 2>&1 | tail -20 >&2
        exit 1
    fi
    sleep 1
done

echo "Running tests"
# The source is mounted read only so that the current code is tested and nothing is written to it
docker run --rm \
    --network "${NETWORK}" \
    -v "${ROOT}/web:/opt/services/survey_web/src:ro" \
    -e PYTHONDONTWRITEBYTECODE=1 \
    -e MPLCONFIGDIR=/tmp/matplotlib \
    -e PROJECT=TEST \
    -e MODULES="${MODULES}" \
    -e DEBUG=False \
    -e DJANGO_SECRET_KEY=test \
    -e DJANGO_ALLOWED_HOSTS=testserver \
    -e SESSION_COOKIE_SECURE=False \
    -e CSRF_COOKIE_SECURE=False \
    -e SITE_NAME=Test -e SITE_HEADER=Test -e SITE_TITLE=Test -e INDEX_TITLE=Test \
    -e DATABASE_HOST=database \
    -e DATABASE_PORT=5432 \
    -e DATABASE_NAME="${DATABASE_NAME}" \
    -e DATABASE_USER=postgres \
    -e DATABASE_PASSWORD=test \
    -e SEARCH_PATH=survey,public \
    sofiax_test_runner \
    python -m pytest -p no:cacheprovider "$@"
