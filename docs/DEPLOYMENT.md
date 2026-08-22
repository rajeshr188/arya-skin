# Deployment

## Current development setup

- SQLite database at `db.sqlite3` (ignored by Git)
- local uploaded media under `media/` (ignored by Git)
- static source under `static/`; WhiteNoise is configured for collected static
- `uv` lockfile and a generated `requirements.txt`
- Docker Compose can run the development application against PostgreSQL 16;
  SQLite remains the zero-configuration local default.

## Staging baseline

Milestone 7A provides environment-driven PostgreSQL, host/origin validation,
secure-cookie and HTTPS settings, guarded proxy-header trust, a non-root Gunicorn
container, immutable static collection, JSON operational logs, a database health
endpoint, and CI against PostgreSQL.

Staging is forcibly noindex and protected with HTTPS Basic authentication. The
health endpoint is the only authentication bypass. Staging media may use one
mounted persistent volume with backups; it is not suitable for multiple web
replicas. See `STAGING.md` for the required environment and acceptance checks.

## Production target (Milestone 7B)

- supported Python 3.12+ runtime;
- PostgreSQL via `psycopg` and an environment-driven connection;
- Gunicorn behind an HTTPS reverse proxy/platform router;
- WhiteNoise for immutable collected static files;
- Cloudflare R2 via a custom domain for user-uploaded Wagtail media;
- durable database/media backups and tested restore procedures.

### Production media storage

Production refuses to start unless `USE_R2_MEDIA=True` and all five R2 media
settings in `.env.example` are present. The token must have access only to
`arya-skin-production-media`; do not reuse the backup token. Connect
`media.drnareshrathod.com` in the bucket's **Custom Domains** settings and keep
the development-only `r2.dev` URL disabled. The custom domain is public because
the website must render Wagtail images and linked public documents.

Before cutover, upload the staging media to R2 and verify representative original
images, generated renditions, and documents through the custom domain. Keep the
staging media volume unchanged until the production database and media restore
test has passed.

`arya-skin-production-backups` is reserved for private, client-side encrypted
database backups. It must not have a public custom domain and must use a separate
bucket-scoped token. Creating this bucket alone does not enable off-server
backups; the upload, retention, alerting, and restore proof remain a separate
production task.

## Required configuration before public launch

- strong `SECRET_KEY`; `DJANGO_DEBUG=False`;
- production `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and
  `WAGTAILADMIN_BASE_URL`;
- final PostgreSQL sizing, backup retention, restore testing, and connection
  limits;
- production HSTS rollout after TLS is confirmed, including deliberate
  subdomain/preload decisions;
- transactional email provider for operational mail;
- bucket-scoped object-storage credentials, active media custom domain, and a
  private backup-bucket policy;
- error-monitoring provider, alert routing, log retention, and named backup
  ownership;
- production Site hostname/port updated in Wagtail admin;
- approved privacy notice and analytics consent behavior;
- clinic-owned GA4 or governed GTM account, with analytics disabled until final
  approval and enhanced outbound/form measurement switched off;
- clinic-owned Search Console property and least-privilege owner access.

The Wagtail Site record is the canonical URL authority. Set its hostname to the
single preferred public domain and its port to 443 before launch; then verify
page canonicals, JSON-LD IDs, `robots.txt`, redirects, and `sitemap.xml` all use
that HTTPS origin.

Never commit secrets. Analytics identifiers are not secrets, but still require
approved account ownership and privacy configuration.

## Release outline

```text
Build:    docker build --tag arya-skin:<release> .
Release:  /app/scripts/release.sh
Web:      gunicorn --config gunicorn.conf.py django_project.wsgi
Health:   GET /healthz/
```

Migrations execute once as a release task, not concurrently in every web worker.
Docker Compose remains a local development aid and is not production
orchestration. The application service must use an HTTPS router and a platform
secret manager. Django should trust `X-Forwarded-Proto` only when that router
strips the client-supplied value and sets its own.
