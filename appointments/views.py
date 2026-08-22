import time

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_http_methods

from clinics.models import ClinicPage

from .forms import AppointmentEnquiryForm, new_form_token


RATE_LIMIT_SESSION_KEY = "appointment_submission_times"


def _public_clinic(slug):
    if not slug:
        return None
    return ClinicPage.objects.live().public().filter(slug=slug).first()


def _is_rate_limited(request):
    now = time.time()
    window = settings.APPOINTMENT_SUBMISSION_WINDOW_SECONDS
    timestamps = [
        value
        for value in request.session.get(RATE_LIMIT_SESSION_KEY, [])
        if value > now - window
    ]
    request.session[RATE_LIMIT_SESSION_KEY] = timestamps
    return len(timestamps) >= settings.APPOINTMENT_SUBMISSION_LIMIT


def _record_submission(request):
    timestamps = request.session.get(RATE_LIMIT_SESSION_KEY, [])
    timestamps.append(time.time())
    request.session[RATE_LIMIT_SESSION_KEY] = timestamps


@sensitive_post_parameters("name", "phone", "email")
@never_cache
@require_http_methods(["GET", "POST"])
def appointment_request(request, clinic_slug=None):
    fixed_clinic = _public_clinic(clinic_slug)
    if clinic_slug and not fixed_clinic:
        raise Http404
    if not fixed_clinic and not ClinicPage.objects.live().public().exists():
        raise Http404

    if request.method == "POST":
        form = AppointmentEnquiryForm(request.POST, clinic=fixed_clinic)
        if _is_rate_limited(request):
            form.add_error(
                None,
                "Too many requests have been submitted. Please try again later.",
            )
        elif form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.clinic = fixed_clinic or form.cleaned_data["clinic"]
            enquiry.clinic_name = enquiry.clinic.title
            enquiry.source_path = request.path[:255]
            enquiry.save()
            _record_submission(request)
            request.session["appointment_request_submitted"] = True
            request.session["appointment_request_clinic_slug"] = enquiry.clinic.slug
            return redirect("appointments:success")
    else:
        form = AppointmentEnquiryForm(
            clinic=fixed_clinic,
            initial={"form_token": new_form_token()},
        )

    response = render(
        request,
        "appointments/appointment_form.html",
        {"form": form, "clinic": fixed_clinic},
    )
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


@require_GET
@never_cache
def appointment_success(request):
    if not request.session.pop("appointment_request_submitted", False):
        return redirect("/")
    clinic_slug = request.session.pop("appointment_request_clinic_slug", "")
    response = render(
        request,
        "appointments/appointment_success.html",
        {"analytics_clinic_slug": clinic_slug},
    )
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response
