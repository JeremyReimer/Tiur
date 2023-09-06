#!/bin/sh

# Start gunicorn
gunicorn -c config/gunicorn/prod.py -t 120

# Start nginx in foreground mode
exec nginx -g 'daemon off;' "$@"
