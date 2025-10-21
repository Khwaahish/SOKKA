from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    help = 'Clear all active sessions (logout all users)'

    def handle(self, *args, **options):
        count = Session.objects.all().count()
        Session.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleared {count} session(s). All users have been logged out.')
        )

