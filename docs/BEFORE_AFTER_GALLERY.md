# Before and after gallery

The CMS contains one gallery page at `/before-after/`. It is seeded as an empty
draft and does not become public until at least one comparison passes the
publication safeguards.

## Adding a comparison

1. Obtain documented consent that specifically permits public website use of
   both photographs. Keep the consent record in the clinic's approved private
   process; never upload it to the website CMS.
2. Remove names, record numbers, dates, location metadata, and other identifiers
   from the files. Do not upload more of the face or body than is necessary.
3. In Wagtail, upload the before and after images with accurate image
   descriptions, then edit **Before and after** and add a comparison.
4. Use a neutral title and, only if useful, short verified context. Do not promise
   results, imply that an example is typical, or state an unverified treatment or
   time interval.
5. Confirm both required checks: publication consent is documented; and the
   labels, same-person comparison, crop, lighting, and editing have been reviewed
   so the presentation is not misleading.
6. Preview the page on mobile and desktop. Dr. Naresh Rathod must approve the
   final pair and wording before the page is published.

The public results-vary notice is fixed in the template and cannot be removed by
an editor. The model also blocks publication of an empty gallery, missing image
descriptions, reused before/after images, or entries without both confirmations.

If consent is withdrawn, unpublish the gallery or remove the comparison promptly
and delete unused CMS images. A deleted database reference may remain in an
encrypted backup until that backup reaches the approved expiry described in the
Privacy notice.

## Educational illustrations are different

The current gallery and its confirmation fields are designed for genuine,
same-patient photographs. Do not place generated, stock, or illustrated imagery
in it and do not use the patient-consent confirmation for synthetic artwork.
Illustrated comparisons must be presented separately, visibly identified as
educational illustrations, and must never be described as patient results.

Prepared illustration-only concepts and their review wording are recorded in
`ILLUSTRATED_COMPARISON_DRAFTS.md`. The separate **Illustrated care journeys**
page provides a permanent disclosure and illustration-specific review checks;
it remains unpublished until Dr. Naresh Rathod approves every pair.
