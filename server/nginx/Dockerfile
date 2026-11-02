FROM nginx

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y openssl
RUN mkdir -p /config/nginx
RUN mkdir -p /etc/ssl

RUN openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 \
    -subj "/C=AU/CN=localhost" \
    -keyout /etc/ssl/localhost.key  -out /etc/ssl/localhost.crt

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./ssl.conf /config/nginx/ssl.conf