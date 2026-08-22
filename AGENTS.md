# Dr. Naresh Rathod clinic website repository guidance

## Product boundary

This is a local medical marketing and patient-education website, not an EHR,
telemedicine product, payment platform, CRM, or patient portal. Optimize the
journey: discover, trust, educate, contact, visit clinic.

## Architecture

- Django is the platform/operational layer.
- Wagtail is the editorial layer for public content, images, settings, revisions,
  redirects, sitemap, and publication workflow.
- Appointment enquiries remain a conventional Django app and must collect only
  the minimum contact information required.
- Templates are server-rendered with Bootstrap and progressive enhancement.
- Static assets and uploaded media are separate. WhiteNoise is for static files,
  not permanent production media storage.

See `docs/ARCHITECTURE.md`, `docs/PLAN.md`, and `docs/STATUS.md` before changing
scope or models.

## Commands

```powershell
uv sync
uv run manage.py migrate
uv run manage.py check
uv run manage.py makemigrations --check
uv run manage.py test
uv run manage.py runserver
```

Wagtail staff administration is at `/cms/`; Django administration is at
`/admin/`. Public django-allauth URLs are intentionally not mounted.

## Content ownership

- The umbrella professional identity and global contact/social/analytics values
  belong in Wagtail site settings.
- The two clinic names are independent: Dolphin Derma Care in Sitapura and Arya
  Skin and Hair Clinic in Chaksu. Never relabel one as the other.
- Doctor facts belong on the Doctor page/domain model.
- Branch address, phone, WhatsApp, hours, maps/GBP, access, photographs, and
  services belong to the relevant Clinic page.
- Narrative may use constrained StreamField blocks; semantic facts must use
  typed fields and relations.
- Prefer Wagtail's built-in SEO fields, images/renditions, redirects, and sitemap.

## Non-negotiable content rules

Never invent or imply unverified qualifications, registration numbers, awards,
experience, affiliations, addresses, phone numbers, hours, services, testimonials,
ratings, patient counts, success rates, treatment outcomes, or Google URLs.
Leave unknown CMS fields blank and add the need to `docs/CONTENT_REQUIRED.md`.

Medical content is general education, not diagnosis. Never promise a cure,
guaranteed outcome, or “permanent solution.” Do not claim clinician review until
it occurred. Structured data must reflect factual visible content.

## SEO, analytics, and privacy

- Create pages only for real clinics and meaningful content; never mass-produce
  locality doorway pages or keyword-stuff copy.
- Preserve clean slugs and semantic heading order. Render canonical/social
  metadata centrally.
- Never send a patient's concern, message, or other sensitive information to
  analytics, URLs, query strings, or third parties.
- Conversion events contain action and page/clinic identifiers only.

## Development conventions

- Work milestone by milestone; do not implement later milestones opportunistically.
- Commit migrations with model changes and test public/published behavior.
- Keep settings environment-ready and secrets out of version control.
- Preserve the existing custom user model. Avoid removing allauth until a
  dedicated, tested migration decision justifies it.
- Do not add SPA frameworks, APIs, queues, caches, or search infrastructure
  without a demonstrated requirement.
- Keep documentation concise and synchronized with actual behavior.
