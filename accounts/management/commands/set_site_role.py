from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.workos_client import workos_client

User = get_user_model()


class Command(BaseCommand):
    help = "Set a user's admin/member permission via WorkOS metadata (dashboard can't edit it directly)."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("role", choices=["", "member", "admin"])

    def handle(self, email, role, **options):
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise CommandError(f"No local user with email {email}")

        workos_user_id = user.profile.workos_user_id
        if not workos_user_id:
            raise CommandError(f"{email} has never logged in via WorkOS yet (no workos_user_id).")

        workos_client.user_management.update_user(id=workos_user_id, metadata={"site_role": role})

        user.profile.site_role = role
        user.profile.save(update_fields=["site_role"])

        self.stdout.write(self.style.SUCCESS(f"{email} site_role set to {role!r}"))
