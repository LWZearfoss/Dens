FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
COPY sites-enabled /etc/nginx/conf.d
RUN rm /etc/nginx/mime.types
COPY mime /etc/nginx
RUN mkdir /etc/nginx/ssl/
COPY ssl/ /etc/nginx/ssl/