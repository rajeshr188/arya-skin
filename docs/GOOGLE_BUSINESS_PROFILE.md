# Google Business Profile operating guide

This document is operational guidance only. No Google profile URL or clinic fact
has been supplied yet. Do not scrape Google reviews or use unofficial APIs.

## One profile per eligible real clinic

Confirm eligibility and ownership for Dolphin Derma Care in Sitapura and Arya
Skin and Hair Clinic in Chaksu.
Each eligible profile should link to its own published `ClinicPage`, not an
artificial location variant or a generic campaign page. The appointment link may
point to the future appointment form with the clinic preselected, without putting
medical information in the URL.

## Consistency checklist

- Use the same official business name, postal address, primary phone, and hours
  on the profile, clinic page, signage, and major citations.
- Choose the most accurate primary category and only factual secondary categories.
- List only services genuinely delivered at that branch.
- Keep regular and special/holiday hours current.
- Use a direct Google Maps URL for the site's Directions action.
- Add current, authentic exterior, reception, consultation, team, and approved
  equipment photography; avoid misleading stock images.
- Keep the profile website URL, appointment URL, and clinic page canonical URL
  current after any site migration.

## Reviews, questions, and posts

- Ask for reviews neutrally; never incentivize, gate, fabricate, or selectively
  suppress feedback.
- Respond professionally without confirming a person's patient status or
  disclosing health information.
- Do not copy Google ratings/counts onto the site manually as if live.
- If testimonials are curated on the website, retain permission, source, wording,
  and date. Investigate an officially supported API separately before automation.
- Answer profile Q&A with general factual information, not individualized advice.
- Keep profile posts useful, current, and consistent with published site content.

## Recommended UTM links

Use lowercase values and keep names stable:

```text
Clinic website:
?utm_source=google&utm_medium=organic&utm_campaign=gbp&utm_content=sitapura_website

Appointment link:
?utm_source=google&utm_medium=organic&utm_campaign=gbp&utm_content=sitapura_appointment
```

Replace `sitapura` with `chaksu` for that branch. UTM values must not contain
patient or medical details. Document link changes so historical reporting remains
interpretable.

## Ownership and reporting practice

- Use clinic-controlled Google accounts and keep at least two current owners;
  agencies or contractors should receive only the minimum manager access needed.
- Record the canonical clinic-page URL, appointment URL, UTM values, responsible
  owner, and date of every profile link change.
- Review profile accuracy and special hours on a defined schedule and after any
  operational change. Escalate unauthorized edits immediately.
- Compare GBP performance with Search Console and the site's approved aggregate
  events. Do not attempt to identify a visitor or join analytics activity to an
  appointment enquiry.
- Treat messages, calls, reviews, and Q&A as separate Google/clinic operational
  channels; do not import their personal content into website analytics.
