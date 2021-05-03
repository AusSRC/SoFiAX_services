#!/bin/bash

# Create database and users from empty PostgreSQL server locally
createdb sofiadb
psql -f create.sql
psql -f db.sql
psql -f update.sql
psql -f privileges.sql
