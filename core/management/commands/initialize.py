from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from wagtail.models import Page
from wagtail.core.models import Site
from dotenv import dotenv_values


class Command(BaseCommand):
    def handle(self, *args, **options):

        if not User.objects.filter(username="admin").exists():
            user = User.objects.create(
                username="admin",
                email="admin@girolabs.com",
                is_active=True,
                is_staff=True,
                is_superuser=True,
            )
            user.set_password("Cuaderno.1")
            user.save()
            self.stdout.write(f"Se creó el usuario: {user.username}")
            self.stdout.write(f"Con password: Cuaderno.1")

        page = Page.objects.filter(title="Welcome to your new Wagtail site!")
        if page.exists():
            page = page.first()
            page.title = "Base"
            page.unpublish()
            page.save_revision().publish()
            page.save_revision()

        config = dotenv_values(".env")
        ADMIN_BASE_URL = config.get("ADMIN_BASE_URL", "http://127.0.0.1:8000").split(
            ":"
        )
        domain = ADMIN_BASE_URL[1][2:]
        port = ADMIN_BASE_URL[2]

        site = Site.objects.first()
        site.site_name = settings.WAGTAIL_SITE_NAME
        if domain:
            site.hostname = domain
        if port:
            site.port = port
        site.save()
