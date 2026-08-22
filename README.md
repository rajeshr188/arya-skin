# Dr. Naresh Rathod clinic website

Server-rendered Django and Wagtail website for Dr. Naresh Rathod and the two
independently named clinics where he practises: Dolphin Derma Care in Sitapura
and Arya Skin and Hair Clinic in Chaksu, Jaipur.

The project is being evolved from the Lithium starter. Milestones 1–7A provide
the CMS foundation, structured public content, the CMS-driven public shell, a
privacy-minimized appointment workflow, a medically governed article system,
factual technical/local SEO foundations, consent-gated analytics readiness, and
a private staging deployment baseline.

## Stack

- Python 3.12+ (currently verified with 3.13.3)
- Django 6.0.4
- Wagtail 7.4 LTS (currently locked to 7.4.3)
- Bootstrap 5.3, WhiteNoise, Gunicorn, psycopg, django-allauth, crispy forms
- SQLite for local development; PostgreSQL for CI, staging, and production

## Local setup

```powershell
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open the public site at <http://127.0.0.1:8000/>, Wagtail at
<http://127.0.0.1:8000/cms/>, and Django admin at
<http://127.0.0.1:8000/admin/>. Appointment enquiries are managed in Django
admin. Public patient accounts are not enabled.

To exercise the PostgreSQL development path instead:

```powershell
docker compose up --build --detach db
docker compose run --rm web python manage.py migrate
docker compose up --build web
```

Stop it with `docker compose down`; the named PostgreSQL volume is retained.

## Verification

```powershell
uv run manage.py check
uv run manage.py makemigrations --check
uv run manage.py test
```

## Configuration

The settings use local-only defaults in development and require explicit secret,
host, origin, PostgreSQL, Wagtail URL, and access-control values in staging.
Uploaded media is written to `media/` locally and must use the documented
persistent staging volume. Do not use WhiteNoise for uploads.

Appointment throttling can be adjusted with `APPOINTMENT_SUBMISSION_LIMIT` and
`APPOINTMENT_SUBMISSION_WINDOW_SECONDS`. The defaults allow five accepted
submissions per browser session per hour.

Production database, trusted-origin, storage, email, and security configuration
is tracked for the production-hardening milestone in `docs/PLAN.md` and
`docs/DEPLOYMENT.md`.

## Project documents

- `AGENTS.md`: mandatory conventions for future contributors and agents
- `docs/ARCHITECTURE.md`: ownership, model proposal, and boundaries
- `docs/PLAN.md`: milestone sequence and definition of done
- `docs/STATUS.md`: current implementation and verification state
- `docs/CONTENT_REQUIRED.md`: facts and assets still needed from the clinic
- `docs/CONTENT_STRATEGY.md`: initial medically reviewed editorial plan
- `docs/SEO_STRATEGY.md`: technical, content, and local SEO policy
- `docs/GOOGLE_BUSINESS_PROFILE.md`: location profile operating guidance
- `docs/ANALYTICS.md`: privacy-safe events and UTM conventions
- `docs/APPOINTMENTS.md`: appointment data, abuse protection, and staff workflow
- `docs/BLOG_EDITORIAL.md`: article sourcing, review, and publishing workflow
- `docs/DEPLOYMENT.md`: current and target deployment architecture
- `docs/STAGING.md`: private staging environment and release runbook
- `deploy/linode/`: secret-free Linode host and staging Compose configuration

Do not invent clinic contacts, addresses, hours, services, credentials, reviews,
or medical claims to make an unfinished page appear complete.
