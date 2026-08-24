# Analytics and attribution

Milestone 6 provides an opt-in analytics implementation. Direct GA4 activation
uses the owner-supplied measurement ID `G-DKBKVGX7NK`; the production switch must
remain off until the account-side controls in this document are confirmed. No
GTM container or Search Console property was created by the application.

## Privacy boundary

- Google code is absent from rendered HTML and no Google analytics request is
  made while analytics is disabled.
- Even with an approved ID, tags remain disabled until the Privacy page is live.
- When enabled, basic consent mode blocks GA4/GTM until a visitor selects
  **Allow analytics**. An initial decline sends nothing to Google.
- The choice is stored only in the visitor's browser under
  `arya_skin_analytics_consent_v2`; appointment submission is never conditional
  on analytics consent.
- Only one provider may be active: direct GA4 is preferred, while GTM is
  available only for an approved, governed container.
- Events use a fixed allowlist and stable page/clinic/treatment slugs. JavaScript
  never reads form fields, link destinations, phone numbers, WhatsApp text, or
  appointment records.
- The accepted-submission event is rendered only after server-side form
  validation and only on the first success-page request.

This is a conservative technical default, not a substitute for legal review of
the final privacy notice, retention, account access, or consent requirements.

## Event contract

| Event | Meaning | Permitted parameters |
| --- | --- | --- |
| `phone_click` | Visitor activates a published telephone link | `page_type`, `clinic_slug` |
| `whatsapp_click` | Visitor activates a WhatsApp CTA | `page_type`, `clinic_slug` |
| `directions_click` | Visitor opens a verified directions URL | `page_type`, `clinic_slug` |
| `appointment_click` | Visitor opens the appointment journey | `page_type`, optional `clinic_slug`/`treatment_slug` |
| `appointment_form_submit` | Server accepted a valid request | `page_type`, `success_state=accepted`, `clinic_slug` |
| `clinic_view` | A published clinic page is viewed | `page_type`, `clinic_slug` |
| `treatment_view` | A published treatment page is viewed | `page_type`, `treatment_slug` |

Never send name, phone, email, date/time preference, message, concern,
diagnosis, form values, destination URL, WhatsApp text, or other patient/medical
data. Custom dimensions, audiences, reports, exports, and GTM variables must
preserve this allowlist.

## Enablement checklist

1. Confirm the clinic owns the GA4 property or governed GTM container and record
   the responsible administrators.
2. Approve and publish the privacy notice and consent wording.
3. In the GA4 web stream, disable automatic **Outbound clicks** and
   **Form interactions**. Outbound measurement can collect the full destination
   URL; this site measures approved actions with its explicit event contract.
4. Do not enable Google Signals, ads personalization, enhanced conversions,
   user-provided data, User-ID, session replay, or form/DOM-scraping tags.
   Set user-level and event-level data retention to **2 months** and turn off
   retention reset on new activity.
5. For GTM, review every tag, trigger, variable, template, permission, and
   publishing role. The container must respect Analytics Storage consent and
   must not read appointment fields or link URLs.
6. A Wagtail superuser may configure exactly one `G-...` or `GTM-...` identifier
   under **Settings -> Site settings**; production may instead use the audited
   `configure_ga4` command. The restricted enquiry account intentionally cannot
   edit site settings. Do not enable analytics until steps 3 and 4 are complete.
7. Test accept, decline, repeat visits, and choice changes in a clean browser.
   Before acceptance, the Network panel must show no requests to Google
   Analytics or Google Tag Manager.
8. Verify the seven events and permitted parameters in Realtime/DebugView or Tag
   Assistant. Register only the approved slug/page parameters as custom
   dimensions and set the clinic-approved data retention period.

Google documents basic consent mode as blocking tags and transmitting no data
before consent: <https://developers.google.com/tag-platform/security/concepts/consent-mode>.
Its enhanced-measurement reference confirms that outbound clicks can collect
full link URLs and that form interaction collection is separately configurable:
<https://support.google.com/analytics/answer/9216061>.

## Search Console

Prefer a Domain property verified through a clinic-controlled DNS account. For a
URL-prefix property, the Wagtail `google_search_console_verification` field can
render the exact content value from Google's HTML verification meta tag. Do not
paste the complete tag. Keep verified owners current, retain more than one
clinic-controlled owner, submit `/sitemap.xml`, and review indexing/security
alerts without granting unnecessary account access.

Google's current ownership requirements are documented at
<https://support.google.com/webmasters/answer/9008080>.

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
other query parameters. Keep a dated campaign-name register so reports remain
interpretable when links change.
