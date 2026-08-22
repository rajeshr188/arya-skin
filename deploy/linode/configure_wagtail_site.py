import os

from wagtail.models import Site


hostname = os.environ["STAGING_HOST"]
site = Site.objects.get(is_default_site=True)
site.hostname = hostname
site.port = 443
site.site_name = "Dr. Naresh Rathod staging"
site.save(update_fields=["hostname", "port", "site_name"])
print(site.root_url)
