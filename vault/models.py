from django.contrib.auth.models import User
# from django.contrib.auth.hashers import make_password, check_password  # FIX FOR FLAW 2 (uncomment)
from django.db import models


class Note(models.Model):
    KIND_CHOICES = [("note", "Private note"), ("expense", "Expense")]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default="note")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.owner})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # FLAW 2 (A02:2021 Cryptographic Failures): the backup PIN is stored in plaintext.
    backup_pin = models.CharField(max_length=128, blank=True)

    # Failed-attempt counters used by FIX FOR FLAW 4 (lockout).
    failed_logins = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    def set_pin(self, raw_pin):
        # FLAW 2 (A02:2021 Cryptographic Failures): the PIN goes into the database as-is.
        self.backup_pin = raw_pin  # [vulnerable]
        # FIX FOR FLAW 2: store a salted PBKDF2 hash instead of the plaintext PIN.
        # self.backup_pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        if not self.backup_pin:
            return False
        # FLAW 2 (A02:2021): the PIN is verified by comparing plaintext strings.
        return self.backup_pin == raw_pin  # [vulnerable]
        # FIX FOR FLAW 2: verify against the hash.
        # return check_password(raw_pin, self.backup_pin)

    def __str__(self):
        return f"Profile({self.user})"
