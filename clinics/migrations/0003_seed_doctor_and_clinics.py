from django.db import migrations


def seed_doctor_and_clinics(apps, schema_editor):
    from wagtail.models import Page

    from clinics.models import ClinicIndexPage, ClinicPage
    from doctors.models import (
        DoctorLanguage,
        DoctorPage,
        DoctorQualification,
        DoctorRegistration,
        DoctorSpecialty,
    )

    home = Page.objects.filter(
        content_type__app_label="website", content_type__model="homepage"
    ).first()
    if not home:
        return

    doctor = DoctorPage.objects.first()
    if not doctor:
        doctor = DoctorPage(
            title="Dr. Naresh Rathod",
            slug="dr-naresh-rathod",
            professional_title="Dermatologist and Cosmetologist",
            seo_title="Dr. Naresh Rathod - Dermatologist and Cosmetologist",
            search_description=(
                "Professional profile of Dr. Naresh Rathod, dermatologist and "
                "cosmetologist practising in Sitapura and Chaksu, Jaipur."
            ),
            live=False,
            has_unpublished_changes=True,
            show_in_menus=True,
            locale_id=home.locale_id,
        )
        home.add_child(instance=doctor)

        DoctorQualification.objects.create(
            page=doctor,
            qualification="MBBS",
            institution=(
                "Jhalawar Medical College, Jhalawar, Rajasthan, India"
            ),
            sort_order=0,
        )
        DoctorQualification.objects.create(
            page=doctor,
            qualification="PGCCD",
            institution=(
                "Indian Association of Dermatologists, Venereologists and "
                "Cosmetologists"
            ),
            sort_order=1,
        )
        DoctorRegistration.objects.create(
            page=doctor,
            authority="Rajasthan Medical Council",
            registration_number="C-6523",
            registration_year=2008,
            sort_order=0,
        )
        for sort_order, specialty in enumerate(
            ["Skin", "Nail", "Hair", "Cosmetology"]
        ):
            DoctorSpecialty.objects.create(
                page=doctor, name=specialty, sort_order=sort_order
            )
        for sort_order, language in enumerate(["Hindi", "English", "Marwari"]):
            DoctorLanguage.objects.create(
                page=doctor, name=language, sort_order=sort_order
            )
        doctor.save_revision()

    clinic_index = ClinicIndexPage.objects.first()
    if not clinic_index:
        clinic_index = ClinicIndexPage(
            title="Clinics",
            slug="clinics",
            seo_title="Clinics where Dr. Naresh Rathod practises in Jaipur",
            search_description=(
                "Clinic locations for Dr. Naresh Rathod in Sitapura and Chaksu, "
                "Jaipur."
            ),
            live=False,
            has_unpublished_changes=True,
            show_in_menus=True,
            locale_id=home.locale_id,
        )
        home.add_child(instance=clinic_index)
        clinic_index.save_revision()

    clinic_records = [
        {
            "title": "Dolphin Derma Care",
            "slug": "sitapura",
            "locality": "Sitapura",
            "address": "Above Apni Pharmacy, Main India Gate, Tonk Road",
            "postal_code": "302022",
            "phone": "9461289316",
            "whatsapp": "9461289316",
            "seo_title": "Dolphin Derma Care, Sitapura - Dr. Naresh Rathod",
            "search_description": (
                "Dolphin Derma Care in Sitapura, Jaipur, where Dr. Naresh "
                "Rathod practises. Contact details remain unpublished pending "
                "confirmation."
            ),
        },
        {
            "title": "Arya Skin and Hair Clinic",
            "slug": "chaksu",
            "locality": "Chaksu",
            "address": "",
            "postal_code": "302027",
            "phone": "9461289316",
            "whatsapp": "9461289316",
            "seo_title": "Arya Skin and Hair Clinic, Chaksu - Dr. Naresh Rathod",
            "search_description": (
                "Arya Skin and Hair Clinic in Chaksu, Jaipur, where Dr. Naresh "
                "Rathod practises. Full address and hours remain unpublished "
                "pending confirmation."
            ),
        },
    ]

    for record in clinic_records:
        if ClinicPage.objects.filter(slug=record["slug"]).exists():
            continue
        clinic = ClinicPage(
            title=record["title"],
            slug=record["slug"],
            locality=record["locality"],
            city="Jaipur",
            state="Rajasthan",
            address=record["address"],
            postal_code=record["postal_code"],
            phone=record["phone"],
            phone_is_public=False,
            whatsapp=record["whatsapp"],
            whatsapp_is_public=False,
            doctor=doctor,
            seo_title=record["seo_title"],
            search_description=record["search_description"],
            live=False,
            has_unpublished_changes=True,
            locale_id=home.locale_id,
        )
        clinic_index.add_child(instance=clinic)
        clinic.save_revision()

class Migration(migrations.Migration):
    dependencies = [
        ("clinics", "0002_initial"),
        ("doctors", "0001_initial"),
        ("website", "0003_reframe_site_identity"),
    ]

    operations = [
        migrations.RunPython(seed_doctor_and_clinics, migrations.RunPython.noop)
    ]
