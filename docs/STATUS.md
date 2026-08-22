# Project status

Last updated: 22 August 2026

Milestones 0 through 6, staging milestone 7A, and the budget production cutover
are complete. `https://drnareshrathod.com` is live on immutable image
`arya-skin:ed6370c`. Production uses PostgreSQL, Cloudflare R2 media, Caddy TLS,
and daily client-side encrypted off-server backups. Monitoring, transactional
email, accessibility/performance review, a tested CSP, and the later HSTS
subdomain/preload decision remain explicitly tracked future work.

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
- Added project documentation and 80 passing foundation/domain/deployment tests.
- Added fail-closed production media storage using a bucket-scoped Cloudflare R2
  configuration and public custom domain; local development and private staging
  retain filesystem media.
- Added a budget single-Linode production replacement configuration that reuses
  the existing named data volumes only after staging stops, plus a tested,
  dry-run-first and conflict-safe media migration command.
- Built and loaded immutable image `arya-skin:9ab2b82`; its R2 dry run found seven
  files, the upload copied all seven, a repeat run skipped all seven, and public
  checks returned PNG content for both an original and a Wagtail rendition.
- Added client-side `age` backup encryption, a separately scoped R2 backup client
  with upload/download integrity checks and constrained 14-day pruning, hardened
  production timer definitions, and an isolated PostgreSQL restore workflow.
- Uploaded and re-downloaded the first 1,813,112-byte encrypted backup, verified
  its database/media checksums, restored its PostgreSQL dump into an isolated
  temporary database, ran a database query, and removed that database. After the
  owner confirmed the matching off-server recovery-key copy, the Linode private
  key was deleted; only its public encryption recipient remains. The production
  timer is enabled and its first production dump passed an isolated restore.
- Published owner-approved Privacy revision 30 covering client-side encrypted
  off-server backups with the same 14-day expiry; authenticated rendering shows
  the new sentence and no copy of the replaced local-only sentence.

## Current Wagtail tree

```text
Root
└── HomePage: Dr. Naresh Rathod                     /                  [live]
    ├── DoctorPage: Dr. Naresh Rathod               /profile/          [live]
    ├── ClinicIndexPage: Clinics                    /clinics/          [live]
    │   ├── ClinicPage: Dolphin Derma Care          /clinics/sitapura/ [live]
    │   └── ClinicPage: Arya Skin and Hair Clinic   /clinics/chaksu/   [live]
    ├── TreatmentIndexPage: Treatments              /treatments/       [draft; empty]
    ├── BlogIndexPage: Articles                      /blog/             [draft; empty]
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
manage.py test                            80 tests passed (SQLite)
manage.py test                            67 tests passed (PostgreSQL 16; previous CI baseline)
manage.py collectstatic --dry-run         passed
manage.py check --deploy                  2 expected initial-HSTS warnings
clean PostgreSQL migration                248 migrations applied
production container build                passed; runs as non-root `app`
staging smoke test                         health 200; anonymous 401; auth 200
production acceptance suite                all page/media/SEO/header checks passed
production encrypted backup                uploaded; isolated DB restore passed
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

## Current production state

- The Ubuntu 24.04 LTS Linode has current security updates and kernel
  `6.8.0-138-generic`.
- Direct root/password SSH is disabled. The key-only `arya-deploy` administrator
  is verified, and UFW permits only SSH, HTTP, and HTTPS inbound.
- Docker Engine and Compose are installed from Docker's official repository with
  bounded local logs.
- Production runs immutable image `arya-skin:ed6370c` with PostgreSQL 16 and
  generated server-only secrets. The database and Gunicorn containers are
  healthy and internal-only; Caddy alone publishes HTTP/HTTPS.
- Wagtail's canonical Site origin is `https://drnareshrathod.com`. Cloudflare
  authoritative DNS proxies the apex and `www`, Caddy holds active Let's Encrypt
  certificates for both, and `www` redirects to the apex.
- Cloudflare R2 serves all seven migrated media objects through
  `media.drnareshrathod.com`. Both a portrait original and Wagtail rendition have
  returned 200 with image content.
- The expanded production acceptance suite passed every approved page, the
  appointment form, health, robots, sitemap, Wagtail admin redirect, R2 portrait,
  canonical origin, navigation, and initial security-header check. Treatments
  and Articles remain unpublished and return 404.
- One active Wagtail administrator and a separate restricted enquiry-monitor
  account for Dr. Naresh Rathod are configured. The latter can view and update
  appointment enquiries but cannot delete them or act as a superuser. Because
  transactional email is deferred, he must check the enquiry administration page
  at least once each business day.
- The production backup timer is enabled and the staging timer is disabled. The
  first 14-day-retained production database backup uploaded client-side encrypted
  to R2 and passed checksum plus isolated PostgreSQL restore/query verification.
  Every successful backup is followed by the approved 90-day closed-enquiry
  purge. The off-server private recovery key remains outside the Linode.
- Final staging backup `arya-skin-staging-20260822T145711Z`, the old immutable
  image `arya-skin:377ee54`, and the unchanged data volumes are retained for
  rollback. The staging stack is stopped because this budget topology runs only
  one stack against the shared database volumes.
- Paid Linode backups, automated monitoring, and transactional email remain
  owner-deferred. The manual daily operating checks in `PRODUCTION_LAUNCH.md`
  apply until monitoring is implemented.

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

Operate the live production site using the manual daily checks in
`PRODUCTION_LAUNCH.md`. Next future-work priorities are automated uptime/service/
disk/backup alerts, approved transactional email, accessibility/performance
review, a tested CSP, and the later HSTS subdomain/preload decision. Analytics
remains disabled until its separate account and consent decisions are supplied.
