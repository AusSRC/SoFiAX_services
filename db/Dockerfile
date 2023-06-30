FROM library/postgres:15.3
RUN apt-get update && apt-get upgrade -y && apt-get install -y postgresql-contrib vim
RUN apt-get install -y postgresql-15-postgis-3
RUN apt-get install -y postgresql-15-pgsphere
COPY *.sql /docker-entrypoint-initdb.d/