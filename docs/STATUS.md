# Project status

Last updated: 22 August 2026

Milestones 0 through 6 and the staging baseline in milestone 7A are complete.
Milestone 7B is in progress. Production Cloudflare R2 media support is implemented
and tested locally. The media custom domain and bucket-scoped token are created,
but server credential installation, media migration, backups, and the production
release itself are not yet configured.

## Implemented

- Audited and retained the useful Lithium Django foundation.
- Kept Django 6.0.4 and locked Wagtail 7.4.3 from the 7.4 LTS line.
- Integrated Wagtail admin, pages, settings, images, documents, search, redirects,
  XML sitemap, publishing, and local media configuration.
- Reframed the umbrella public identity around Dr. Naresh Rathod while preserving
  the two independent clinic names.
- Added a structured `DoctorPage` with qualifications, registration, specialties,
  languages, memberships, dated experience, biography, philosophy, affiliations,
  and portrait fields.
- Added `ClinicIndexPage` and structured `ClinicPage` models with branch address,
  contact, publication consent switches, opening hours, availability, services,
  gallery, Maps/GBP, coordinates, landmarks, parking, and accessibility fields.
- Added reusable breadcrumb, clinic-card, and clinic-contact components plus
  doctor/clinic templates.
- Added a constrained shared StreamField block library for headings, rich text,
  images, image/text layouts, quotes, FAQs, CTAs, doctor advice, and notices.
- Added `TreatmentCategory`, `TreatmentIndexPage`, and structured `TreatmentPage`
  models with FAQs, doctor/clinic relationships, medical disclaimer rendering,
  and controlled homepage featuring.
- Added Contact and Standard Page models and templates plus CMS-driven homepage,
  navigation, footer, cards, and conditional CTAs.
- Seeded supplied doctor details and both clinic records as drafts. The supplied
  phone/WhatsApp number is stored but not publicly exposed.
- Seeded empty Treatments, Contact, Privacy, and Medical disclaimer containers as
  drafts. No treatment offering, medical content, or legal policy was invented.
- Added a privacy-minimized appointment form that collects only clinic, name,
  phone, optional email, preferred date/time, and explicit contact consent.
- Added signed form tokens, CSRF protection, a honeypot, session throttling,
  no-cache responses, sensitive POST filtering, clinic tamper protection, and
  draft-clinic exclusion.
- Added a Django-admin workflow with new, contacted, scheduled, closed, and spam
  states; clinic snapshots; consent versioning; and constrained administrative
  notes. No patient account, diagnosis, or detailed medical message is stored.
- Added clinic-aware appointment, approved phone/WhatsApp/directions actions and
  a mobile conversion bar. Unapproved contact actions remain hidden.
- Added Blog Index and Article pages, reusable categories and author/reviewer
  records, factual sources, constrained article bodies, accessible featured
  images, review dates, and related treatment/article relationships.
- Added a publication-readiness guard: incomplete articles may remain drafts but
  cannot go live without an author, body, source, reviewed status, reviewer, and
  valid completed-review date.
- Added public category filtering, pagination, responsive Wagtail image
  renditions, publication/review attribution, sources, related content, medical
  disclaimer, and latest-article homepage integration.
- Seeded only an empty draft Articles index. No article, category, author,
  reviewer, medical copy, source, or review claim was invented.
- Added centralized page-specific descriptions, canonical URLs, robots metadata,
  Open Graph/Twitter cards, social-image renditions, and article dates.
- Added factual JSON-LD for the website, doctor, breadcrumbs, page collections,
  clinics, and reviewed articles. Optional clinic telephone, map, geo, and hours
  appear only when their public structured fields are populated.
- Added `robots.txt`, appointment noindex headers, draft/error noindex behavior,
  production-host canonical tests, redirect tests, and expanded sitemap tests.
  No legacy redirect or structured-data fact was invented.
- Added an explicit Wagtail analytics enable switch, mutually exclusive GA4/GTM
  ID validation, and optional Search Console verification metadata.
- Added basic consent mode that makes no Google analytics request before opt-in
  and remains unavailable until the Privacy page is published. Analytics is
  disabled by default because no approved account or privacy notice exists.
- Added a fixed seven-event conversion/view contract using only page type and
  stable clinic/treatment slugs. Accepted appointment events are server-gated,
  one-time, and contain no patient-entered values.
