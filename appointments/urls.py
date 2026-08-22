from django.urls import path

from . import views


app_name = "appointments"

urlpatterns = [
    path("request/", views.appointment_request, name="request"),
    path(
        "request/<slug:clinic_slug>/",
        views.appointment_request,
        name="request_for_clinic",
    ),
    path("received/", views.appointment_success, name="success"),
]
