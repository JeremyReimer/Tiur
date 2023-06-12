#!/bin/sh

# Start gunicorn
gunicorn -c config/gunicorn/prod.py

# Start nginx in foreground mode
exec nginx -g 'daemon=off;'
