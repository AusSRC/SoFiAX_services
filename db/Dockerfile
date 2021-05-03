FROM ubuntu:20.04
WORKDIR /src

# time zone
ENV TZ=Australia/Perth
RUN apt-get update && \
    apt-get install -y tzdata

# install postgresql
RUN apt update && \
    apt install -y postgresql postgresql-contrib

# install dependencies
RUN apt-get upgrade -y && \
    apt-get install -y vim postgresql-contrib postgis postgresql-12-postgis-3 postgresql-pgsphere 

# copy
COPY init.sh create.sql db.sql update.sql privileges.sql ./

# run initialisation
COPY pg_hba.conf /etc/postgresql/12/main/
RUN chmod 777 /etc/postgresql/12/main/pg_hba.conf && \
    echo "listen_addresses = '*'" >> /etc/postgresql/12/main/postgresql.conf
RUN service postgresql start && \
    export PGUSER=postgres && \
    ./init.sh

# start postgresql
USER postgres
CMD [ "/usr/lib/postgresql/12/bin/postgres", "-D", "/var/lib/postgresql/12/main", "-c", "config_file=/etc/postgresql/12/main/postgresql.conf" ]