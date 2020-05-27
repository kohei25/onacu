from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username="acunico").exists():
            User.objects.create_superuser(username="acunico", email="email@email.com", password="acunico0826")
            self.stdout.write(self.style.SUCCESS('Successfully created new super user'))