#!/bin/bash

set -e

# Initialise database (for new database connection)
init () {
  echo "Running makemigrations"
  python manage.py makemigrations

  echo "Running migrate"
  python manage.py migrate

  echo "Creating local superuser"
  python manage.py shell -c """
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@csiro.au', 'admin')
"""

  gunicorn -b :8000 api.wsgi:application
}

# Start the service
start () {
  gunicorn -b :8000 api.wsgi:application
}

case ${1} in
  init)
    init
    ;;
  start)
    start
    ;;
  *)
    exec "$@"
    ;;
esac