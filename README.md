# SecureVault - Personal Expense & Note Vault

**Created by Pablo Landos** - Cyber Security Base, Course Project I (OWASP Top 10: 2021).

SecureVault is a small Django app where users register, log in, and keep private notes and
expense entries (create, view, search, delete), plus a security page for a backup PIN and
password. It is **deliberately vulnerable**: five OWASP Top 10 (2021) flaws are active by
default and each has its fix directly below it as commented-out code (`# FIX FOR FLAW X`).
Never deploy it. Only Django is required.

## Run it (Windows, Linux, macOS)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data        # creates alice / redqueen and bob / builder
python manage.py runserver
```

Open http://127.0.0.1:8000/. Demo accounts (PINs are seeded too):

| user  | password   | backup PIN |
|-------|------------|-----------|
| alice | `redqueen` | `4821`    |
| bob   | `builder`  | `1593`    |

To start over: delete `db.sqlite3` and `security.log`, then migrate and seed again.

## The five flaws

Line numbers refer to the committed files.

| # | OWASP 2021 | Flaw (active) | Commented fix |
|---|------------|---------------|---------------|
| 1 | A01 Broken Access Control (IDOR) | [`views.py#L244`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L244) view, [`#L257`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L257) delete | [`#L245-L246`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L245-L246), [`#L258-L259`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L258-L259) |
| 2 | A02 Cryptographic Failures | plaintext PIN: [`models.py#L32`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/models.py#L32), [`#L40`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/models.py#L40); shown in [`views.py#L202`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L202) | [`models.py#L2`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/models.py#L2) (import), [`#L33-L34`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/models.py#L33-L34), [`#L41-L42`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/models.py#L41-L42); [`views.py#L203-L204`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L203-L204) |
| 3 | A03 Injection (SQL) | [`views.py#L278-L279`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L278-L279), [`#L287`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L287) | [`views.py#L280-L284`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L280-L284), [`#L288-L289`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L288-L289) |
| 4 | A07 Identification & Authentication Failures | validators off: [`settings.py#L56-L58`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/securevault/settings.py#L56-L58); no strength check [`views.py#L63-L64`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L63-L64); no lockout [`#L107`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L107) (login), [`#L146`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L146) (PIN reset) | [`settings.py#L60-L66`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/securevault/settings.py#L60-L66); [`views.py#L65-L70`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L65-L70), [`#L108-L113`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L108-L113), [`#L117-L118`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L117-L118), [`#L126-L128`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L126-L128), [`#L147-L152`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L147-L152), [`#L160-L161`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L160-L161), [`#L170-L172`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L170-L172) |
| 5 | A09 Logging & Monitoring Failures | no `LOGGING`: [`settings.py#L79-L80`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/securevault/settings.py#L79-L80); silent: [`views.py#L123`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L123) (login), [`#L166`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L166) (reset), [`#L262`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L262) (delete) | [`settings.py#L82-L100`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/securevault/settings.py#L82-L100); [`views.py#L124-L125`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L124-L125), [`#L167-L169`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L167-L169), [`#L239-L240`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L239-L240), [`#L253-L254`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L253-L254), [`#L263-L265`](https://github.com/Paul1730/Securevault_University-of-Helsinki-and-MOOC/blob/main/vault/views.py#L263-L265) |

### Applying the fixes

For each `# FIX FOR FLAW X` block: uncomment the code under it and delete the matching line(s)
tagged `# [vulnerable]` (or the line directly above the fix). Also uncomment the two imports
in `views.py` (lines 12-13, flaw 4) and the import in `models.py` (line 2, flaw 2). Delete
`db.sqlite3` and re-run `migrate` + `seed_data` after fixing flaw 2, because the seeded PINs
must be hashed. Restart the server.

## Reproducing each flaw (use two logins: alice and bob)

1. **IDOR:** log in as alice, open `/note/<bob's id>/` (bob's notes are ids 4-6). Her browser
   shows bob's note. Posting the Delete button there removes it.
2. **Cryptographic failure:** log in as alice, open `/settings/`: the PIN `4821` is shown in
   plain text (it is also plaintext in `db.sqlite3`: `sqlite3 db.sqlite3 "select backup_pin from vault_profile"`).
3. **SQL injection:** log in as alice, open
   `/search/?q=%27%20OR%201%3D1%20--` (the query `' OR 1=1 --`). Bob's notes appear too
   (owner id 2). The search page also shows raw SQL errors for a lone `'`.
4. **Auth failures:** register a user with the one-character password `a` (accepted). Try 20+
   wrong passwords for `alice` at `/login/`, none are blocked. Brute-force `bob`'s PIN at
   `/reset/` with no limit.
5. **No logging:** after any of the above, `security.log` does not exist and the server
   terminal shows no security events.

## Screenshots (`screenshots/`)

Show the **browser window with the URL bar** or the **server terminal**, never code. Take the
"before" shots with the fixes off and the "after" shots with the fixes on, same steps.

| File | What to capture |
|------|-----------------|
| `flaw-1-before-1.png` | Logged in as alice, URL bar `127.0.0.1:8000/note/4/` showing bob's note |
| `flaw-1-after-1.png` | Same URL after the fix: "Not Found" page (and the terminal's 404 line) |
| `flaw-2-before-1.png` | `/settings/` showing `Current PIN: 4821` |
| `flaw-2-before-2.png` | Terminal: `sqlite3 db.sqlite3 "select user_id, backup_pin from vault_profile"` showing `4821` |
| `flaw-2-after-1.png` | `/settings/` showing "(stored as a salted PBKDF2 hash)"; same sqlite3 command now shows `pbkdf2_sha256$...` |
| `flaw-3-before-1.png` | URL bar `.../search/?q=%27+OR+1%3D1+--` with other users' notes listed |
| `flaw-3-after-1.png` | Same URL after the fix: no results |
| `flaw-4-before-1.png` | Registration succeeding with password `a` (logged-in page, user shown in the navigation bar) |
| `flaw-4-before-2.png` | Login page after 10+ wrong passwords for `alice` in a row, still showing only "Invalid username or password." (no lockout), then a correct login succeeding |
| `flaw-4-after-1.png` | Register page showing "This password is too short..." for `a` |
| `flaw-4-after-2.png` | After 5 wrong passwords: "Account temporarily locked. Try again in 5 minutes." |
| `flaw-5-before-1.png` | Server terminal after several failed logins and a delete: only plain request lines, no security events (and `ls` showing no `security.log`) |
| `flaw-5-after-1.png` | Server terminal showing `WARNING security LOGIN_FAILED user=alice ip=127.0.0.1 ...` lines |
| `flaw-5-after-2.png` | Terminal: `cat security.log` showing the same WARNING lines with timestamps |

Tip: after the fixes, reset the locked account with `rm db.sqlite3 && python manage.py migrate && python manage.py seed_data`.

## Files

```
manage.py
requirements.txt
securevault/{settings,urls,wsgi}.py
vault/{models,views,urls,admin,apps}.py
vault/migrations/0001_initial.py
vault/management/commands/seed_data.py
vault/templates/vault/{base,login,register,reset,index,note_form,note_detail,search,settings}.html
screenshots/
```
