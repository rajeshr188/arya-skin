# Staging deployment runbook

Milestone 7A makes the application suitable for a private staging environment.
It does not authorize a public production launch or replace the outstanding
content, privacy, storage, monitoring, and operational approvals.

## Required services

- an HTTPS application service or trusted HTTPS reverse proxy;
- PostgreSQL 16 or another version supported by the locked Django release;
- one persistent volume mounted at `MEDIA_ROOT` for staging uploads;
- a secret manager for Django and staging-access credentials;
- database and media-volume backups.

The persistent filesystem option is intentionally limited to one staging web
replica. Production or horizontally scaled staging requires shared object
storage, which remains Milestone 7B work.

## Required environment

| Variable | Staging requirement |
| --- | --- |
| `DJANGO_ENVIRONMENT` | `staging` |
| `DJANGO_DEBUG` | `False` |
| `SECRET_KEY` | unique random value of at least 50 characters |
| `DATABASE_URL` | PostgreSQL URL; use the provider-required `sslmode` |
| `ALLOWED_HOSTS` | exact staging hostname, without scheme |
| `CSRF_TRUSTED_ORIGINS` | exact `https://` staging origin |
| `WAGTAILADMIN_BASE_URL` | exact `https://` staging origin |
| `STAGING_ACCESS_USERNAME` | reviewer username without a colon |
| `STAGING_ACCESS_PASSWORD` | unique random value of at least 16 characters |
| `MEDIA_ROOT` | mounted persistent-volume path |
| `HEALTH_CHECK_HOST` | a hostname present in `ALLOWED_HOSTS` |
| `TRUST_X_FORWARDED_PROTO` | `True` only for a proxy that strips and sets this header |

`SITE_NOINDEX` is forced on in staging. Secure session/CSRF cookies, HTTPS
redirects, and a short 300-second HSTS policy default on. Do not enable HSTS
subdomains or preload for a staging hostname.

Use `.env.example` as a key reference, not as a source of real secrets. Keep
deployment values in the platform secret manager rather than repository files or
shell history.

## Build and release

Build the same immutable image that will run on the application service:

```powershell
docker build --tag arya-skin:staging .
```

Run `scripts/release.sh` once as the platform release/pre-deploy task. It runs
the deployment checks, migrations, and static collection. Do not run migrations
concurrently in every web replica.

The image starts Gunicorn as a non-root user on `PORT` (default `8000`). Configure
the platform health probe for `/healthz/`; it bypasses reviewer authentication,
checks the database, exposes no database details, and is excluded from HTTPS
redirects for the container-local probe.

## First staging setup

1. Provision PostgreSQL and a persistent media volume with backups.
2. Configure the required environment and deploy the image.
3. Run the release task once.
4. Create the first Wagtail administrator using `python manage.py createsuperuser`
   in a one-off task; do not automate a default password.
5. In **Wagtail → Settings → Sites**, set the exact staging hostname and port
   `443`. Confirm canonicals, sitemap, robots, and JSON-LD use that origin.
6. Keep all incomplete clinic, legal, treatment, and article pages as drafts.
7. Use synthetic appointment data only. Delete test enquiries before copying or
   promoting any database.

## Acceptance checks

- unauthenticated `/` returns `401` and a `WWW-Authenticate` challenge;
- authenticated responses include
  `X-Robots-Tag: noindex, nofollow, noarchive`;
- `/healthz/` returns `200 {"status":"ok"}` without reviewer credentials;
- HTTP redirects to HTTPS except for the internal health endpoint;
- `/cms/` requires both staging access and a Wagtail staff login;
- appointment, CMS, and CSRF workflows operate over the staging hostname;
- static assets load from WhiteNoise and an uploaded test image survives a
  restart/redeploy;
- logs are one-line JSON and contain request paths but no query strings, bodies,
  appointment fields, or secrets;
- the provider has current database and media backups and a named owner;
- analytics remains disabled unless its separate approvals are complete.

The repository CI runs migrations and all tests against PostgreSQL and validates
a production security profile. A successful CI run and staging acceptance review
are prerequisites for Milestone 7B, not evidence that public launch content is
approved.
