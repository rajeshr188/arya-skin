# Deployment

## Current development setup

- SQLite database at `db.sqlite3` (ignored by Git)
- local uploaded media under `media/` (ignored by Git)
- static source under `static/`; WhiteNoise is configured for collected static
- `uv` lockfile and a generated `requirements.txt`
- Gunicorn/Docker starter files retained from Lithium

## Production target

- supported Python 3.12+ runtime;
- PostgreSQL via `psycopg` and an environment-driven connection;
- Gunicorn behind an HTTPS reverse proxy/platform router;
- WhiteNoise for immutable collected static files;
- S3-compatible/object storage and optional CDN for user-uploaded Wagtail media;
- durable database/media backups and tested restore procedures.

## Required configuration before launch

- strong `SECRET_KEY`; `DEBUG=False`;
- production `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and
  `WAGTAILADMIN_BASE_URL`;
- environment-driven PostgreSQL settings;
- secure cookies, HTTPS redirect/HSTS after TLS is confirmed;
- transactional email provider for operational mail;
- object-storage credentials and private/public access policy as appropriate;
- error monitoring, log retention, health checks, and backup ownership;
- production Site hostname/port updated in Wagtail admin.

The Wagtail Site record is the canonical URL authority. Set its hostname to the
single preferred public domain and its port to 443 before launch; then verify
page canonicals, JSON-LD IDs, `robots.txt`, redirects, and `sitemap.xml` all use
that HTTPS origin.

Never commit secrets. Analytics identifiers are not secrets, but still require
approved account ownership and privacy configuration.

## Release outline

```powershell
uv sync --frozen --no-dev
uv run manage.py check --deploy
uv run manage.py migrate --noinput
uv run manage.py collectstatic --noinput
```

Run tests in CI before release. Migrations should execute once as a release task,
not concurrently in every web worker. The existing Docker Compose file remains a
local PostgreSQL aid and is not yet a production orchestration definition.
