# Dockerfile
FROM python:3.9-bullseye

# Install nginx
RUN apt-get update 
RUN apt-get install nginx -y --no-install-recommends

# Install python_ldap dependencies
RUN apt-get install libsasl2-dev libldap2-dev libssl-dev -y

# Configure nginx
COPY config/nginx/tiur.com /etc/nginx/sites-available/tiur.com
RUN ln -s /etc/nginx/sites-available/tiur.com /etc/nginx/sites-enabled

# Create non-privileged user to run the Django app
RUN useradd -ms /bin/bash tiuruser

# Copy application to non-privileged user's home directory
RUN mkdir /home/tiuruser/tiur
COPY . /home/tiuruser/tiur

# Create logfile, user, and nginx directories
RUN mkdir /var/log/gunicorn
RUN mkdir /var/run/gunicorn
RUN mkdir /var/www/tiur
RUN mkdir /var/lib/nginx/body
RUN mkdir /var/lib/nginx/fastcgi
RUN mkdir /var/lib/nginx/proxy

# Set permissions
RUN chown -R tiuruser:tiuruser /var/log/gunicorn
RUN chown -R tiuruser:tiuruser /var/run/gunicorn
RUN chown -R tiuruser:tiuruser /var/www/tiur
RUN chown -R tiuruser:tiuruser /var/log/nginx
RUN chown -R tiuruser:tiuruser /var/lib/nginx
RUN chown -R tiuruser:tiuruser /run

# Install dependencies (including gunicorn)
RUN pip install -r /home/tiuruser/tiur/requirements.txt

# Switch to non-privileged user
USER tiuruser
WORKDIR /home/tiuruser/tiur

# Collect static files
RUN python3 manage.py collectstatic

# Expose HTTP port to server
EXPOSE 80

# Copy startup file
COPY entrypoint.sh /usr/local/bin

# Start gunicorn and nginx servers
CMD ["entrypoint.sh"]
