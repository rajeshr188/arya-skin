# Appointment enquiry workflow

The Milestone 3 workflow is a contact request, not online scheduling and not a
patient record. It becomes available only when at least one unrestricted clinic
page is published.

## Public data and behavior

The form stores the selected clinic, name, phone, optional email, preferred date,
time preference, contact consent and consent version, server-controlled source
path, and timestamps. It does not request a diagnosis, detailed concern, date of
birth, postal address, uploaded document, or patient account.

The confirmation page never includes submitted values or a reference in its URL.
Form responses are marked no-cache. CSRF, a signed two-hour form token, a hidden
honeypot, and a per-session submission window provide first-party abuse controls.
The default rate is five accepted requests per browser session per hour.

## Staff workflow

Authorized staff use `/admin/appointments/appointmentenquiry/`. Personal and
consent fields are read-only; staff may change status and add a short
administrative follow-up note. The supported states are new, contacted,
scheduled, closed, and spam. This note must not be used for diagnosis or clinical
records.

When transactional email is enabled, each accepted enquiry creates a durable
database delivery record for every configured staff recipient. A systemd timer
runs the delivery command every minute. Failed deliveries retain only the
exception type, retry after 1, 5, and 15 minutes, then 1 and 6 hours, and continue
at six-hour intervals. The enquiry remains saved even if the provider is down.

Notification email contains only the clinic name, received time, and a generic
secure admin link. It intentionally excludes name, phone, email, preferred
date/time, source path, enquiry reference, and any patient-entered value. Resend
is the SMTP transport; it receives the designated staff recipient address and
this privacy-minimized message, not the enquiry contents. SMS, WhatsApp API,
calendar, CRM, and patient acknowledgement email remain disabled.

The approved consent wording is `appointment-contact-v1`. Dr. Naresh Rathod is
the only currently designated enquiry monitor and initial notification
recipient, with a response target of one business day. His separate restricted
CMS account has only appointment-enquiry view and change permissions; it is not
a superuser and cannot delete enquiries. The daily admin-page review remains the
fallback until production delivery has been verified and whenever automated
notification health is uncertain.
If no response is received within one business day, the requester is instructed
to call or WhatsApp the selected clinic. The approved fallback also reiterates
that the request is not confirmation and must not be used for emergencies.
Closed enquiries are retained for 90 days; run
`python manage.py purge_closed_enquiries` on a schedule before enabling the
public form. Do not grant another person access without explicit approval and a
separate accountable login.

## Production operation

Keep SMTP values in `/srv/arya-skin/secrets/transactional-email.env`, mode 600.
Do not paste the API key into Git, chat, command output, or the main `.env`.
Deploy and migrate with notifications still disabled, then run the repeat-safe
privacy update:

```sh
docker compose --env-file .env --file compose.production.yml exec -T web \
  python manage.py update_appointment_email_privacy
```

Only then install the protected SMTP environment, recreate the web container so
it reads the values, and run the privacy-safe transport test:

```sh
docker compose --env-file .env --file compose.production.yml up -d \
  --force-recreate web
docker compose --env-file .env --file compose.production.yml exec -T web \
  python manage.py send_appointment_notification_test
```

Install `arya-skin-production-notifications.service` and its timer in
`/etc/systemd/system`, then inspect `systemctl status` and `journalctl` after the
first run. The admin enquiry list shows pending, retrying, and sent counts without
displaying recipient addresses.
