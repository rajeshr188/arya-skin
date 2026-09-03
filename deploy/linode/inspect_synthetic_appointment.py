import os

from appointments.models import AppointmentEnquiry


SYNTHETIC_NAME = "Automated Notification Acceptance"

enquiries = AppointmentEnquiry.objects.filter(
    name=SYNTHETIC_NAME,
    phone="9999999999",
    email="",
    source_path="/appointments/request/sitapura/",
    clinic__slug="sitapura",
)
enquiry_count = enquiries.count()
print(f"synthetic_enquiries={enquiry_count}")

delivery_counts = {}
for enquiry in enquiries:
    for delivery in enquiry.notification_deliveries.all():
        delivery_counts[delivery.status] = delivery_counts.get(delivery.status, 0) + 1
for status in ("pending", "retrying", "sent"):
    print(f"synthetic_deliveries_{status}={delivery_counts.get(status, 0)}")

if os.environ.get("DELETE_SYNTHETIC_APPOINTMENT") == "1":
    unsent_count = sum(
        count
        for status, count in delivery_counts.items()
        if status != "sent"
    )
    if enquiry_count != 1 or unsent_count:
        raise RuntimeError(
            "Refusing cleanup unless exactly one synthetic enquiry exists and all "
            "of its notifications are sent."
        )
    deleted, _ = enquiries.delete()
    print(f"synthetic_objects_deleted={deleted}")
