# Architecture

## Audited foundation

This repository is the Lithium starter at commit `a6a0718`. At the audit it
used Python 3.12+, Django 6.0.4, Bootstrap 5.3.3, django-allauth,
django-crispy-forms, WhiteNoise, Gunicorn, psycopg, SQLite for local development,
and optional Docker/PostgreSQL files. It had a custom user model, demo template
views, no content models, and no meaningful tests.

Wagtail 7.4 LTS is selected because its official compatibility table supports
Django 6.0 and Python 3.12. Django is not downgraded.

## Responsibilities

### Django platform layer

- settings, security, URL composition, storage, static/media configuration;
- the existing `accounts.CustomUser` and Django admin;
- appointment enquiries, consent, validation, spam handling, and staff status;
- future privacy-safe analytics event emission and external integrations.

django-allauth remains installed because removing it offers little Milestone 1
value and could destabilize the starter. Its public URLs are not mounted because
patient accounts and public signup/login are not product requirements. Wagtail
uses Django's normal staff authentication.

### Wagtail editorial layer

- page tree, publishing workflow, redirects, sitemap, images, and documents;
- home, doctor, clinic, treatment, blog, contact, and standard/legal pages;
- reusable site identity/contact/social/analytics settings;
- editorial relationships between articles, treatments, doctor, and clinics.

The Wagtail admin is mounted at `/cms/`; Django admin remains at `/admin/`.
Front-end Wagtail routing is mounted last so application URLs retain priority.

## Application boundaries

- `accounts`: existing custom user model and Django admin integration.
- `website`: cross-site foundations, homepage, standard pages, constrained
  shared blocks, site settings, and shared template tags.
- `doctors`: structured doctor profile, qualifications, registrations,
  specialties, languages, memberships, and portrait. Implemented in Milestone 2A.
- `clinics`: physical-location content and location-specific contact facts.
  Implemented in Milestone 2A with opening hours, services, images, local data,
  and explicit phone/WhatsApp publication switches.
- `treatments`: structured condition/treatment landing pages, categories, FAQs,
  doctor ownership, clinic availability, and homepage featuring. Implemented in
  Milestone 2B.
- `blog`: editorial articles, reusable author/reviewer records, categories,
  factual sources, review dates, related treatments/articles, pagination, and a
  publication-readiness guard. Implemented in Milestone 4.
- `appointments`: conventional Django appointment-enquiry form and operational
  record, consent versioning, first-party abuse controls, clinic snapshot,
  minimal status lifecycle, and secure Django-admin workflow. Implemented in
  Milestone 3.

Apps will be introduced only when their milestone begins; empty placeholder apps
are intentionally avoided.

## Implemented page tree

```text
Wagtail root
└── HomePage: Dr. Naresh Rathod      /
    ├── DoctorPage [draft]            /dr-naresh-rathod/
    ├── ClinicIndexPage [draft]       /clinics/
    │   ├── Dolphin Derma Care [draft]
    │   │                              /clinics/sitapura/
    │   └── Arya Skin and Hair Clinic [draft]
    │                                  /clinics/chaksu/
    ├── TreatmentIndexPage [draft]   /treatments/
    │   └── TreatmentPage            /treatments/<slug>/ (none seeded)
    ├── BlogIndexPage [draft]        /blog/
    │   └── BlogPage                 /blog/<slug>/ (none seeded)
    ├── ContactPage [draft]          /contact/
    ├── StandardPage [draft]         /privacy/
    └── StandardPage [draft]         /medical-disclaimer/
```

The root `HomePage` is live. All incomplete supporting pages are drafts so their
routes, navigation entries, homepage sections, and footer links remain hidden.
No treatment or blog content records are seeded. Dr. Naresh Rathod is the
umbrella professional identity; clinic names remain independent.

## Structured content

- `SiteSettings` (`BaseSiteSetting`): professional/site display names, default contact
  and social links, default social image, analytics IDs, and reusable disclaimer.
- `DoctorPage`: biography, structured qualifications/registrations/memberships,
  specialties, languages, dated experience claims, care philosophy, and a
  Wagtail portrait. Implemented.
- `ClinicPage`: locality, address, phones, WhatsApp, schedules, map/GBP links,
  coordinates/place ID, access information, gallery, services, FAQs, and related
  treatments. The implemented foundation covers all except clinic-specific FAQs;
  treatment availability is owned by `TreatmentPage`. Clinic contact data is
  never copied into global settings.
- `TreatmentPage`: structured overview/symptoms/causes/diagnosis/consultation,
  approaches, and expectations fields; constrained body blocks; page-specific
  FAQs; category, doctor, and clinic relationships; and controlled homepage
  featuring. Implemented in Milestone 2B; no real treatment content is seeded.
- `BlogPage`: excerpt, constrained body, accessible featured image,
  author/reviewer, automatic publication date, completed/next review dates,
  factual sources, categories, and live-filtered related treatments/articles.
  Incomplete pages may remain drafts, while publication requires an author,
  body, source, reviewed status, reviewer, and valid review date.
- snippets: categories and reusable people/FAQ records only where reuse is real;
  page-specific FAQs remain attached to their page.

Wagtail's built-in `title`, `slug`, `seo_title`, `search_description`, revisions,
workflow, image renditions, redirects, and sitemap support are reused instead of
duplicated.

## StreamField policy

Semantic facts use typed model fields and relations. StreamField is limited to
editorial narrative made from constrained blocks such as rich text, heading,
image, image/text, quote, FAQ, CTA, doctor advice, and warning/information. Block
options and rich-text features remain deliberately narrow; editors do not get an
unrestricted page builder.

## Rendering and media

Pages are server-rendered with Django templates and Bootstrap. Shared metadata,
navigation, footer, CTA, cards, breadcrumbs, FAQ, and JSON-LD live in reusable
components. Wagtail renditions provide responsive images; originals are never
used as page-sized assets by default. WhiteNoise serves static assets only.
Local uploads use `MEDIA_ROOT`; production will use an object-storage-compatible
default storage without changing content models.

## Safety and SEO constraints

- Unknown addresses, contacts, hours, credentials, services, reviews, ratings,
  and outcomes remain blank and unpublished.
- Medical content is educational, avoids individualized diagnosis and cure
  guarantees, and shows a reusable disclaimer.
- Page metadata uses visible factual content. Structured data cannot introduce
  facts absent from the page.
- Location pages represent real clinics only; no doorway-page generation.
- Analytics records action names and page context, never concern/message text.
