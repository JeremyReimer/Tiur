server_tokens               off;
access_log                  /var/log/nginx/tiur.log;
error_log                   /var/log/nginx/tiur.log;
daemon                      off;

# This configuration will be changed to redirect to HTTPS later
server {
  server_name               .tiur.com;
  listen                    80;
  location / {
    proxy_pass              http://localhost:8000;
    proxy_set_header        Host $host;
  }
  location /static {
    autoindex on;
    alias /var/www/tiur/static/;
  }
}
