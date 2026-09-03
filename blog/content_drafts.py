"""Source-checked patient-education drafts for editorial review."""

from datetime import date


BLOG_INDEX_INTRODUCTION = (
    "<p>Clear, practical information about common skin concerns, consultations, "
    "and procedure safety. These articles provide general education and do not "
    "replace an individual medical assessment.</p>"
)

SOURCE_ACCESSED_ON = date(2026, 9, 3)

BLOG_DRAFTS = (
    {
        "title": "Acne treatment takes time: what to expect from a plan",
        "slug": "acne-treatment-takes-time",
        "category": ("Acne care", "acne-care"),
        "excerpt": (
            "Why acne treatment is usually measured in weeks rather than days, "
            "what consistency means, and when it is sensible to seek a review."
        ),
        "search_description": (
            "A practical guide to acne treatment timelines, consistent skin care, "
            "follow-up, and when to consult a dermatologist."
        ),
        "image": {
            "filename": "acne-treatment-takes-time.png",
            "title": "Acne care takes time - editorial illustration",
            "alt_text": (
                "A woman following a simple skin-care routine beside a calendar"
            ),
        },
        "related_treatment_slug": "acne-assessment-treatment",
        "body": [
            (
                "rich_text",
                "<p>Acne can be frustrating partly because improvement is rarely "
                "instant. A treatment plan has to address the type and severity of "
                "the acne, where it appears, the risk of marks or scarring, and the "
                "person's health and preferences. What helps one person may not be "
                "the right choice for another.</p><p>A sensible plan therefore has "
                "two parts: choosing an appropriate approach and giving it enough "
                "time to judge the response safely.</p>",
            ),
            (
                "heading",
                {"text": "Why progress is usually gradual", "level": "h2"},
            ),
            (
                "rich_text",
                "<p>The American Academy of Dermatology advises that it commonly "
                "takes at least six to eight weeks to begin seeing fewer breakouts. "
                "That does not mean every plan works on the same schedule, or that "
                "a particular result can be promised. It means that changing products "
                "every few days can make it difficult to tell what is helping and may "
                "irritate the skin.</p><p>Use treatment exactly as advised. If a product "
                "causes a concerning reaction, or if the instructions are unclear, "
                "contact the treating clinician rather than simply adding more "
                "products.</p>",
            ),
            (
                "heading",
                {"text": "What consistency looks like", "level": "h2"},
            ),
            (
                "rich_text",
                "<ul><li>Follow the agreed routine and application instructions.</li>"
                "<li>Use gentle, non-comedogenic skin-care and cosmetic products when "
                "recommended.</li><li>Avoid squeezing or picking spots, which can "
                "increase inflammation and the chance of marks.</li><li>Note new "
                "symptoms, irritation, missed applications, and changes in other "
                "medicines.</li><li>Attend follow-up so the plan can be adjusted based "
                "on the actual response.</li></ul><p>Consistency does not mean enduring "
                "severe side effects. A clinician should explain what may be expected "
                "and what should prompt earlier contact.</p>",
            ),
            (
                "heading",
                {"text": "When to arrange a dermatology review", "level": "h2"},
            ),
            (
                "rich_text",
                "<p>Consider an assessment when acne is deep or painful, is leaving "
                "scars or persistent dark marks, is affecting confidence or daily "
                "life, or has not improved despite a consistent routine. Sudden or "
                "unusual acne-like eruptions can also need assessment because not "
                "every facial bump is acne.</p><p>At a consultation, be ready to explain "
                "when the problem began, where it occurs, what has already been tried, "
                "and which medicines or supplements are being used. Mention pregnancy "
                "or pregnancy plans because they can affect which options are suitable.</p>",
            ),
            (
                "information",
                {
                    "style": "information",
                    "heading": "A useful goal for follow-up",
                    "text": (
                        "<p>Follow-up is not only about asking whether the skin is "
                        "clear. It is a chance to compare the number and type of new "
                        "breakouts, check side effects, discuss marks or scarring, and "
                        "decide whether to continue, adjust, or change the plan.</p>"
                    ),
                },
            ),
            (
                "faq",
                {
                    "heading": "Common questions",
                    "items": [
                        {
                            "question": "Should I stop if I do not see a change in a week?",
                            "answer": (
                                "<p>Not necessarily. Acne plans often need several "
                                "weeks before improvement can be judged. Follow the "
                                "instructions you were given and ask the clinician if "
                                "you are unsure or develop a concerning reaction.</p>"
                            ),
                        },
                        {
                            "question": "Does stronger treatment always work faster?",
                            "answer": (
                                "<p>No. More is not automatically better and can cause "
                                "irritation or other harm. The choice and strength of "
                                "treatment should match the individual assessment.</p>"
                            ),
                        },
                        {
                            "question": "Can acne marks be discussed at the same visit?",
                            "answer": (
                                "<p>Yes. Tell the clinician about dark marks or scarring. "
                                "Controlling active acne and discussing the type of mark "
                                "are important before considering additional procedures.</p>"
                            ),
                        },
                    ],
                },
            ),
        ],
        "sources": (
            {
                "title": "Acne: Overview",
                "publisher": "American Academy of Dermatology",
                "url": "https://www.aad.org/public/diseases/acne/really-acne/overview",
            },
            {
                "title": "Acne: Diagnosis and treatment",
                "publisher": "American Academy of Dermatology",
                "url": "https://www.aad.org/public/diseases/acne/derm-treat/treat",
            },
        ),
    },
    {
        "title": "Patch testing for skin allergy: what it can and cannot tell you",
        "slug": "patch-testing-skin-allergy-explained",
        "category": ("Skin allergy", "skin-allergy"),
        "excerpt": (
            "Patch testing investigates delayed contact allergy. Learn why the "
            "history still matters, what the test involves, and what its limits are."
        ),
        "search_description": (
            "Understand when patch testing may be used for allergic contact dermatitis, "
            "how it differs from other allergy tests, and how results are interpreted."
        ),
        "image": {
            "filename": "patch-testing-explained.png",
            "title": "Patch testing explained - editorial illustration",
            "alt_text": (
                "A woman reviewing everyday skin-care products beside a patch-test symbol"
            ),
        },
        "related_treatment_slug": "skin-allergy-assessment-testing",
        "body": [
            (
                "rich_text",
                "<p>An itchy or recurring rash can have many causes. Contact dermatitis "
                "is one possibility: something touching the skin may irritate it, or "
                "may trigger a delayed allergic reaction. These two processes can look "
                "similar, so the pattern of the rash and a careful exposure history "
                "remain important.</p><p>Patch testing is one tool a dermatologist may "
                "consider when allergic contact dermatitis is suspected. It does not "
                "replace the consultation, and it is not a general test for every type "
                "of allergy or every rash.</p>",
            ),
            (
                "heading",
                {"text": "What patch testing looks for", "level": "h2"},
            ),
            (
                "rich_text",
                "<p>Small amounts of selected substances are placed in chambers that "
                "are taped to the skin, commonly on the back. The patches are removed "
                "later and the skin is checked on more than one occasion because an "
                "allergic contact reaction can take time to appear. The exact series "
                "of substances and visit schedule depend on the clinical question and "
                "local practice.</p><p>This is different from a skin-prick test. Patch "
                "testing is mainly used to investigate delayed allergy from skin "
                "contact; it is not designed to diagnose immediate breathing, food, "
                "or anaphylactic reactions.</p>",
            ),
            (
                "heading",
                {"text": "Why your everyday exposures matter", "level": "h2"},
            ),
            (
                "rich_text",
                "<p>A test result only becomes useful when it fits the real exposure. "
                "Before a consultation, think about skin, hair, nail, fragrance, and "
                "cleaning products; jewellery and clothing; work materials; hobbies; "
                "and anything applied by another person. A rash may appear hours or "
                "days after contact, and it may occur away from the most obvious contact "
                "site.</p><p>Bring product packaging or clear ingredient lists if asked. "
                "Do not apply an unknown household substance to the skin to test it "
                "yourself.</p>",
            ),
            (
                "heading",
                {"text": "What a result does not prove on its own", "level": "h2"},
            ),
            (
                "rich_text",
                "<p>A positive patch-test reaction shows sensitisation to a tested "
                "substance, but the clinician still has to decide whether that substance "
                "explains the current rash. A negative result does not rule out every "
                "possible cause, especially when the relevant substance was not tested "
                "or the condition is not allergic contact dermatitis.</p><p>Availability "
                "of patch testing, the appropriate test series, and whether referral is "
                "needed should be confirmed during consultation.</p>",
            ),
            (
                "information",
                {
                    "style": "warning",
                    "heading": "Know when this is not a routine appointment",
                    "text": (
                        "<p>Breathing difficulty, swelling of the lips, tongue, face, "
                        "or throat, faintness, or a rapidly worsening widespread "
                        "reaction needs emergency care. Do not wait for patch testing "
                        "or an online appointment response.</p>"
                    ),
                },
            ),
            (
                "faq",
                {
                    "heading": "Common questions",
                    "items": [
                        {
                            "question": "Is patch testing the same as a skin-prick test?",
                            "answer": (
                                "<p>No. Patch testing looks mainly for delayed allergic "
                                "contact reactions. Skin-prick testing is used for "
                                "different, immediate allergic responses.</p>"
                            ),
                        },
                        {
                            "question": "Does a positive result explain every rash?",
                            "answer": (
                                "<p>No. The result has to be interpreted alongside the "
                                "rash pattern and real-life exposures. A positive result "
                                "may not be relevant to the current problem.</p>"
                            ),
                        },
                        {
                            "question": "Should I stop all products before my visit?",
                            "answer": (
                                "<p>Do not make broad changes without advice. Record what "
                                "you use and follow any preparation instructions given by "
                                "the clinic or testing centre.</p>"
                            ),
                        },
                    ],
                },
            ),
        ],
        "sources": (
            {
                "title": "Contact dermatitis: Diagnosis and treatment",
                "publisher": "American Academy of Dermatology",
                "url": (
                    "https://www.aad.org/public/diseases/eczema/types/"
                    "contact-dermatitis/treatment"
                ),
            },
            {
                "title": "Contact dermatitis - Diagnosis",
                "publisher": "NHS",
                "url": "https://www.nhs.uk/conditions/contact-dermatitis/diagnosis/",
            },
        ),
    },
    {
        "title": "Chemical peels: a safety-first consultation checklist",
        "slug": "chemical-peel-safety-checklist",
        "category": ("Procedure safety", "procedure-safety"),
        "excerpt": (
            "Questions to ask before a chemical peel, from suitability and expected "
            "recovery to skin tone, aftercare, alternatives, and possible risks."
        ),
        "search_description": (
            "Use this safety-first checklist when discussing a chemical peel, including "
            "suitability, risks, recovery, aftercare, and at-home peel warnings."
        ),
        "image": {
            "filename": "chemical-peel-safety-checklist.png",
            "title": "Chemical peel safety checklist - editorial illustration",
            "alt_text": (
                "A woman reviewing a procedure checklist with sun-protection items"
            ),
        },
        "related_treatment_slug": "chemical-peel-consultation",
        "body": [
            (
                "rich_text",
                "<p>A chemical peel is not one standard product or procedure. Peels "
                "vary in ingredient, concentration, depth, preparation, recovery, and "
                "risk. The right question is not simply, 'Which peel is strongest?' It "
                "is whether a peel is appropriate for the concern and, if so, which "
                "approach offers a reasonable balance of benefit and risk.</p><p>A "
                "consultation should happen before treatment. Use the discussion to "
                "understand the plan rather than to obtain a promised result.</p>",
            ),
            (
                "heading",
                {"text": "Questions about suitability", "level": "h2"},
            ),
            (
                "rich_text",
                "<ul><li>What diagnosis or concern is the peel intended to address?</li>"
                "<li>Is a peel suitable for my skin tone and history?</li><li>Which "
                "ingredient and depth are being considered, and why?</li><li>Could my "
                "medicines, recent procedures, tendency to scar, infection history, or "
                "sun exposure change the risk?</li><li>What alternatives should I "
                "consider, including doing nothing for now?</li></ul><p>Experience with "
                "the person's skin tone matters because unwanted lighter or darker "
                "pigmentation can occur. Give an accurate history and mention all skin "
                "products, medicines, supplements, and previous cosmetic procedures.</p>",
            ),
            (
                "heading",
                {"text": "Questions about the procedure and recovery", "level": "h2"},
            ),
            (
                "rich_text",
                "<ul><li>Who will perform the procedure, and what training and experience "
                "do they have with this peel and my skin tone?</li><li>What preparation "
                "is required?</li><li>What discomfort, redness, swelling, scaling, or "
                "downtime might occur?</li><li>What are the important risks and warning "
                "signs?</li><li>What aftercare and sun protection will be needed?</li>"
                "<li>When should follow-up occur?</li></ul><p>Ask for realistic ranges, "
                "not guarantees. Recovery varies with peel depth and individual response.</p>",
            ),
            (
                "heading",
                {"text": "Why strong at-home peels are a safety concern", "level": "h2"},
            ),
            (
                "rich_text",
                "<p>The US Food and Drug Administration has warned consumers against "
                "using certain high-concentration chemical peel products without "
                "appropriate professional supervision. These products can penetrate "
                "deeply enough to cause chemical burns, pain, swelling, infection, "
                "skin-colour changes, and scarring.</p><p>Do not assume that an online "
                "product is safe because it is labelled 'professional', 'natural', or "
                "'for home use'. Do not increase concentration, layers, or contact time "
                "in an attempt to speed up a result.</p>",
            ),
            (
                "information",
                {
                    "style": "warning",
                    "heading": "Seek help for an unexpected reaction",
                    "text": (
                        "<p>After a peel, obtain prompt medical advice for severe or "
                        "worsening pain, extensive blistering, spreading redness, "
                        "discharge, fever, an eye concern, or another unexpected "
                        "reaction. Follow emergency advice when symptoms are severe.</p>"
                    ),
                },
            ),
            (
                "faq",
                {
                    "heading": "Common questions",
                    "items": [
                        {
                            "question": "Does a deeper peel always mean a better result?",
                            "answer": (
                                "<p>No. Greater depth also changes recovery and risk. "
                                "The appropriate option depends on the concern, skin, "
                                "medical history, and a clinician's assessment.</p>"
                            ),
                        },
                        {
                            "question": "Can a chemical peel be guaranteed to remove marks?",
                            "answer": (
                                "<p>No. Results vary, and some types of marks or "
                                "pigmentation may not be suitable for a peel. The likely "
                                "benefit, limitations, and alternatives should be "
                                "discussed before treatment.</p>"
                            ),
                        },
                        {
                            "question": "Why is sun protection discussed before a peel?",
                            "answer": (
                                "<p>Sun exposure can affect preparation, recovery, and "
                                "the risk of unwanted pigment change. Follow the specific "
                                "before-and-after instructions provided for the selected "
                                "procedure.</p>"
                            ),
                        },
                    ],
                },
            ),
        ],
        "sources": (
            {
                "title": (
                    "FDA warns against purchasing or using chemical peel skin products "
                    "without professional supervision"
                ),
                "publisher": "US Food and Drug Administration",
                "url": (
                    "https://www.fda.gov/drugs/drug-alerts-and-statements/"
                    "fda-warns-against-purchasing-or-using-chemical-peel-skin-products-"
                    "without-professional-supervision"
                ),
            },
            {
                "title": "Chemical peels: Preparation",
                "publisher": "American Academy of Dermatology",
                "url": (
                    "https://www.aad.org/public/cosmetic/younger-looking/"
                    "chemical-peels-preparation"
                ),
            },
            {
                "title": "Chemical peels: FAQs",
                "publisher": "American Academy of Dermatology",
                "url": (
                    "https://www.aad.org/public/cosmetic/younger-looking/"
                    "chemical-peels-faqs"
                ),
            },
        ),
    },
)
