# Dr. Naresh Rathod clinic website delivery plan

The website is being evolved incrementally from the Lithium Django starter. Each
milestone must leave the repository runnable and reviewable. Missing facts remain
blank in the CMS and are tracked in `CONTENT_REQUIRED.md`.

## Milestone 0 — repository audit and architecture

- [x] Inspect dependencies, settings, URLs, templates, static files, auth,
  deployment files, tests, and documentation.
- [x] Confirm the Lithium foundation and actual installed versions.
- [x] Select a supported Wagtail release for Django 6.0.
- [x] Define content ownership and application boundaries.
- [x] Record missing real-world content.

## Milestone 1 — Wagtail foundation

- [x] Add Wagtail 7.4 LTS and required applications/middleware.
- [x] Add Wagtail admin, documents, sitemap, redirects, and front-end routing.
- [x] Create the `website` app with the initial home page and site settings.
- [x] Add media configuration and a restrained shared base template.
- [x] Seed only verified brand/location facts in the initial page tree.
- [x] Keep Django admin available and public allauth routes unavailable.
- [x] Add foundation tests, create migrations, and run checks/tests.
- [x] Update `STATUS.md` with verified results.

## Milestone 2 — core public website

- [x] Milestone 2A: structured Doctor and Clinic models, draft records,
  conditional contact visibility, templates, migrations, and tests.
- [x] Milestone 2B: Treatment Index/Treatment, Contact, and Standard Page
  models and templates.
- [x] Add reusable constrained StreamField blocks, FAQs, categories, and
  doctor/clinic relationships.
- [x] Build the CMS-driven homepage, navigation, footer, treatment cards,
  CTAs, and supporting templates.
- [x] Seed empty supporting containers only; keep incomplete records unpublished.

## Milestone 3 — appointment conversion

- [x] Build the conventional Django appointment enquiry model, validation, form,
  secure staff view, minimal status lifecycle, consent, and spam controls.
- [x] Add clinic-aware call, WhatsApp, directions, appointment CTAs, and the
  mobile conversion bar.

## Milestone 4 — blog

- [x] Build blog index/article models, categories, authorship and review metadata,
  related content, image renditions, pagination, and editorial tests.

## Milestone 5 — SEO

- [x] Complete canonical/Open Graph metadata, robots, structured data,
  breadcrumbs, redirects, sitemap coverage, and local clinic SEO tests.

## Milestone 6 — analytics and Google

- [x] Add privacy-safe, consent-gated GA4/GTM configuration and conversion events.
- [x] Document Search Console, UTM, and Google Business Profile operating practice.

## Milestone 7 — production hardening

- [x] Milestone 7A: environment-driven PostgreSQL and HTTPS settings, private
  noindex staging access, non-root container/release workflow, health checks,
  structured logs, persistent staging-media guidance, and PostgreSQL CI.
- [ ] Milestone 7B: production object storage, monitoring/alerts, transactional
  email, backup/restore proof, accessibility/performance review, CSP, final HSTS,
  public content/legal approval, and production launch review.
  - [x] Add fail-closed Cloudflare R2 media configuration and dependency locking.
  - [x] Complete owner editorial approval; professional legal/privacy review is
    explicitly deferred and must not be claimed.
  - [x] Connect and publicly resolve the media custom domain and create its
    bucket-scoped application token.
  - [x] Install the media credential on the server, migrate media, and prove
    retrieval through the custom domain.
  - [x] Add a budget single-Linode production replacement configuration and a
    dry-run-first, repeat-safe filesystem-to-R2 migration command.
  - [ ] Add encrypted off-server database backup upload, retention, alerting, and
    an isolated restore test.
    - [x] Add client-side age encryption, scoped R2 upload/download, checksum
      verification, 14-day pruning, production timer definitions, and restore
      tooling.
    - [x] Upload a real backup, pass the isolated R2 restore proof, and remove the
      server recovery key after confirming its off-server copy.
    - [ ] Enable the production timer at cutover and connect timer-failure
      alerting.
  - [ ] Complete the remaining production controls and launch review.

## Definition of done for every milestone

1. Migrations are committed and `makemigrations --check` is clean.
2. `manage.py check` and the relevant tests pass.
3. Documentation describes the actual implementation.
4. No unverified healthcare or business claims are published.
5. The next milestone remains explicitly out of scope until review.
