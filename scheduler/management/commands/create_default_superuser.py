import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Create (or update) a superuser from environment variables, without needing
    interactive input or shell access. Safe to run on every deploy: if the user
    already exists it just makes sure they're still staff/superuser and leaves
    the password alone.

    Reads:
        DJANGO_SUPERUSER_USERNAME
        DJANGO_SUPERUSER_EMAIL
        DJANGO_SUPERUSER_PASSWORD

    If any of these are missing, the command does nothing (so local dev without
    these vars set isn't affected).
    """

    help = "Create a default superuser from DJANGO_SUPERUSER_* environment variables if one doesn't exist yet."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD not set — skipping superuser creation."
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": True, "is_superuser": True},
        )

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        else:
            # Already exists — just make sure permissions are correct.
            # Password is intentionally left alone so a later manual change isn't overwritten on redeploy.
            changed = False
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if changed:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated permissions for existing user '{username}'."))
            else:
                self.stdout.write(f"Superuser '{username}' already exists — nothing to do.")
