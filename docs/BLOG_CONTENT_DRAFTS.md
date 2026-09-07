# Prepared blog content drafts

The initial three articles were prepared on 3 September 2026; three further
articles were prepared on 7 September 2026. All require Dr. Naresh Rathod's
editorial and medical review. The seed command does not identify an author or
medical reviewer and cannot publish an article. The owner designated Dr. Naresh
Rathod as both author and assigned medical reviewer, with the public role
"Dermatologist and Cosmetologist"; that assignment does not claim review is
complete. Existing Wagtail articles are preserved when new drafts are imported.

## Draft set

1. **Acne treatment takes time: what to expect from a plan**
   - Intent: set realistic expectations about consistency, follow-up, and the
     usual delay before improvement can be judged.
   - Related draft: Acne assessment and treatment.
   - Sources: American Academy of Dermatology acne overview and diagnosis/
     treatment guidance.
2. **Patch testing for skin allergy: what it can and cannot tell you**
   - Intent: distinguish delayed contact-allergy investigation from a general
     or immediate allergy test and explain why history and interpretation matter.
   - Related draft: Skin allergy assessment and testing.
   - Sources: American Academy of Dermatology and NHS contact-dermatitis
     diagnosis guidance.
3. **Chemical peels: a safety-first consultation checklist**
   - Intent: help a reader ask about suitability, skin tone, risks, recovery,
     alternatives, and aftercare; warn against unsupervised strong home peels.
   - Related draft: Chemical peel consultation.
   - Sources: US Food and Drug Administration warning and American Academy of
     Dermatology preparation/FAQ guidance.
4. **Hair shedding or hair loss: what clues matter at a consultation**
   - Intent: help readers distinguish patterns worth recording, recognize scalp
     findings that deserve timely assessment, and prepare a useful history.
   - Related draft: General dermatology consultation.
   - Sources: American Academy of Dermatology diagnosis and signs guidance, and
     NHS hair-loss guidance.
5. **Daily sun protection: how to choose and use sunscreen well**
   - Intent: explain broad-spectrum protection, SPF, water resistance,
     application, reapplication, shade, and protective clothing without product
     promotion.
   - Related draft: General dermatology consultation.
   - Sources: American Academy of Dermatology selection/application guidance and
     current US Food and Drug Administration consumer guidance.
6. **Ringworm and fungal skin infections: why the right diagnosis matters**
   - Intent: explain why ring-shaped rashes need context, warn against steroid
     creams on an undiagnosed possible fungal infection, and reduce spread.
   - Related draft: General dermatology consultation.
   - Sources: US Centers for Disease Control and Prevention ringworm guidance
     and American Academy of Dermatology signs guidance.

Every direct source URL and the access date are stored with the relevant Wagtail
article.

## Original illustrations

The six generated editorial illustrations are project-owned source assets in
`content_assets/blog/`. They use the site's green, mint, cream, and terracotta
palette and deliberately contain no text, brands, before-and-after comparison,
unverified equipment, or promised outcome.

Alternative text prepared with the drafts:

- `acne-treatment-takes-time.png`: "A woman following a simple skin-care
  routine beside a calendar"
- `patch-testing-explained-v2.png`: "An adult patient with patch-test chambers
  attached to the upper back"
- `chemical-peel-safety-checklist.png`: "A woman reviewing a procedure
  checklist with sun-protection items"
- `hair-shedding-or-hair-loss.png`: "An adult man viewing gradual thinning at
  the crown of his scalp"
- `daily-sun-protection-sunscreen.png`: "Sun-protection items arranged around
  an unbranded sunscreen bottle"
- `ringworm-fungal-skin-infection.png`: "An illustrated magnifier examining a
  circular scaly patch on brown skin"

The images are imported into Wagtail/R2 only when the execute mode is used.
Wagtail renditions, rather than the full original files, serve the article page
and cards.

For future illustrations, a depicted clinic doctor must be male and must not
suggest that an unnamed clinician or staff member provides care. Prefer a clearly
patient-focused scene when the doctor's identity is not needed. If Dr. Naresh
Rathod is meant to be recognizable, use his approved portrait as an explicit
reference rather than inventing a likeness.

## Safe import

Preview the operation first:

```powershell
uv run manage.py seed_blog_drafts
```

Create any missing illustrated drafts:

```powershell
uv run manage.py seed_blog_drafts --execute
```

Preview and then apply the approved author/reviewer assignment:

```powershell
uv run manage.py assign_blog_editorial_roles
uv run manage.py assign_blog_editorial_roles --execute
```

The command is repeat-safe and additive. It preserves existing articles and an
already-published Articles index, while refusing a prepared slug outside that
index, unexpected initial index copy, missing illustrations, or missing related
treatment drafts.

## Required review before publication

For each article, Dr. Naresh Rathod should:

1. verify every medical statement and request corrections where needed;
2. verify the recorded author and assigned-reviewer attribution;
3. review the title, excerpt, illustration, alternative text, and direct sources;
4. confirm that the related treatment is appropriate;
5. enter the real completed-review date and an optional future review date; and
6. explicitly approve the article and Articles index for publication.

Until those steps are complete, the publication guard keeps the articles and
index unavailable to anonymous visitors, navigation, search engines, the
homepage article area, and the sitemap.
