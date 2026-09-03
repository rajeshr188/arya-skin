# Production launch record

Launch authorization date: 22 August 2026

## Owner-authorized budget deferrals

The owner authorized the single-Linode production cutover and initially chose to
postpone automated service/backup failure monitoring and transactional email
notifications. On 3 September 2026, the owner authorized staff-only appointment
email to Dr. Naresh Rathod and completed sending-domain verification. Monitoring
remains deferred; email completed production delivery acceptance on 3 September
2026.

Until monitoring is added, an operator must manually check the public homepage,
`/healthz/`, the production backup timer result, available disk space, and the
latest encrypted R2 backup each day. A service outage, low disk condition, or
failed/missing backup may otherwise remain unnoticed.

Transactional email now sends Dr. Naresh Rathod a privacy-minimized alert for a
new appointment enquiry. SMS, WhatsApp API, calendar, CRM, and patient
acknowledgement email remain disabled. Because automated worker-failure alerts
are deferred, Dr. Naresh must still sign in to the restricted enquiry
administration page at least once each business day. The published fallback tells
requesters to call or WhatsApp the selected clinic after one business day.

Use these manual server checks each day until automated monitoring is added:

```sh
cd /srv/arya-skin/production
./check_production.sh
systemctl list-timers arya-skin-production-backup.timer --no-pager
sudo systemctl show arya-skin-production-backup.service \
  --property=Result --property=ExecMainStatus --no-pager
sudo journalctl --unit arya-skin-production-backup.service -n 30 --no-pager
df -h /
```

The latest backup service result must be successful and its journal must contain
an `encrypted_backup_uploaded` line. Dr. Naresh should check new enquiries at
`https://drnareshrathod.com/admin/appointments/appointmentenquiry/`.

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
- [x] Final staging backup and restore/configuration preflight passed.
- [x] Production stack started only after staging stopped cleanly.
- [x] Production canonical Site, HTTPS, health, admin, media, forms, redirects,
  robots/sitemap, and security headers verified.
- [x] Production backup timer enabled and a production backup completed.
- [x] Rollback image, database/media volumes, and final staging backup retained.

## Launch outcome

Production launched at `https://drnareshrathod.com` on 22 August 2026 using
immutable image `arya-skin:9ec9026`. PostgreSQL and the web container are
healthy, and only Caddy publishes host ports. Caddy obtained Let's Encrypt
certificates for the apex and `www`; Cloudflare briefly returned 525 during
certificate issuance and then passed all acceptance checks.

The acceptance suite returned 200 for the approved public pages, appointment
form, health endpoint, robots, sitemap, and R2 portrait; 302 for Wagtail admin;
and 404 for the intentionally unpublished Treatments and Articles indexes. It
also verified the apex canonical, `www` redirect, absence of production noindex,
navigation exclusion of the empty indexes, and the initial HSTS, nosniff,
frame-denial, and referrer-policy headers.

The first encrypted production backup
`arya-skin-production-20260822T150130Z.backup.tar.age` uploaded successfully. Its
local PostgreSQL dump passed checksum verification, an isolated restore, and a
database query. The production timer is active; the staging timer is disabled.
The final staging backup from `20260822T145711Z` and image `arya-skin:377ee54`
remain available for rollback.

After launch, a returning browser reported a Workbox `sw.js` failure while
fetching an R2 rendition. The exact rendition remained healthy and returned its
complete PNG response. The application had never registered a service worker,
so the failure was traced to a registration retained from a site previously
hosted on the apex origin. Production now serves a no-store retirement worker at
`/sw.js`; the first-party script asks only existing same-origin registrations to
update. The retirement worker clears service-worker caches, unregisters itself,
and reloads controlled tabs without clearing cookies or local storage. The
tested fix was deployed as immutable image `arya-skin:ed6370c`; the full
production acceptance suite passed afterward.

