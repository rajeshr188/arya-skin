# Linode private staging

This directory contains the version-controlled, secret-free infrastructure for
`staging.drnareshrathod.com` on the single Linode staging host.

- Caddy is the only service publishing host ports (`80` and `443`).
- PostgreSQL and Gunicorn are reachable only on the internal Docker network.
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
6. Point the Linode DNS `staging` A record to the Linode IPv4 address.
7. Start Caddy only after public DNS resolves to the Linode.
8. Run `./check_staging.sh` on the host, then complete the editorial acceptance
   checks in `docs/STAGING.md`.

## Local staging backups

Install the daily database and media backup timer after the stack is healthy:

```sh
chmod 750 backup_staging.sh test_restore.sh check_staging.sh
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

These access-restricted local copies help with application-level recovery but do
not survive loss of the Linode. Enable Linode Backups or copy backups to
separately controlled encrypted storage before treating off-server backup
coverage as complete.

Do not use this single-host layout for public production. Milestone 7B still
requires object storage, monitoring, transactional email, and restore testing.
