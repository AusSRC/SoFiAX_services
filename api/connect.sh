#!/bin/bash

'''
In running these commands you will face issues with migrating. 
You will have to manually resolve issues which may include:
    - Foreign key relations
    - varchar to models.CharField(max_length=-1)

As a temporary fix I have set max_length=200 which is the max for Django.
'''

# Create WALLABY database
createdb sofiadb
psql -h localhost -f create.sql
psql -h localhost -f db.sql

# Create Django models for tables
python3 manage.py startapp run
python3 manage.py startapp detection
python3 manage.py startapp instance
python3 manage.py startapp products

# Autogenerate models.py file
python3 manage.py inspectdb detection --database wallaby > detection/models.py
python3 manage.py inspectdb instance --database wallaby > instance/models.py
python3 manage.py inspectdb run --database wallaby > run/models.py
python3 manage.py inspectdb products --database wallaby > products/models.py

# Updated model fields (for commenting, tagging and final source catalogue)
python3 manage.py startapp sources
python3 manage.py startapp tag
python3 manage.py startapp comments

python3 manage.py inspectdb sources --database wallaby > sources/models.py
python3 manage.py inspectdb tag --database wallaby > tag/models.py
python3 manage.py inspectdb comments --database wallaby > comments/models.py
python3 manage.py inspectdb tag_detection --database wallaby >> tag/models.py