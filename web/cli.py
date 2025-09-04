#!/usr/bin/env python
"""Custom entrypoint into Django web application."""
import os
import sys
import logging
import django
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line


logging.basicConfig(level=logging.INFO)


def main():
    """Run local version of sofia_web application
    1. Parse user defined config
    2. Check database connection
    3. Initialise database if necessary
    4. Done...
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    logging.info('Starting sofia web application...')

    # Database migrations
    logging.info('Django database migrations...')
    call_command("migrate", interactive=False)

    # Create default user
    logging.info('Creating default user')
    User = get_user_model()
    if not User.objects.filter(username=settings.DEFAULT_USER):
        User.objects.create_superuser(
            username=settings.DEFAULT_USER,
            password=settings.DEFAULT_PASSWORD
        )
    else:
        logging.info('Default user already exists...')

    # Start server
    logging.info('Starting server...')
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
