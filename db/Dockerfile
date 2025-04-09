FROM library/postgres:17.0
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y vim \
    postgresql-contrib \
    postgresql-17-postgis-3 \
    postgresql-17-pgsphere
RUN echo "en_US.UTF-8 UTF-8"> /etc/locale.gen && locale-gen
COPY *.sql /docker-entrypoint-initdb.d/
