FROM library/postgres:17.0
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y vim \
    postgresql-contrib \
    postgresql-17-postgis-3 \
    postgresql-17-pgsphere
RUN echo "en_US.UTF-8 UTF-8"> /etc/locale.gen && locale-gen

# The database is initialised by init.sh from the SQL files of the modules in MODULES
COPY create.sql defaults.sql privileges.sql /sql/
COPY modules/ /sql/modules/
COPY install-modules.sh /usr/local/bin/install-modules
COPY init.sh /docker-entrypoint-initdb.d/init.sh
RUN chmod +x /usr/local/bin/install-modules /docker-entrypoint-initdb.d/init.sh
