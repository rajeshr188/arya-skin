# Illustrated comparison drafts

Prepared on 7 September 2026 as educational artwork. These files are synthetic
illustrations, not patient photographs, clinical evidence, or predictions of an
individual result. They do not identify a treatment, product, procedure, or time
interval.

Do not add these assets to the patient **Before and after** gallery by confirming
that patient publication consent exists. That confirmation would not accurately
describe synthetic artwork. The separate **Illustrated care journeys** CMS page
has a permanent disclosure and illustration-specific publication checks.

Every displayed pair should include this visible disclosure:

> Educational illustration—not a patient photograph or a promised result. The
> same appearance can have different causes, and individual outcomes vary.

## 1. Visible acne

- Neutral title: **Illustrated change in visible acne**
- Before file: `content_assets/before_after/acne-visible-change-before.jpg`
- Before description: Illustration of an adult man with several raised acne
  blemishes and flat dark marks on both cheeks.
- After file: `content_assets/before_after/acne-visible-change-after.jpg`
- After description: Matching illustration of the same man with fewer raised
  blemishes and some residual dark marks and natural skin texture.
- Presentation note: Do not name a treatment or imply that all acne or dark marks
  follow this course.

Visual signs were checked against the American Academy of Dermatology's
[acne signs and symptoms](https://www.aad.org/public/diseases/acne/really-acne/symptoms)
guidance. The source supports the general visual vocabulary, not the depicted
change as an expected outcome.

## 2. Dry, scaly skin

- Neutral title: **Illustrated change in a dry, scaly skin patch**
- Before file: `content_assets/before_after/dry-scaly-skin-before.jpg`
- Before description: Close illustration of a medium-brown forearm with one
  localized dry, scaly and mildly discoloured patch.
- After file: `content_assets/before_after/dry-scaly-skin-after.jpg`
- After description: Matching illustration of the same forearm with less visible
  scaling and mild residual uneven colour and natural skin texture.
- Presentation note: Do not label the appearance as eczema or another diagnosis
  without a real clinical assessment.

Visual signs were checked against the American Academy of Dermatology's
[atopic dermatitis symptoms](https://www.aad.org/public/diseases/eczema/types/atopic-dermatitis/symptoms)
guidance. The pair intentionally remains non-diagnostic.

## 3. Visible scalp flaking

- Neutral title: **Illustrated change in visible scalp flaking**
- Before file: `content_assets/before_after/scalp-flaking-before.jpg`
- Before description: Rear three-quarter illustration of an adult man's scalp
  with small white flakes along the hair part and nearby hair.
- After file: `content_assets/before_after/scalp-flaking-after.jpg`
- After description: Matching illustration of the same scalp and hairstyle with
  fewer visible flakes and no change in hair density.
- Presentation note: Do not call the appearance dandruff, seborrhoeic dermatitis,
  psoriasis, eczema, or infection without diagnosis. Do not imply hair regrowth.

Visual signs were checked against the American Academy of Dermatology's
[dandruff guidance](https://www.aad.org/public/everyday-care/hair-scalp-care/scalp/treat-dandruff).
The source notes that scalp flaking can have different causes, which is why this
pair uses neutral wording.

## Required review before use

Dr. Naresh Rathod should confirm that:

- each visual is anatomically and clinically reasonable;
- the change is not exaggerated or presented as typical;
- before and after crops, lighting, identity, and colour treatment are fairly
  matched;
- the educational-illustration disclosure is prominent; and
- placement does not make the assets look like genuine patient results.

Run `python manage.py seed_illustrated_care_journeys` to preview the import and add
`--execute` to create the three pairs as an unpublished draft. The command is
repeat-safe and refuses to overwrite existing editorial content. Keep the page
unpublished until the checks above are complete.
