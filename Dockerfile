FROM python:3.9-bullseye
RUN apt-get update && apt-get install nginx -y --no-install-recommends
COPY config/nginx/tiur.com /etc/nginx/sites-available/tiur.com
