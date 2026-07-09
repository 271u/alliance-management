# config/gunicorn.conf.py

import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", "3"))

accesslog = "-"
errorlog = "-"

# Safe here because Gunicorn is only reachable from Docker/internal Traefik,
# not directly from the public internet.
forwarded_allow_ips = os.getenv("GUNICORN_FORWARDED_ALLOW_IPS", "*")

access_log_format = (
    '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s '
    '"%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" '
    'socket_ip=%(h)s request_time_us=%(D)s'
)
