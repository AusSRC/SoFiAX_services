# start from an official image
FROM nginx

RUN apt-get update && apt-get -y upgrade && \
    apt-get install openssl && \
    mkdir -p /config/nginx && \
    mkdir -p /etc/ssl &&  \
    openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
    -subj "/C=AU/CN=localhost" \
    -keyout /etc/ssl/localhost.key  -out /etc/ssl/localhost.crt

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./ssl.conf /config/nginx/ssl.conf