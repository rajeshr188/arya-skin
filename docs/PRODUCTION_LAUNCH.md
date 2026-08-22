# Production launch record

Launch authorization date: 22 August 2026

## Owner-authorized budget deferrals

The owner authorized the single-Linode production cutover and explicitly chose
to postpone automated service/backup failure monitoring and transactional email
notifications. These are recorded as future work, not completed controls.

Until monitoring is added, an operator must manually check the public homepage,
`/healthz/`, the production backup timer result, available disk space, and the
latest encrypted R2 backup each day. A service outage, low disk condition, or
failed/missing backup may otherwise remain unnoticed.

Until transactional email is added, no email, SMS, WhatsApp API, calendar, or
CRM notification is sent for a new appointment enquiry. Dr. Naresh Rathod must
sign in to the restricted enquiry administration page at least once each
business day to meet the approved response target. The published fallback tells
requesters to call or WhatsApp the selected clinic after one business day.

## Cutover gates

- [x] Owner editorial review completed; professional legal/privacy review was
  explicitly deferred and is not claimed.
- [x] Empty Treatments and Articles indexes unpublished with their drafts kept.
- [x] Production R2 media migration and public original/rendition checks passed.
- [x] Encrypted R2 backup download, integrity, decryption, and isolated restore
  proof passed; the private recovery key is retained only off-server.
- [x] Production Compose configuration validates and the immutable application
  image runs as an unprivileged user.
- [x] Monitoring and transactional email explicitly deferred with manual interim
  procedures documented above.
- [ ] Final staging backup and restore/configuration preflight passed.
- [ ] Production stack started only after staging stopped cleanly.
- [ ] Production canonical Site, HTTPS, health, admin, media, forms, redirects,
  robots/sitemap, and security headers verified.
- [ ] Production backup timer enabled and a production backup completed.
- [ ] Rollback image, database/media volumes, and final staging backup retained.

## Future work

- Add externally delivered uptime, service, disk, and backup-failure alerts.
- Add approved transactional email with privacy-safe content and delivery tests.
- Revisit a tested Content Security Policy after inventories of required
  first-party and third-party script/style/image sources.
- Reassess HSTS duration, subdomain coverage, and preload only after the initial
  production TLS period is stable.

