#!/bin/bash


# Exit immediately if a command exits with a non-zero status
set -e

# Treat unset variables as an error and exit immediately
set -u

# Ensure the script exits if any command in a pipeline fails
set -o pipefail

# Default email
DEFAULT_EMAIL="operations@aussrc.org"

# Usage function
usage() {
    echo "Usage: $0 -d DOMAIN [-e EMAIL] [-s]"
    echo "  -d DOMAIN   The domain for which to request the certificate"
    echo "  -e EMAIL    The email address for notifications (default: $DEFAULT_EMAIL)"
    echo "  -s          Use staging environment to avoid hitting request limits"
    exit 1
}

# Default values
STAGING=0

# Parse arguments
while getopts ":d:e:s" opt; do
    case ${opt} in
        d )
            DOMAIN=$OPTARG
            ;;
        e )
            EMAIL=$OPTARG
            ;;
        s )
            STAGING=1
            ;;
        \? )
            usage
            ;;
    esac
done

# Check if DOMAIN is set
if [ -z "${DOMAIN:-}" ]; then
    usage
fi

# Set default email if not provided
EMAIL=${EMAIL:-$DEFAULT_EMAIL}

# Create letsencrypt and www directories in certs if they don't exist
mkdir -p ./letsencrypt
mkdir -p ./www

# Determine whether to use the staging environment
if [ "$STAGING" -ne 0 ]; then
    STAGING_ARG="--staging"
else
    STAGING_ARG=""
fi

# Request the certificate
docker run --rm -p 80:80 -v "./letsencrypt:/etc/letsencrypt" \
    certbot/certbot certonly --standalone $STAGING_ARG -d "$DOMAIN" \
    --email "$EMAIL" --agree-tos --non-interactive