- Added consent controls, analytics-choice reopening, clinic/mobile/home/treatment
  event annotations, and documented GA4, GTM, Search Console, UTM, and Google
  Business Profile operating safeguards.
- Added explicit development, staging, and production settings profiles with
  strict environment validation, PostgreSQL URL parsing, HTTPS/proxy security,
  secret/host/origin validation, and deployment-safe cookie defaults.
- Added forced private staging access, noindex headers, a database-readiness
  endpoint, privacy-safe JSON logs, and a documented staging release checklist.
- Added a non-root multi-stage container, Gunicorn configuration, release script,
  local PostgreSQL Compose workflow, and persistent-media guidance.
- Added PostgreSQL-backed CI for migration, test, static-file, and production
  deployment checks. A clean PostgreSQL database now applies the entire migration
  graph in dependency order.
- Retained Django admin and installed allauth; public allauth routes remain
  intentionally unavailable.
- Added project documentation and 76 passing foundation/domain/deployment tests.
- Added fail-closed production media storage using a bucket-scoped Cloudflare R2
  configuration and public custom domain; local development and private staging
  retain filesystem media.
- Added a budget single-Linode production replacement configuration that reuses
  the existing named data volumes only after staging stops, plus a tested,
  dry-run-first and conflict-safe media migration command.

## Current Wagtail tree

```text
Root
└── HomePage: Dr. Naresh Rathod                     /                  [live]
    ├── DoctorPage: Dr. Naresh Rathod               /profile/          [live]
    ├── ClinicIndexPage: Clinics                    /clinics/          [live; draft changes]
    │   ├── ClinicPage: Dolphin Derma Care          /clinics/sitapura/ [live]
    │   └── ClinicPage: Arya Skin and Hair Clinic   /clinics/chaksu/   [live]
    ├── TreatmentIndexPage: Treatments              /treatments/       [live; empty]
    ├── BlogIndexPage: Articles                      /blog/             [live; empty]
    ├── ContactPage: Contact                        /contact/          [live]
    ├── StandardPage: Privacy                       /privacy/          [live]
    └── StandardPage: Medical disclaimer            /medical-disclaimer/ [live]
```

The owner completed editorial review of the current public content. Professional
legal/privacy review remains explicitly deferred and is not claimed.

## Architecture decisions

- Dr. Naresh Rathod is the umbrella professional identity.
- Dolphin Derma Care belongs to Sitapura; Arya Skin and Hair Clinic belongs to
  Chaksu. Neither clinic is relabelled as the other.
- Contact values and consent are separate fields. A phone or WhatsApp action is
  rendered only when its explicit public switch is enabled.
- Experience is displayed only when both a year count and an “as of” date exist.
- Missing clinic facts remain blank; incomplete seeded pages remain drafts.
- Django owns appointment operations; Wagtail owns public editorial data.
- Appointment routes require at least one published, unrestricted clinic. A
  submitted request is explicitly not presented as a confirmed appointment.
- Article publication is technically blocked until the required sourcing,
  authorship, and completed medical-review metadata are present.
- The Wagtail Site hostname/port is the authority for canonical, sitemap,
  redirects, robots, and structured-data URLs; production must use its preferred
  HTTPS domain.
- Analytics uses one approved provider and basic opt-in consent. A live Privacy
  page is a technical prerequisite; GA4 enhanced outbound/form measurement and
  any GTM form/DOM variables remain prohibited.
- SQLite remains a convenience for local development only. CI, staging, and
  production use PostgreSQL; staging additionally requires HTTPS, Basic access
  control, forced noindex, a persistent media volume, and secret-manager values.
- Database migration and static collection are release operations, separate from
  web-process startup. The application container runs as an unprivileged user.

## Verification

Verified against Python 3.13.3, Django 6.0.4, and Wagtail 7.4.3:

```text
manage.py migrate                         no pending migrations
manage.py check                           0 issues
manage.py makemigrations --check          no changes detected
manage.py test                            76 tests passed (SQLite)
manage.py test                            67 tests passed (PostgreSQL 16; previous CI baseline)
manage.py collectstatic --dry-run         passed
manage.py check --deploy                  0 issues (production profile)
clean PostgreSQL migration                248 migrations applied
production container build                passed; runs as non-root `app`
staging smoke test                         health 200; anonymous 401; auth 200
direct homepage request                   HTTP 200
all nine draft routes                     HTTP 404
git diff --check                          passed
```