On 23 August 2026, new Wagtail image uploads returned 500 while existing public
R2 images continued to render. Logs showed that Gunicorn could not resolve the
R2 API endpoint: it was attached only to the intentionally internal database
network. The web service now also joins Docker's non-published `edge` network for
outbound R2 access, while PostgreSQL remains on the internal `backend` network
only and Gunicorn still publishes no host port. A unique R2 diagnostic object
passed write, read, delete, and post-delete verification. The default 500
template was also made standalone because its former SEO tags masked the
original exception when Django rendered it without request context.
The persistent fix was deployed as immutable image `arya-skin:95c8b03`. A
post-deployment audit found one CMS image record, its original present in R2,
and no orphan records from the failed upload attempts.

On 23 August 2026, the guarded before-and-after gallery was deployed as
immutable image `arya-skin:c53bca7`. Its migration created an empty
`/before-after/` draft with no patient images. Production acceptance passed,
the public route returned 404, and no gallery navigation link was rendered.
Publication requires at least one distinct image pair, accurate descriptions,
documented publication consent, and a confirmed fair-presentation review. The
post-migration encrypted backup
`arya-skin-production-20260823T055556Z.backup.tar.age` uploaded successfully.

On 24 August 2026, the GA4 privacy-preparation release was deployed as immutable
image `arya-skin:a79cd6a`. The published Privacy notice was updated through
revision 35, and measurement ID `G-DKBKVGX7NK` was stored with analytics still
disabled. Public verification found no measurement ID, analytics configuration,
consent banner, or Google tag in the homepage HTML. The acceptance script was
also corrected to follow the current CMS-managed portrait instead of a deleted
historic filename. All acceptance checks passed, and encrypted backup
`arya-skin-production-20260824T050554Z.backup.tar.age` uploaded successfully.

Later on 24 August 2026, the owner confirmed that GA4 outbound-click and form
interaction measurement, Google Signals, user-provided/advertising features,
and enhanced conversions were disabled, and that two-month retention with reset
off was selected. Basic Consent Mode was then enabled for `G-DKBKVGX7NK`.
Production verification found the banner, accept/decline/manage controls, and
measurement configuration, while the server-rendered HTML contained no Google
tag before consent. The full acceptance suite passed, and encrypted backup
`arya-skin-production-20260824T051503Z.backup.tar.age` uploaded successfully.

On 3 September 2026, the privacy-safe appointment notification implementation
was deployed as immutable image `arya-skin:686e4e9`. Migration
`appointments.0003_appointmentnotificationdelivery` added the durable delivery
outbox. Privacy revision 41 disclosed the transactional provider's limited data
handling. The full production acceptance suite passed, and the notification
command confirmed that sending remained disabled during this first phase.

The owner then installed the sending-only Resend key in a mode-600 server secret.
A patient-data-free transport test reached the designated inbox. The one-minute
systemd timer was enabled, and a clearly synthetic request submitted through the
live public form was automatically delivered with `attempted=1`, `sent=1`, and
`retrying=0`. The recipient confirmed inbox receipt. The guarded cleanup removed
the one synthetic enquiry and its delivery record, then verified that none
remained. Fresh encrypted backup
`arya-skin-production-20260903T092947Z.backup.tar.age` uploaded successfully
after activation.

Later on 3 September 2026, five source-checked patient-information pages were
deployed as unpublished Wagtail drafts in immutable image `arya-skin:9b43e1f`:
acne assessment and treatment, skin-allergy assessment and testing, chemical
peel consultation, laser treatment consultation, and general dermatology
consultation. Each is linked to Dr. Naresh Rathod and both clinics but remains
excluded from menus, routing, and search visibility. The seeder's repeat run was
unchanged, the inventory reported five total and zero live treatments, and every
draft URL returned 404 externally. Encrypted backup
`arya-skin-production-20260903T095431Z.backup.tar.age` completed after creation.
Publication requires Dr. Naresh Rathod's explicit page-by-page approval.

## Future work

- Add externally delivered uptime, service, disk, and backup-failure alerts.
- Revisit a tested Content Security Policy after inventories of required
  first-party and third-party script/style/image sources.
- Reassess HSTS duration, subdomain coverage, and preload only after the initial
  production TLS period is stable.
