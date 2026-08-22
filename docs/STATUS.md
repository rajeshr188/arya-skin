# Project status

Last updated: 22 August 2026

Milestones 0 through 6 are complete. Production hardening is not implemented.

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
- Retained Django admin and installed allauth; public allauth routes remain
  intentionally unavailable.
- Added project documentation and 59 passing foundation/domain tests.

## Current Wagtail tree

```text
Root
└── HomePage: Dr. Naresh Rathod                     /                  [live]
    ├── DoctorPage: Dr. Naresh Rathod               /dr-naresh-rathod/ [draft]
    ├── ClinicIndexPage: Clinics                    /clinics/          [draft]
    │   ├── ClinicPage: Dolphin Derma Care          /clinics/sitapura/ [draft]
    │   └── ClinicPage: Arya Skin and Hair Clinic   /clinics/chaksu/   [draft]
    ├── TreatmentIndexPage: Treatments              /treatments/       [draft]
    ├── BlogIndexPage: Articles                      /blog/             [draft]
    ├── ContactPage: Contact                        /contact/          [draft]
    ├── StandardPage: Privacy                       /privacy/          [draft]
    └── StandardPage: Medical disclaimer            /medical-disclaimer/ [draft]
```

Draft routes correctly return 404 publicly. Staff can complete and preview them
in Wagtail before publication.

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

## Verification

Verified against Python 3.13.3, Django 6.0.4, and Wagtail 7.4.3:

```text
manage.py migrate                         no pending migrations
manage.py check                           0 issues
manage.py makemigrations --check          no changes detected
manage.py test                            59 tests passed
manage.py collectstatic --dry-run         passed
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

## Missing real-world content

Before publishing the draft pages, confirm phone/WhatsApp publication consent,
clinic hours and doctor availability, the complete Chaksu address, final Sitapura
address formatting, Maps links, and the precise qualification/experience display
wording. Appointment consent wording, staff access, response practice, and data
retention also require operational approval. Blog authors, medical reviewers,
source standards, review intervals, and every article require approval. See
`CONTENT_REQUIRED.md`.

## Next milestone

Milestone 7 should complete PostgreSQL/environment configuration, durable media
storage, deployment security, accessibility, performance, and production error
handling. Analytics must remain disabled until the outstanding account, privacy,
and consent approvals are supplied.