Tests cover clean-database migrations, page-tree structure, draft publishing
visibility, structured doctor records, clinic identity/routing, contact consent,
constrained blocks, treatment relationships/rendering, supporting pages,
homepage content gating, appointment data minimization, consent, validation,
CSRF, signed tokens, spam controls, throttling, clinic integrity, staff access,
conversion actions, Wagtail admin, allauth exposure, and sitemap.
Blog tests additionally cover publication blocking, sources, attribution, review
dates, draft-safe relationships, category filtering, pagination, homepage
integration, alt text, and generated image renditions.
SEO tests cover production HTTPS origins, canonical/social/article metadata,
robots exclusions, factual doctor/clinic/article JSON-LD, private-field omission,
breadcrumbs, redirects, draft/noindex behavior, and sitemap coverage.
Analytics tests cover disabled defaults, provider validation, live-privacy
gating, consent controls, safe clinic/treatment actions, Search Console metadata,
one-time accepted submissions, and the client-side event allowlist.
Deployment tests cover strict environment parsing, PostgreSQL configuration,
database readiness responses, staging access/noindex behavior, and redacted JSON
request logs.

## Current staging state

- The Ubuntu 24.04 LTS Linode has current security updates and kernel
  `6.8.0-138-generic`.
- Direct root/password SSH is disabled. The key-only `arya-deploy` administrator
  is verified, and UFW permits only SSH, HTTP, and HTTPS inbound.
- Docker Engine and Compose are installed from Docker's official repository with
  bounded local logs.
- The immutable `377ee54` application image, PostgreSQL 16, generated server-only
  secrets, and persistent database/media volumes are provisioned.
- All migrations and the staging release checks completed. The internal database
  and Gunicorn containers are healthy with no restart, and neither is published
  on a host port.
- Wagtail's canonical Site origin is `https://staging.drnareshrathod.com`.
- Cloudflare authoritative DNS resolves the proxied staging hostname to the
  Linode origin. Caddy has an active Let's Encrypt certificate and redirects HTTP
  to HTTPS.
- External and credentialed acceptance checks pass: anonymous pages remain
  access-controlled and noindexed, the health endpoint is available, and the
  authenticated site and Wagtail login route respond successfully. Uploaded
  media and Wagtail renditions are served from the persistent staging volume,
  remain protected by reviewer authentication, and return the expected image
  content type.
- One active Wagtail administrator and a separate restricted enquiry-monitor
  account for Dr. Naresh Rathod are configured. The latter can view and update
  appointment enquiries but cannot delete them or act as a superuser. A daily,
  access-restricted PostgreSQL and media backup timer is enabled with 14-day
  local retention. Each
  successful backup is followed by the 90-day closed-enquiry purge; the latest
  isolated database/media restore and post-release maintenance tests passed.
- Owner editorial review is complete and the approved public pages are live on
  staging. The Clinic Index has a newer unpublished revision that must be resolved
  during the production release audit. Paid Linode backups remain deferred; two
  R2 buckets have been created, but encrypted off-server backup automation is not
  yet implemented.

## Missing real-world content

Both clinic pages contain owner-approved call/WhatsApp publication consent,
addresses, doctor-availability schedules, and the shared service list. The
uploaded doctor portrait and its alternative text are also approved. Maps links
and access details remain optional but must not be inferred. Precise
qualification/experience wording may remain absent. Dr.
Naresh Rathod is the designated enquiry monitor; consent, a one-business-day
response target, the call/WhatsApp fallback for an unanswered request, and
90-day post-closure retention are approved. The Privacy and Medical disclaimer
pages contain owner-approved working text. Professional
legal/privacy review remains recommended but was explicitly deferred by the
owner for the budget launch; the drafts are not legally verified. Blog authors,
medical reviewers, source standards, review intervals, and every article also
require approval. See `CONTENT_REQUIRED.md`.

## Next milestone

Milestone 7B should next install the R2 media credential on the server, migrate
and verify media, add encrypted off-server database backups with a restore proof,
and then complete monitoring, transactional email, accessibility/performance,
CSP/HSTS, and the production launch review. Analytics remains disabled until its
separate account and consent decisions are supplied.
