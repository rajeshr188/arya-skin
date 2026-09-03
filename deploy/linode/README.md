# Linode private staging

This directory contains the version-controlled, secret-free infrastructure for
`staging.drnareshrathod.com` on the single Linode staging host.

- Caddy is the only service publishing host ports (`80` and `443`).
- PostgreSQL and Gunicorn are reachable only on the internal Docker network.
- In production, Gunicorn also joins the non-published `edge` network so it can
  reach the Cloudflare R2 API. PostgreSQL remains on `backend` only; the web
  service still publishes no host port.
- Database, media, and Caddy certificate data use persistent named volumes.
- The server `.env` is generated with `bootstrap-env.sh`, mode `600`, and must
  never be copied into Git or command output.
- The one-CPU/one-GB host uses one Gunicorn worker and two threads.

## Deployment order

1. Secure and update the Ubuntu host; install Docker Engine and Compose.
2. Load the immutable application image off-host.
3. Copy this directory to `/srv/arya-skin/staging`.
4. Generate `.env` once and validate the rendered Compose configuration.
5. Start PostgreSQL, run `scripts/release.sh` once, then start the web service.
6. Point the Cloudflare DNS `staging` record to the Linode IPv4 address.
7. Start Caddy only after public DNS resolves to the Linode.
8. Run `./check_staging.sh` on the host, then complete the editorial acceptance
   checks in `docs/STAGING.md`.

For a contact-value-redacted inventory of page publication and content
completeness, run:

```sh
docker compose --file compose.staging.yml exec -T web \
  python manage.py shell < editorial_inventory.py
```

After explicit owner approval, an empty Treatments and Articles index can be
removed from public navigation without deleting its CMS draft. The guarded
operation refuses to run if either index has unpublished edits or any child
content:

```sh
docker compose --file compose.staging.yml exec -T web \
  python manage.py shell < unpublish_empty_content_indexes.py
```

## Local staging backups

Install the daily database and media backup timer after the stack is healthy:

```sh
chmod 750 backup_staging.sh test_restore.sh check_staging.sh \
  purge_closed_enquiries.sh
sudo install -d -m 0700 -o arya-deploy -g arya-deploy /srv/arya-skin/backups
sudo install -m 0644 arya-skin-staging-backup.service \
  arya-skin-staging-backup.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now arya-skin-staging-backup.timer
./backup_staging.sh
./test_restore.sh
```

The timer takes a PostgreSQL custom-format dump and a compressed media archive
daily, writes checksums, and retains 14 days by default. `test_restore.sh`
restores the newest dump into an isolated temporary database and extracts its
media archive without touching the live database or media volume. Review timer
and service history with `systemctl list-timers` and `journalctl`.

After each successful backup, the same service runs the approved appointment
retention command. It deletes only enquiries that have remained in the `Closed`
state for more than 90 days. The pre-deletion backup then ages out under the
14-day backup policy.

These access-restricted local copies help with application-level recovery but do
not survive loss of the Linode. The installed service therefore follows each
successful local backup with client-side `age` encryption and upload to the
private backup bucket. Treat off-server coverage as complete only after the
recovery key has been retained away from the server and `test_r2_restore.sh` has
passed its download, integrity, decryption, and isolated restore checks.

## Budget production replacement

The approved budget launch reuses this Linode and its existing data volumes. It
is a single-host deployment, not high availability. Production replaces staging
during cutover; never run both PostgreSQL services against the shared volume.
Expect a short maintenance window and retain the final staging backup and image
for rollback.

The production files are deliberately separate:

- `compose.production.yml` references the existing PostgreSQL, media-import, and
  Caddy volumes by explicit external names;
- `bootstrap-production-env.sh` preserves the current server-only Django and
  PostgreSQL secrets while generating the production host configuration;
- `/srv/arya-skin/secrets/r2-media.env` supplies the separately protected,
  bucket-scoped R2 credential;
- `/srv/arya-skin/secrets/transactional-email.env` supplies the sending-only
  Resend SMTP credential and staff recipient list;
- `migrate_media_to_r2.sh` defaults to a dry run and requires `--execute` before
  it uploads anything;
- `configure_wagtail_production.py` changes the canonical Wagtail Site only in
  the cutover window; and
- `check_production.sh` verifies the apex, admin redirect, health endpoint, and
  `www` redirect after launch.

Before stopping staging, build and transfer an immutable image, copy the
version-controlled production files to `/srv/arya-skin/production`, generate its
mode-600 `.env`, run the local backup and isolated restore test, and complete the
R2 media dry run and upload. Freeze editorial changes before the final media
sync. The detailed cutover commands must be executed in order and the production
stack must not start until staging has been stopped cleanly.

This budget topology still requires monitoring and the remaining production
acceptance checks before it is called production-ready. Encrypted off-server
database/media backups are configured and restore-tested on staging; the
production timer replaces the staging timer only during cutover.

## Encrypted off-server production backups

`backup_production.sh` creates and validates a PostgreSQL custom-format dump,
then `encrypt_upload_latest_backup.sh` packages the dump and checksum and encrypts
the stream with `age` before upload. `scripts/r2_backup.py` writes only to the
`encrypted/` prefix in the bucket selected by the separately scoped backup token,
verifies object size and SHA-256 metadata, and deletes only matching encrypted
objects older than the approved 14-day retention period.

After the first production backup and periodically thereafter, run
`test_production_restore.sh`. It verifies the latest local manifest, restores the
dump into an isolated temporary PostgreSQL database, runs a query, and removes
only that temporary database. The separate R2 restore proof additionally tests
download, metadata integrity, decryption, and the off-server recovery key.

After changing production media credentials or Docker networking, run the
guarded storage probe through the web container:

```sh
docker compose --file compose.production.yml exec -T web \
  python manage.py shell < test_media_storage_write.py
```

It writes one uniquely named text object below `healthchecks/`, verifies that it
is readable, and deletes it immediately. It does not alter CMS image records.

The scheduled job needs only `backup-age-recipient.txt`, which contains the
public encryption recipient. Keep the private `backup-recovery-key.agekey` as a
secure off-server password-manager attachment. It may be present on the Linode
only for the initial `test_r2_restore.sh` proof and must be removed afterward.
Without that recovery key, encrypted off-server backups cannot be restored.

The production timer must replace, not duplicate, the staging timer at cutover.
Review each run with `systemctl status` and `journalctl`; monitoring of timer
failures remains a separate launch requirement.

## Production appointment notifications

Deploy and migrate with notifications disabled, then publish the repeat-safe
Privacy amendment. Next copy `transactional-email.env.example` to the protected
server secrets directory, set the private recipient and API key, keep it mode
600, and recreate the web container. Never store the key or real recipient in
the repository or display them in command output. Send the patient-data-free
transport test as documented in `docs/APPOINTMENTS.md`.

Install and enable the minute worker only after Dr. Naresh confirms receipt of
that test:

```sh
sudo install -m 0644 arya-skin-production-notifications.service \
  arya-skin-production-notifications.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now arya-skin-production-notifications.timer
sudo systemctl start arya-skin-production-notifications.service
sudo systemctl status arya-skin-production-notifications.service --no-pager
```

The service exits non-zero when a delivery is moved to retrying, making failures
visible in its journal. Automated alerting is still deferred, so include this
service in the manual daily check until external alerts are introduced.
