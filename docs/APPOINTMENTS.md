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

No email, SMS, WhatsApp API, calendar, CRM, or analytics integration is enabled.
The clinic must approve access, retention, consent wording, and response practice
before public launch.
