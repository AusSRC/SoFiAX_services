FROM library/postgres:12.2

RUN apt-get update && apt-get upgrade -y && apt-get install -y vim && \
    apt-get install -y postgresql-contrib && \
    apt-get install -y postgresql-12-postgis-3 && \
    apt-get install -y postgresql-12-pgsphere 
        
COPY ./init.sh /docker-entrypoint-initdb.d/20-init.sh

COPY create.sql /create.sql
COPY db.sql /db.sql
COPY update.sql /update.sql
COPY privileges.sql /privileges.sql

RUN chmod +x /docker-entrypoint-initdb.d/20-init.sh
