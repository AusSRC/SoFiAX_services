# start from an official image
FROM nginx

RUN apt-get update 
RUN apt-get -y upgrade 
RUN apt-get install -y openssl
RUN mkdir -p /config/nginx
    
COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./ssl.conf /config/nginx/ssl.conf