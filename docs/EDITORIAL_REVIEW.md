# Staging editorial review

Review date: 22 August 2026

## Outcome

The owner completed the staging editorial review on 22 August 2026 and approved
the current factual clinic, doctor, contact, privacy, and medical-disclaimer
content for the budget production launch. This is owner editorial acceptance,
not professional legal/privacy or independent medical review. The owner has
explicitly deferred professional legal/privacy review, and analytics remains
disabled.

The final release audit must resolve the Clinic Index page's unpublished revision
and verify the exact live revision of every page after the production data copy.

## Verified in staging

- The public identity is Dr. Naresh Rathod, Dermatologist and Cosmetologist.
- The two independent clinic drafts are correctly named and routed:
  Dolphin Derma Care at `/clinics/sitapura/` and Arya Skin and Hair Clinic at
  `/clinics/chaksu/`.
- Both clinic drafts reference Dr. Naresh Rathod. The owner has approved their
  stored phone number for public calls and WhatsApp at both clinics.
- The doctor page contains the supplied qualifications, confirmed Rajasthan
  Medical Council registration, four practice areas, and three languages.
- No experience claim, biography, membership, affiliation, treatment detail,
  article, testimonial, rating, or patient-outcome claim is published. The
  owner-approved shared service list is published on both clinic pages.
- The owner approved the uploaded doctor portrait for publication and its default
  alternative text is "Portrait of Dr. Naresh Rathod." There are no clinic
  photographs, treatment records, or article records.
- Both clinic pages, the doctor page, Contact, Privacy, and Medical disclaimer are
  live on staging, so the appointment form can route to verified clinic data.

## Release conditions

The owner approved the Privacy and Medical disclaimer wording during the final
editorial review. Professional legal/privacy review remains recommended but was
explicitly deferred by the owner on 22 August 2026 for the budget launch. Do not
describe the wording as professionally reviewed, legally verified, or a guarantee
of compliance.

The public fallback for an unanswered request is approved: after one business
day, ask the requester to call or WhatsApp the selected clinic and reiterate
that an online request is not confirmation or an emergency channel.

Only synthetic details may be used for release testing. Confirm the Clinic Index
revision, clear any hidden time values on days marked closed, and check every
call, WhatsApp, address, schedule, privacy, disclaimer, and appointment route on
the production candidate before DNS cutover.

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
