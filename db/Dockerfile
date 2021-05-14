FROM library/postgres:12.2

# time zone
ENV TZ=Australia/Perth

# install postgresql and dependencies
RUN apt-get update && apt-get upgrade -y && \ 
    apt-get install -y tzdata \
    vim \
    postgresql-contrib  \
    postgresql-12-postgis-3  \
    postgresql-12-pgsphere 

# copy
COPY ./init.sh /docker-entrypoint-initdb.d/20-init.sh
COPY create.sql db.sql update.sql privileges.sql ./

# run initialisation
COPY pg_hba.conf /etc/postgresql/12/main/
RUN chmod 777 /etc/postgresql/12/main/pg_hba.conf && \
    echo "listen_addresses = '*'" >> /etc/postgresql/12/main/postgresql.conf

RUN chmod +x /docker-entrypoint-initdb.d/20-init.sh    
    
# start postgresql
USER postgres
CMD [ "/usr/lib/postgresql/12/bin/postgres", "-c", "config_file=/etc/postgresql/12/main/postgresql.conf" ]
