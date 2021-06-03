#!/bin/bash

# Create database and users from empty PostgreSQL server locally
createdb sofiadb
psql -h localhost -f create.sql
psql -h localhost -f db.sql
psql -h localhost -f update.sql
psql -h localhost -f privileges.sql
psql -h localhost -f sofia_fields.sql