from datetime import timedelta

from django import forms
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils import timezone

from clinics.models import ClinicPage

from .models import AppointmentEnquiry


FORM_TOKEN_SALT = "appointments.enquiry-form"
CONSENT_VERSION = "appointment-contact-v1"
CONSENT_TEXT = (
    "I agree that the selected clinic may use these details to contact me about "
    "this appointment request."
)


class AppointmentEnquiryForm(forms.ModelForm):
    clinic = forms.ModelChoiceField(
        queryset=ClinicPage.objects.none(),
        empty_label="Choose a clinic",
    )
    form_token = forms.CharField(widget=forms.HiddenInput)
    website = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
            }
        ),
    )
    consent_to_contact = forms.BooleanField(label=CONSENT_TEXT)

    class Meta:
        model = AppointmentEnquiry
        fields = [
            "clinic",
            "name",
            "phone",
            "email",
            "preferred_date",
            "time_preference",
            "consent_to_contact",
        ]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "name": "Your name",
            "phone": "Phone number",
            "email": "Email address (optional)",
            "preferred_date": "Preferred date",
            "time_preference": "Preferred time",
        }
        help_texts = {
            "preferred_date": "A request is not a confirmed appointment.",
            "time_preference": "Availability will be confirmed by clinic staff.",
        }

    def __init__(self, *args, clinic=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixed_clinic = clinic
        public_clinics = ClinicPage.objects.live().public().order_by("path")
        self.fields["clinic"].queryset = public_clinics
        self.fields["clinic"].widget.attrs["class"] = "form-select"
        for field_name in ("name", "phone", "email", "preferred_date"):
            self.fields[field_name].widget.attrs["class"] = "form-control"
        self.fields["time_preference"].widget.attrs["class"] = "form-select"
        self.fields["consent_to_contact"].widget.attrs["class"] = "form-check-input"
        self.fields["name"].widget.attrs["autocomplete"] = "name"
        self.fields["phone"].widget.attrs["autocomplete"] = "tel"
        self.fields["email"].widget.attrs["autocomplete"] = "email"
        self.fields["preferred_date"].widget.attrs["min"] = (
            timezone.localdate().isoformat()
        )
        self.fields["preferred_date"].widget.attrs["max"] = (
            timezone.localdate() + timedelta(days=180)
        ).isoformat()
        if clinic:
            self.fields["clinic"].initial = clinic
            self.fields["clinic"].widget = forms.HiddenInput()

    def clean_clinic(self):
        clinic = self.cleaned_data.get("clinic")
        if self.fixed_clinic:
            return self.fixed_clinic
        return clinic

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]
        today = timezone.localdate()
        if preferred_date < today:
            raise ValidationError("Choose today or a future date.")
        if preferred_date > today + timedelta(days=180):
            raise ValidationError("Choose a date within the next 180 days.")
        return preferred_date

    def clean_form_token(self):
        token = self.cleaned_data["form_token"]
        try:
            value = signing.loads(token, salt=FORM_TOKEN_SALT, max_age=7200)
        except signing.BadSignature as error:
            raise ValidationError("Please reload the form and try again.") from error
        if value != "appointment-enquiry":
            raise ValidationError("Please reload the form and try again.")
        return token

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise ValidationError("Unable to submit this request.")
        return ""

    def save(self, commit=True):
        enquiry = super().save(commit=False)
        enquiry.consent_version = CONSENT_VERSION
        if commit:
            enquiry.save()
        return enquiry


def new_form_token():
    return signing.dumps("appointment-enquiry", salt=FORM_TOKEN_SALT)
