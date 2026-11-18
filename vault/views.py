"""SecureVault views - Created by Pablo Landos (Cyber Security Base, Course Project I).

Five OWASP Top 10 (2021) flaws are active by default. Each has its fix directly below it as
commented-out code labelled "# FIX FOR FLAW X". Search this file for "FLAW" to find them all.
"""
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.password_validation import validate_password  # FIX FOR FLAW 4
# from django.core.exceptions import ValidationError                     # FIX FOR FLAW 4
from django.contrib.auth.models import User
from django.db import connection
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Note, Profile

audit = logging.getLogger("security")

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 5


# ---------------------------------------------------------------- helpers

def client_ip(request):
    return request.META.get("REMOTE_ADDR", "unknown")


def _profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def _is_locked(user):
    profile = _profile(user)
    return bool(profile.locked_until and profile.locked_until > timezone.now())


def _register_failure(user):
    profile = _profile(user)
    profile.failed_logins += 1
    if profile.failed_logins >= MAX_FAILED_ATTEMPTS:
        profile.locked_until = timezone.now() + timedelta(minutes=LOCKOUT_MINUTES)
        profile.failed_logins = 0
    profile.save()


def _reset_failures(user):
    profile = _profile(user)
    profile.failed_logins = 0
    profile.locked_until = None
    profile.save()


def _password_problem(user, password):
    """Return an error string if the password is unacceptable, otherwise None."""
    # FLAW 4 (A07:2021): no password strength check, so "a" is accepted.
    return None  # [vulnerable]
    # FIX FOR FLAW 4: run the validators enabled in settings.AUTH_PASSWORD_VALIDATORS.
    # try:
    #     validate_password(password, user)
    # except ValidationError as exc:
    #     return " ".join(exc.messages)
    # return None


def _audit_foreign_access(request, note_id, action):
    """Log an attempt to touch a note that belongs to somebody else."""
    if Note.objects.filter(id=note_id).exclude(owner=request.user).exists():
        audit.warning("ACCESS_DENIED user=%s ip=%s action=%s note_id=%s",
                      request.user.username, client_ip(request), action, note_id)


# ---------------------------------------------------------------- accounts

