from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


RICH_TEXT_FEATURES = [
    "h2",
    "h3",
    "bold",
    "italic",
    "ol",
    "ul",
    "link",
]


class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(max_length=160)
    level = blocks.ChoiceBlock(choices=[("h2", "Heading 2"), ("h3", "Heading 3")])

    class Meta:
        icon = "title"
        template = "blocks/heading.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(
        max_length=255,
        help_text="Describe the meaningful content of the image.",
    )
    caption = blocks.CharBlock(max_length=255, required=False)

    class Meta:
        icon = "image"
        template = "blocks/image.html"


class ImageTextBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(max_length=255)
    heading = blocks.CharBlock(max_length=160)
    text = blocks.RichTextBlock(features=RICH_TEXT_FEATURES)
    image_position = blocks.ChoiceBlock(
        choices=[("left", "Image left"), ("right", "Image right")],
        default="left",
    )

    class Meta:
        icon = "image"
        template = "blocks/image_text.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(max_length=500)
    attribution = blocks.CharBlock(max_length=160, required=False)

    class Meta:
        icon = "openquote"
        template = "blocks/quote.html"


class FAQItemBlock(blocks.StructBlock):
    question = blocks.CharBlock(max_length=255)
    answer = blocks.RichTextBlock(
        features=["bold", "italic", "ol", "ul", "link"]
    )


class FAQBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=160, default="Frequently asked questions")
    items = blocks.ListBlock(FAQItemBlock(), min_num=1, max_num=12)

    class Meta:
        icon = "help"
        template = "blocks/faq.html"


class CallToActionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=160)
    text = blocks.TextBlock(max_length=400, required=False)
    label = blocks.CharBlock(max_length=60)
    internal_page = blocks.PageChooserBlock(required=False)
    external_url = blocks.URLBlock(required=False)

    def clean(self, value):
        cleaned = super().clean(value)
        if bool(cleaned.get("internal_page")) == bool(cleaned.get("external_url")):
            raise blocks.StructBlockValidationError(
                non_block_errors=[
                    "Choose exactly one destination: an internal page or an external URL."
                ]
            )
        return cleaned

    class Meta:
        icon = "link"
        template = "blocks/call_to_action.html"


class DoctorAdviceBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=160, default="Doctor's advice")
    text = blocks.RichTextBlock(features=["bold", "italic", "ol", "ul", "link"])

    class Meta:
        icon = "user"
        template = "blocks/doctor_advice.html"


class InformationBlock(blocks.StructBlock):
    style = blocks.ChoiceBlock(
        choices=[
            ("information", "Information"),
            ("warning", "Warning"),
        ],
        default="information",
    )
    heading = blocks.CharBlock(max_length=160)
    text = blocks.RichTextBlock(features=["bold", "italic", "ol", "ul", "link"])

    class Meta:
        icon = "warning"
        template = "blocks/information.html"


class ContentStreamBlock(blocks.StreamBlock):
    heading = HeadingBlock()
    rich_text = blocks.RichTextBlock(
        features=RICH_TEXT_FEATURES,
        template="blocks/rich_text.html",
    )
    image = ImageBlock()
    image_text = ImageTextBlock()
    quote = QuoteBlock()
    faq = FAQBlock()
    call_to_action = CallToActionBlock()
    doctor_advice = DoctorAdviceBlock()
    information = InformationBlock()

    class Meta:
        block_counts = {
            "call_to_action": {"max_num": 3},
            "doctor_advice": {"max_num": 4},
        }
