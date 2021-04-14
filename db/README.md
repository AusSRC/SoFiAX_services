# db

Subdirectory containing sql scripts for PostgreSQL database initialisation. 

## Installation

To install and initialise a PostgreSQL instance with the SoFiAX_services schema run the following after cloning the repository. Note that the database requires two libraries: `postgis` and `pg_sphere`.

You may need to create a default user and database. This [tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04) may help with this.

```
# install postgresql and libraries (note we are using postgresql version 12)
sudo apt install postgresql postgresql-contrib postgis sudo apt-get install postgresql-12-pgsphere

# start postgresql
sudo systemctl start postgresql

# run initialisation scripts
cd SoFiAX_services/db
./init.sh
```
