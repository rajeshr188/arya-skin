# Analytics and attribution

Analytics is not enabled in Milestone 1. CMS fields exist for future approved
GA4/GTM identifiers, but templates must not load analytics until consent,
privacy, and account decisions are complete.

## Event contract

| Event | Meaning | Safe context |
| --- | --- | --- |
| `phone_click` | Visitor activates a published telephone link | page type, clinic slug |
| `whatsapp_click` | Visitor activates a WhatsApp CTA | page type, clinic slug |
| `directions_click` | Visitor opens a verified Maps/directions URL | clinic slug |
| `appointment_click` | Visitor opens the appointment-request journey | source page, clinic slug |
| `appointment_form_submit` | A valid request is accepted | success state, clinic slug |
| `clinic_view` | A published clinic page is viewed | clinic slug |
| `treatment_view` | A published treatment page is viewed | treatment slug |

Never send name, phone, email, date/time preference, general concern, message,
WhatsApp text, or any other patient/medical data. Fire submission only after the
server accepts the form, not on button click.

## Implementation policy

- Prefer a small `data-analytics-event` convention and one progressive-enhancement
  script over inline handlers.
- Treat stable content slugs as identifiers; do not use free text entered by a
  visitor.
- Prevent duplicate event firing and test keyboard activation.
- GA4 alone is sufficient unless GTM has a documented operational need.
- Record Search Console verification without exposing secrets.

## UTM convention

Use lowercase snake-case values:

```text
utm_source=google|instagram|facebook|whatsapp|newsletter|partner
utm_medium=organic|social|referral|email|cpc
utm_campaign=<stable_campaign_name>
utm_content=<location_or_creative>
utm_term=<paid_keyword_only>
```

For Google Business Profile use `source=google`, `medium=organic`,
`campaign=gbp`, and content such as `chaksu_website` or
`sitapura_appointment`. Never place personal or health information in UTM or
other query parameters.
