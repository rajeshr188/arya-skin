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
6. Point the GoDaddy `staging` A record to the Linode IPv4 address.
7. Start Caddy only after public DNS resolves to the Linode.
8. Run the acceptance checks in `docs/STAGING.md`.

Do not use this single-host layout for public production. Milestone 7B still
requires object storage, monitoring, transactional email, and restore testing.
