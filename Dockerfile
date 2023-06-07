# Dockerfile
FROM python:3.9-bullseye

# Install nginx
RUN apt-get update && apt-get install nginx -y --no-install-recommends
COPY config/nginx/tiur.com /etc/nginx/sites-available/tiur.com
RUN ln -s /etc/nginx/sites-available/tiur.com /etc/nginx/sites-enabled

# Create logfile directories and set permissions
RUN mkdir /var/log/gunicorn
RUN mkdir /var/run/gunicorn
RUN mkdir /var/www/tiur
RUN chown -cR jeremy_reimer:jeremy_reimer /var/{log,run}/gunicorn
RUN chown -cR jeremy_reimer:jeremy_reimer /var/www/tiur

# Install dependencies
RUN pip install -r requirements.txt

# Start server
EXPOSE 80
RUN gunicorn -c config/gunicorn/prod.py
RUN systemctl start nginx
