FROM library/postgres:12.2

RUN apt-get update && apt-get upgrade -y && apt-get install -y vim && \
    apt-get install -y postgresql-contrib && \
    apt-get install -y postgresql-12-postgis-3 && \
    apt-get install -y postgresql-12-pgsphere 

COPY create.sql /docker-entrypoint-initdb.d/01_create.sql
COPY db.sql /docker-entrypoint-initdb.d/02_db.sql
COPY update.sql /docker-entrypoint-initdb.d/03_update.sql
COPY privileges.sql /docker-entrypoint-initdb.d/04_privileges.sql

