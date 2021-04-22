#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 10:34:59 2021

@author: bee
"""

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = '-=(gyah-@e$-ymbz02mhwu6461zv&1&8uojya413ylk!#bwa-l'
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]
if os.environ.get("DJANGO_ALLOWED_HOSTS") is not None:
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

#Variable for view configuration of website 
SITE_HEADER = os.environ.get("SITE_HEADER")
SITE_TITLE = os.environ.get("SITE_TITLE")
INDEX_TITLE = os.environ.get("INDEX_TITLE")
