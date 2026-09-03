# Initial blog content drafts

Prepared on 3 September 2026 for Dr. Naresh Rathod's editorial and medical
review. These articles and the Articles index are unpublished. The initial seed
command does not identify an author or medical reviewer and cannot make the
articles public. The owner subsequently designated Dr. Naresh Rathod as both
author and assigned medical reviewer, with the public role "Dermatologist and
Cosmetologist"; that assignment does not claim the review is complete.

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

Every direct source URL and the access date are stored with the relevant Wagtail
article.

## Original illustrations

The three generated editorial illustrations are project-owned source assets in
`content_assets/blog/`. They use the site's green, mint, cream, and terracotta
palette and deliberately contain no text, brands, before-and-after comparison,
unverified equipment, or promised outcome.

Alternative text prepared with the drafts:

- `acne-treatment-takes-time.png`: "A woman following a simple skin-care
  routine beside a calendar"
- `patch-testing-explained.png`: "A woman reviewing everyday skin-care products
  beside a patch-test symbol"
- `chemical-peel-safety-checklist.png`: "A woman reviewing a procedure
  checklist with sun-protection items"

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

Create the three illustrated drafts:

```powershell
uv run manage.py seed_blog_drafts --execute
```

Preview and then apply the approved author/reviewer assignment:

```powershell
uv run manage.py assign_blog_editorial_roles
uv run manage.py assign_blog_editorial_roles --execute
```

The command is repeat-safe after a complete import and refuses a partial set,
an already-published Articles index, unexpected existing index copy, missing
illustrations, or missing related treatment drafts.

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
