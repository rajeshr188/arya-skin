# Staging editorial review

Review date: 22 August 2026

## Outcome

The private staging site is suitable for owner editing and preview, but its
content is not approved for public production. The verified homepage is live on
staging. Every page that depends on incomplete business, legal, or medical facts
remains unpublished, and analytics remains disabled.

## Verified in staging

- The public identity is Dr. Naresh Rathod, Dermatologist and Cosmetologist.
- The two independent clinic drafts are correctly named and routed:
  Dolphin Derma Care at `/clinics/sitapura/` and Arya Skin and Hair Clinic at
  `/clinics/chaksu/`.
- Both clinic drafts reference Dr. Naresh Rathod. Their stored phone and WhatsApp
  values are not exposed because publication consent is disabled.
- The doctor draft contains the supplied qualifications, confirmed Rajasthan
  Medical Council registration, four practice areas, and three languages.
- No experience claim, biography, membership, affiliation, treatment, article,
  testimonial, rating, or clinic service is published.
- There are no treatment or article records and no uploaded images. This is
  acceptable for private structural staging.
- The appointment form remains unavailable until at least one clinic is approved
  and published. This prevents enquiries being routed to incomplete clinic data.

## Required before publishing clinic and appointment pages

The owner must approve or supply:

1. Whether the stored phone number may receive public calls for each clinic.
2. Whether that number may be published as WhatsApp for each clinic.
3. Final Sitapura address formatting and the complete Chaksu address.
4. Opening hours, weekly closures, and Dr. Naresh Rathod's availability at each
   clinic.
5. The services genuinely offered at each clinic.
6. The appointment contact-consent wording, enquiry retention period, authorized
   staff, and expected response process.
7. Final privacy-policy and medical-disclaimer wording.

Do not publish the clinic pages merely to test the form. Use Wagtail Preview for
content review; once the facts above are approved, publish the doctor page,
clinic index, approved clinic pages, contact/legal pages, and then test the form
using synthetic details.

## May be completed later

The professional biography, care philosophy, memberships, affiliations,
portrait, clinic photographs, maps/Google Business Profile links, arrival and
parking guidance, social profiles, and default sharing image may be added later.
Unknown accessibility information must stay blank rather than imply access that
has not been verified.

Treatment pages and articles may also remain absent. Before any medical page is
published, approve its content, genuine author/reviewer, sources, imagery, and
review date using the workflows in `CONTENT_REQUIRED.md` and
`BLOG_EDITORIAL.md`.

## Operational notes

- The generated Wagtail welcome page remains as an unreachable page outside the
  configured Site root. It has no public effect but can be removed later to make
  the page explorer less confusing.
- Daily local database/media backups and the tested restore procedure remain
  enabled. The owner has deferred paid Linode backups for the budget staging
  phase and accepts that local backups will not survive total server loss.
