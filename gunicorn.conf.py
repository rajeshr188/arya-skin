import os


bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))
accesslog = "-"
# Keep successful-request logs useful without recording IP addresses, referrers,
# user agents, or query strings. Application warnings/errors use the JSON
# formatter configured in Django.
access_log_format = (
    '{"logger":"gunicorn.access","method":"%(m)s","path":"%(U)s",'
    '"status":%(s)s,"duration_us":%(D)s}'
)
errorlog = "-"
capture_output = True
