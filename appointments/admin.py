from django.contrib import admin
from django.utils import timezone

from .models import AppointmentEnquiry


@admin.register(AppointmentEnquiry)
class AppointmentEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "name",
        "clinic_name",
        "preferred_date",
        "time_preference",
        "status",
    )
    list_filter = ("status", "clinic", "time_preference", "created_at")
    search_fields = ("name", "phone", "email", "clinic_name", "reference")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    readonly_fields = (
        "reference",
        "clinic",
        "clinic_name",
        "name",
        "phone",
        "email",
        "preferred_date",
        "time_preference",
        "consent_to_contact",
        "consent_version",
        "source_path",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Request",
            {
                "fields": (
                    "reference",
                    "clinic",
                    "clinic_name",
                    "name",
                    "phone",
                    "email",
                    "preferred_date",
                    "time_preference",
                )
            },
        ),
        ("Workflow", {"fields": ("status", "staff_note")}),
        (
            "Consent and source",
            {
                "fields": (
                    "consent_to_contact",
                    "consent_version",
                    "source_path",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    actions = ("mark_contacted", "mark_closed", "mark_spam")

    def has_add_permission(self, request):
        return False

    @admin.action(description="Mark selected enquiries as contacted")
    def mark_contacted(self, request, queryset):
        queryset.update(
            status=AppointmentEnquiry.Status.CONTACTED,
            updated_at=timezone.now(),
        )

    @admin.action(description="Mark selected enquiries as closed")
    def mark_closed(self, request, queryset):
        queryset.update(
            status=AppointmentEnquiry.Status.CLOSED,
            updated_at=timezone.now(),
        )

    @admin.action(description="Mark selected enquiries as spam")
    def mark_spam(self, request, queryset):
        queryset.update(
            status=AppointmentEnquiry.Status.SPAM,
            updated_at=timezone.now(),
        )
