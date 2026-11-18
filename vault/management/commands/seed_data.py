from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from vault.models import Note, Profile

USERS = {
    # username: (password, backup pin)
    "alice": ("redqueen", "4821"),
    "bob": ("builder", "1593"),
}

NOTES = {
    "alice": [
        ("note", "Bank recovery codes", "Savings account recovery code: 7731-AAQ-9920", None),
        ("expense", "Rent November", "Paid by bank transfer", "850.00"),
        ("expense", "Groceries", "Weekly shop", "62.40"),
    ],
    "bob": [
        ("note", "Wi-Fi and alarm codes", "Router admin: hunter2 / Alarm code: 0420", None),
        ("expense", "Laptop repair", "Screen replacement", "129.99"),
        ("note", "Secret gift idea", "Surprise trip for the anniversary", None),
    ],
}


class Command(BaseCommand):
    help = "Create demo users (alice, bob) and a few private entries."

    def handle(self, *args, **options):
        for username, (password, pin) in USERS.items():
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.set_pin(pin)
                profile.save()
                for kind, title, content, amount in NOTES[username]:
                    Note.objects.create(owner=user, kind=kind, title=title,
                                        content=content, amount=amount)
                self.stdout.write(f"Created {username} / {password} (PIN {pin})")
            else:
                self.stdout.write(f"{username} already exists, skipped")
