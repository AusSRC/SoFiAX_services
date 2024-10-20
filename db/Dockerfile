# Use the latest version of PostgreSQL
FROM postgres:15.8

# Install necessary packages in a single RUN command to reduce the number of layers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-contrib \
    postgresql-15-postgis \
    postgresql-15-pgsphere \
    vim && \
    rm -rf /var/lib/apt/lists/*

# Set locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Copy db_files directory to the container
COPY *.sql /db-files/