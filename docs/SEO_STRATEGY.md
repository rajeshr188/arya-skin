# SEO strategy

## Principles

The site should earn visibility by being accurate, useful, technically sound,
and locally specific. It will not use keyword stuffing, mass-generated locality
pages, misleading claims, or fabricated authority signals.

## Technical foundation

- Wagtail's title, slug, `seo_title`, `search_description`, redirects,
  publishing controls, and sitemap facilities are active.
- One centralized layer renders factual descriptions, canonical URLs, robots,
  Open Graph, Twitter cards, article dates, and social-image renditions.
- JSON-LD includes `WebSite`, `Person`, `WebPage`/`CollectionPage`,
  `BreadcrumbList`, `MedicalClinic`, and `BlogPosting` only where the published
  page supplies the relevant visible facts.
- Clinic telephone, map, coordinates, and opening-hour data are omitted from
  structured data until their corresponding public fields are enabled/populated.
- Draft/error/operational pages are noindex; appointment and staff routes are
  excluded by `robots.txt`, while live Wagtail pages use the XML sitemap.
- Wagtail redirects preserve approved legacy URLs without seeding invented old
  paths.
- Keep public pages server-rendered, responsive, fast, and crawlable without
  client-side JavaScript.
- Production-domain/canonical, custom 404, redirect, sitemap, and structured-data
  behavior is covered by automated tests.

## Production URL configuration

Canonical URLs, JSON-LD IDs, `robots.txt`, redirects, and sitemap locations use
the default Wagtail Site record as their authority. Before launch, update
Settings → Sites in `/cms/` with the exact public hostname and HTTPS port 443.
Use one preferred hostname and redirect every alternate host at the platform or
reverse-proxy layer. Re-run tests and inspect page source after configuration.

## Local search

Create one substantial page for each verified clinic: Sitapura and Chaksu.
Each should expose consistent name, address, phone, hours, directions, access,
photography, branch services, and helpful local context. Do not create pages for
areas where Dr. Naresh Rathod does not practise.

The homepage represents the overall clinic/doctor brand in Jaipur; clinic pages
serve location intent; treatment pages serve condition intent; articles answer
educational intent. Copy should use natural language rather than repeated exact
match phrases.

## Trust and medical quality

- Show only verified credentials, registrations, affiliations, and experience.
- Show real author and medical-review states plus accurate dates.
- Cite appropriate medical sources during editorial production.
- Keep educational disclaimers visible and avoid personalized diagnosis or cure
  promises.
- Never invent reviews, ratings, outcomes, awards, or patient totals.

## Internal linking model

```text
Educational article → treatment/condition → doctor → real clinic → contact action
```

Relationships should be modeled so templates can render relevant links without
depending entirely on links inserted into rich text. Only live related pages may
appear publicly.

## Launch checks

- Confirm every published page has a distinct SEO title and useful description.
- Validate JSON-LD against the rendered production page and visible facts.
- Confirm sitemap URLs use the preferred HTTPS hostname and drafts are absent.
- Confirm `robots.txt` names the same production sitemap.
- Enter only real legacy redirects and test their final destination/status.
- Submit the sitemap to Search Console after domain ownership is confirmed.

## Measurement

Use Search Console for indexing/query diagnostics and privacy-safe analytics for
conversion actions. Never send patient concern or message text. See
`ANALYTICS.md` and `GOOGLE_BUSINESS_PROFILE.md`.
