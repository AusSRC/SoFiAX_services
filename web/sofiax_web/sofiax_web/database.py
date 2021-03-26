#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:52:00 2021
"""

#import dj_database_url
#db_from_env = dj_database_url.config(conn_max_age=500)
#DATABASES['default'].update(db_from_env)

DATABASES = {
    'default': {
        'ENGINE': os.environ.get("SQL_ENGINE", 'django.db.backends.postgresql'),
        'OPTIONS': {
            'options': '-c search_path=public,wallaby'
        },
        'NAME':  os.environ.get("SQL_DATABASE"),
        'USER':  os.environ.get("SQL_USER", "admin"),
        'PASSWORD': os.environ.get("SQL_PASSWORD", "admin"),
        'HOST':  os.environ.get("SQL_HOST", "sofiax_db"),
        'PORT':  os.environ.get("SQL_PORT", "5432"),
    },
    'wallaby': {
        'ENGINE': os.environ.get("SQL_ENGINE", 'django.db.backends.postgresql'),
        'OPTIONS': {
            'options': '-c search_path=wallaby'
        },
        'NAME':  os.environ.get("SQL_DATABASE"),
        'USER':  os.environ.get("SQL_USER", "admin"),
        'PASSWORD': os.environ.get("SQL_PASSWORD", "admin"),
        'HOST':  os.environ.get("SQL_HOST", "sofiax_db"),
        'PORT':  os.environ.get("SQL_PORT", "5432"),
    }
}