def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "That username is taken.")
        else:
            problem = _password_problem(User(username=username), password)
            if problem:
                messages.error(request, problem)
            else:
                user = User.objects.create_user(username=username, password=password)
                _profile(user)
                login(request, user)
                return redirect("index")
    return render(request, "vault/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        # FLAW 4 (A07:2021): unlimited login attempts, there is no lockout at all.
        # FIX FOR FLAW 4: refuse locked accounts before even checking the password.
        # target = User.objects.filter(username=username).first()
        # if target and _is_locked(target):
        #     audit.warning("LOGIN_BLOCKED_LOCKED user=%s ip=%s", username, client_ip(request))
        #     messages.error(request, "Account temporarily locked. Try again in 5 minutes.")
        #     return render(request, "vault/login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # FIX FOR FLAW 4: a successful login clears the failure counter.
            # _reset_failures(user)
            login(request, user)
            return redirect("index")

        # FLAW 5 (A09:2021): failed logins are silently ignored, nothing is logged.
        pass  # [vulnerable]
        # FIX FOR FLAW 5: write a WARNING audit record (timestamp comes from the formatter).
        # audit.warning("LOGIN_FAILED user=%s ip=%s action=login", username, client_ip(request))
        # FIX FOR FLAW 4: count the failure so the account locks after 5 wrong passwords.
        # if target:
        #     _register_failure(target)
        messages.error(request, "Invalid username or password.")
    return render(request, "vault/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def reset_password(request):
    """Reset a password with the username plus the 4-digit backup PIN."""
    if request.method == "POST":
        username = request.POST.get("username", "")
        pin = request.POST.get("pin", "")
        new_password = request.POST.get("new_password", "")
        target = User.objects.filter(username=username).first()

        # FLAW 4 (A07:2021): unlimited PIN guesses, so a 4-digit PIN falls to brute force.
        # FIX FOR FLAW 4: block the endpoint while the account is locked.
        # if target and _is_locked(target):
        #     audit.warning("RESET_BLOCKED_LOCKED user=%s ip=%s", username, client_ip(request))
        #     messages.error(request, "Account temporarily locked. Try again in 5 minutes.")
        #     return render(request, "vault/reset.html")

        if target and _profile(target).check_pin(pin):
            problem = _password_problem(target, new_password)
            if problem:
                messages.error(request, problem)
            else:
                target.set_password(new_password)
                target.save()
                # FIX FOR FLAW 4: clear the counter after a legitimate reset.
                # _reset_failures(target)
                messages.success(request, "Password updated. You can now log in.")
                return redirect("login")
        else:
            # FLAW 5 (A09:2021): wrong PIN guesses are not logged.
            pass  # [vulnerable]
            # FIX FOR FLAW 5: log every failed reset attempt.
            # audit.warning("RESET_FAILED user=%s ip=%s action=reset_password",
            #               username, client_ip(request))
            # FIX FOR FLAW 4: count the failed PIN guess.
            # if target:
            #     _register_failure(target)
            messages.error(request, "Wrong username or PIN.")
    return render(request, "vault/reset.html")


@login_required
def security_settings(request):
    profile = _profile(request.user)
    if request.method == "POST":
        if "pin" in request.POST:
            pin = request.POST.get("pin", "")
            if pin.isdigit() and len(pin) == 4:
                profile.set_pin(pin)
                profile.save()
                messages.success(request, "Backup PIN saved.")
            else:
                messages.error(request, "The PIN must be exactly 4 digits.")
        elif "new_password" in request.POST:
            new_password = request.POST.get("new_password", "")
            problem = _password_problem(request.user, new_password)
            if problem:
                messages.error(request, problem)
            else:
                request.user.set_password(new_password)
                request.user.save()
                login(request, request.user)
                messages.success(request, "Password changed.")
        return redirect("security_settings")

    # FLAW 2 (A02:2021): the stored PIN is shown exactly as it sits in the database.
    pin_display = profile.backup_pin  # [vulnerable]
    # FIX FOR FLAW 2: the PIN is hashed, so only show whether one is set.
    # pin_display = "(stored as a salted PBKDF2 hash)" if profile.backup_pin else ""
    return render(request, "vault/settings.html", {"pin_display": pin_display})


# ---------------------------------------------------------------- notes

@login_required
def index(request):
    notes = Note.objects.filter(owner=request.user).order_by("-created")
    total = sum(n.amount for n in notes if n.amount)
    return render(request, "vault/index.html", {"notes": notes, "total": total})


@login_required
def add_note(request):
    if request.method == "POST":
        amount = request.POST.get("amount", "").strip()
        try:
            amount = amount or None
            note = Note.objects.create(
                owner=request.user,
                kind=request.POST.get("kind", "note"),
                title=request.POST.get("title", "")[:200] or "Untitled",
                content=request.POST.get("content", ""),
                amount=amount,
            )
        except Exception:
            messages.error(request, "Invalid amount.")
            return render(request, "vault/note_form.html")
        return redirect("note_detail", note_id=note.id)
    return render(request, "vault/note_form.html")


@login_required
def note_detail(request, note_id):
    # FIX FOR FLAW 5: log the attempt when somebody opens a note they do not own.
    # _audit_foreign_access(request, note_id, "view")

    # FLAW 1 (A01:2021 Broken Access Control / IDOR): the note is fetched by id only, so any
    # logged-in user can read anyone's note by changing the number in the URL.
    note = get_object_or_404(Note, id=note_id)  # [vulnerable]
    # FIX FOR FLAW 1: only return the note if it belongs to the current user.
    # note = get_object_or_404(Note, id=note_id, owner=request.user)
    return render(request, "vault/note_detail.html", {"note": note})


@login_required
@require_POST
def delete_note(request, note_id):
    # FIX FOR FLAW 5: log the attempt when somebody deletes a note they do not own.
    # _audit_foreign_access(request, note_id, "delete")

    # FLAW 1 (A01:2021 Broken Access Control / IDOR): any user can delete any note by id.
    note = get_object_or_404(Note, id=note_id)  # [vulnerable]
    # FIX FOR FLAW 1: restrict the lookup to the current user's notes.
    # note = get_object_or_404(Note, id=note_id, owner=request.user)

    # FLAW 5 (A09:2021): deletions leave no audit trail.
    pass  # [vulnerable]
    # FIX FOR FLAW 5: record who deleted what.
    # audit.warning("NOTE_DELETED user=%s ip=%s action=delete note_id=%s owner=%s",
    #               request.user.username, client_ip(request), note.id, note.owner.username)
    note.delete()
    messages.success(request, "Entry deleted.")
    return redirect("index")


@login_required
def search(request):
    query = request.GET.get("q", "")
    results, error = [], None
    if query:
        # FLAW 3 (A03:2021 Injection): user input is formatted straight into the SQL string.
        # Try q = ' OR 1=1 --   to dump every user's notes.
        sql = (f"SELECT id, title, content, owner_id FROM vault_note "  # [vulnerable]
               f"WHERE owner_id = {request.user.id} AND title LIKE '%{query}%'")  # [vulnerable]
        # FIX FOR FLAW 3: a parameterised query; the driver escapes the values.
        # sql = ("SELECT id, title, content, owner_id FROM vault_note "
        #        "WHERE owner_id = %s AND title LIKE %s")
        # params = [request.user.id, f"%{query}%"]
        # (the ORM equivalent is Note.objects.filter(owner=request.user, title__icontains=query))
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)  # [vulnerable]
                # FIX FOR FLAW 3: pass the parameters separately.
                # cursor.execute(sql, params)
                results = [dict(zip(("id", "title", "content", "owner_id"), row))
                           for row in cursor.fetchall()]
        except Exception as exc:
            error = f"Search failed: {exc}"
    return render(request, "vault/search.html",
                  {"query": query, "results": results, "error": error})
