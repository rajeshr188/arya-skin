from django.contrib import admin
from django.utils import timezone

from .models import AppointmentEnquiry, AppointmentNotificationDelivery


@admin.register(AppointmentEnquiry)
class AppointmentEnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "name",
        "clinic_name",
        "preferred_date",
        "time_preference",
        "status",
        "notification_status",
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
        "notification_status",
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
        ("Notification", {"fields": ("notification_status",)}),
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

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            "notification_deliveries"
        )

    def has_add_permission(self, request):
        return False

    @admin.display(description="Email notification")
    def notification_status(self, enquiry):
        deliveries = list(enquiry.notification_deliveries.all())
        if not deliveries:
            return "Not queued"
        counts = {
            status: sum(delivery.status == status for delivery in deliveries)
            for status in AppointmentNotificationDelivery.Status.values
        }
        return ", ".join(
            f"{label}: {counts[value]}"
            for value, label in AppointmentNotificationDelivery.Status.choices
            if counts[value]
        )

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
