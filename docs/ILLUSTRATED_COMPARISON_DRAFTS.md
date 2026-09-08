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

## 4. Visible facial redness

- Neutral title: **Illustrated change in visible facial redness**
- Before file: `content_assets/before_after/facial-redness-before.jpg`
- Before description: Illustration of an adult woman with moderate diffuse
  redness across both central cheeks and around the sides of the nose.
- After file: `content_assets/before_after/facial-redness-after.jpg`
- After description: Matching illustration of the same woman with milder
  residual redness across the central cheeks and natural skin texture.
- Presentation note: Do not label the appearance as rosacea, identify a trigger,
  or imply that every skin tone displays facial colour change in the same way.

Visual wording was checked against the American Academy of Dermatology's
[rosacea signs and symptoms](https://www.aad.org/public/diseases/rosacea/what-is/symptoms)
guidance. The pair remains deliberately non-diagnostic because redness and
colour change can have different causes and appearances.

## 5. Shaving-area bumps

- Neutral title: **Illustrated change in shaving-area bumps**
- Before file: `content_assets/before_after/shaving-area-bumps-before.jpg`
- Before description: Three-quarter illustration of an adult man with several
  small raised bumps and flat dark marks along the lower jaw and upper neck.
- After file: `content_assets/before_after/shaving-area-bumps-after.jpg`
- After description: Matching illustration of the same man with fewer raised
  bumps, several residual dark marks and unchanged beard density.
- Presentation note: Do not diagnose razor bumps, folliculitis or acne from an
  illustration and do not connect the change to a product or procedure.

The location and neutral wording were checked against the American Academy of
Dermatology's [folliculitis overview](https://www.aad.org/public/diseases/a-z/folliculitis)
and [razor-bump guidance](https://www.aad.org/news/how-to-prevent-razor-bumps).
These sources support the visual vocabulary, not a diagnosis or expected result.

## 6. Raised welt-like patches

- Neutral title: **Illustrated change in raised welt-like patches**
- Before file: `content_assets/before_after/raised-welts-before.jpg`
- Before description: Close illustration of a brown-skinned adult forearm with
  several smooth raised pink-brown patches of varied size.
- After file: `content_assets/before_after/raised-welts-after.jpg`
- After description: Matching illustration of the same forearm with two faint
  raised patches, mild residual uneven colour and natural skin texture.
- Presentation note: Do not diagnose hives, identify an allergy or trigger, or
  connect the depicted change to a medicine or other treatment.

Visual signs were checked against the American Academy of Dermatology's
[hives signs and symptoms](https://www.aad.org/public/diseases/a-z/hives-symptoms)
guidance. Raised patches can vary in shape and colour and may have several
causes, so the pair stays non-diagnostic.

## Required review before use

Dr. Naresh Rathod should confirm that:

- each visual is anatomically and clinically reasonable;
- the change is not exaggerated or presented as typical;
- before and after crops, lighting, identity, and colour treatment are fairly
  matched;
- the educational-illustration disclosure is prominent; and
- placement does not make the assets look like genuine patient results.

Run `python manage.py seed_illustrated_care_journeys` to preview the import and add
`--execute` to create any missing prepared pairs as an unpublished draft. The
command is repeat-safe, preserves the existing ordered prefix, and refuses to
overwrite mismatched journey content. It also preserves an established page's
editorial introduction. If the page is already live, additions are stored in a
new unpublished revision without changing the version visitors can see. Keep
each addition unpublished until the checks above are complete.
