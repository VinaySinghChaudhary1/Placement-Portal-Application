# Placement Portal Application

A campus placement portal for an institute's placement cell, built for the IIT-M
App Dev II (MAD-II) project. Three roles: **Admin** (pre-seeded, no registration),
**Company** (self-register, needs admin approval before posting drives), and
**Student** (self-register, applies to approved drives).

Stack: **Flask** (REST API) + **Flask-Security-Too** (auth) · **VueJS 3** (SPA UI,
built with Vite) + **Bootstrap 5** · **SQLite** (via SQLAlchemy, created
programmatically) · **Redis** (caching) · **Redis + Celery** (scheduled/async jobs).

## Folder structure

```
placement-portal/
  backend/
    application/        # models, routes, celery tasks, helpers
    static/              # uploaded resumes + generated exports/reports/charts
    templates/emails/     # HTML email templates
    app.py                # Flask app factory + celery init + blueprint registration
    celery_config.py
    requirements.txt
  frontend/
    src/{views,components,router,store,services,assets}
    package.json
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis server running locally on `localhost:6379`
- A local SMTP debug server on `localhost:1025` for viewing emails. Two options:
  - **[MailHog](https://github.com/mailhog/MailHog)** (recommended) — runs an SMTP
    listener on port **1025** (matches this project's config, no changes needed)
    *and* a web inbox at **`http://localhost:8025`** — open that URL in your
    browser to see emails, not `:1025` itself (`:1025` is the raw SMTP protocol
    port, a browser can't render it — that's an `ERR_INVALID_HTTP_RESPONSE`, not
    a bug).
  - **`aiosmtpd`** — a no-install-extras fallback that just prints emails as text
    in its own terminal (no web page):
    ```bash
    pip install aiosmtpd
    python -m aiosmtpd -n -l localhost:1025
    ```
    (the older built-in `smtpd` module was removed in Python 3.12, so use
    `aiosmtpd` instead if you're on Python 3.12+)

## 1. Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The SQLite database, tables, the one admin account, and a little demo data are
created automatically the first time the app starts (`application/initial_data.py`) —
there is no manual DB setup step.

**Demo accounts** (also created automatically):

| Role    | Email                     | Password     |
|---------|---------------------------|--------------|
| Admin   | admin@placement.edu       | Admin@123    |
| Company | hr@technova.com           | Company@123  |
| Company | hr@finedge.com (pending)  | Company@123  |
| Student | asha.rao@student.edu      | Student@123  |
| Student | vikram.j@student.edu      | Student@123  |

## 2. Run everything (4 terminals)

```bash
# Terminal 1 — Redis
redis-server

# Terminal 2 — SMTP debug server
MailHog                                    # then open http://localhost:8025 to view emails
# or: python -m aiosmtpd -n -l localhost:1025   (emails print in this terminal instead)

# Terminal 3 — Flask API (http://127.0.0.1:5000)
cd backend && source .venv/bin/activate
python app.py

# Terminal 4 — Celery worker (runs the async CSV export job)
cd backend && source .venv/bin/activate
celery -A app.celery worker --loglevel=INFO --pool=solo

# Terminal 5 (optional) — Celery beat (runs the daily reminder + monthly report on schedule)
cd backend && source .venv/bin/activate
celery -A app.celery beat --loglevel=INFO
```

`--pool=solo` is the simplest option on Windows; on macOS/Linux you can drop it.
Terminal 5 is only needed to see the *scheduled* jobs fire automatically — you can
also trigger both jobs on demand from Admin → Reports in the UI, which works even
without `celery beat` running.

## 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (default `http://localhost:8080`). The frontend talks to
the backend at `http://127.0.0.1:5000` by default — override with a `.env` file
(see `.env.example`) if your backend runs elsewhere.

## Backend jobs implemented

- **Daily reminders** (`application/tasks_reminder.py`) — finds students eligible
  for approved drives whose deadline is within N days (admin-configurable under
  Settings) who haven't applied yet, and emails them (Google Chat webhook is also
  wired up if `GCHAT_WEBHOOK_URL` is set).
- **Monthly activity report** (`application/tasks_monthly.py`) — on the 1st of
  every month (configurable), emails the admin an HTML report with a chart and a
  PDF attachment (`application/pdf_helper.py`, `application/chart_helper.py`).
- **CSV export** (`application/tasks_export.py`) — triggered from the student
  dashboard, runs as an async Celery task, writes a CSV under
  `backend/static/exports/csv/`, and creates an in-app notification + email once done.

Both scheduled jobs can also be run on demand from **Admin → Reports** without
waiting for the schedule, which is the easiest way to demo them.

## Public pages: design system

The public-facing pages — **Home**, **Login**, **Register (student/company)**,
**Contact**, and the shared **Navbar**/**Footer** — use a small motion-driven
design system layered on top of Bootstrap 5. Logged-in dashboard pages
(admin/company/student) are intentionally untouched by this: it's additive,
namespaced CSS, not a global restyle.

- `frontend/src/assets/styles/motion.css` — gradient/shadow/radius tokens,
  hero/blob/card/button styles, all under a `.pp-*` prefix so nothing collides
  with existing Bootstrap or dashboard classes.
- `frontend/src/directives/reveal.js` — a `v-reveal` Vue directive (optionally
  `v-reveal="1"`–`v-reveal="4"` for a staggered delay) that fades/slides an
  element in once it scrolls into view, via a single `IntersectionObserver`.
  No animation library was added on purpose — this keeps `npm install`
  untouched and avoids adding a render-heavy 3D engine for what is, underneath,
  a college placement portal. `prefers-reduced-motion: reduce` disables all of
  it for users who've asked their OS for less motion.
- **Contact page** (`/contact`) — new public route with a message form. Update
  the placeholder email/phone/address in `Footer.vue` and `Contact.vue` with
  the real placement cell details before sharing this outside a local demo.

## Contact form endpoint

`POST /api/contact` (public, no login required — see Security notes below) validates
name/email/message, emails the seeded admin account via the existing SMTP setup,
and falls back to an in-app `Notification` if mail delivery fails. It has its own
abuse guards since it's the one endpoint in the app that doesn't require a token:
a per-IP rate limit (5 messages / 15 minutes, in-memory — resets on backend restart),
a honeypot field, and email format/length validation (`email-validator`, already
in `requirements.txt`).

## Troubleshooting

**`ModuleNotFoundError: No module named 'pkg_resources'`** (on `python app.py` or
`celery -A app.celery worker`) — `pip install -r requirements.txt` pulled in a
setuptools version >= 82, which removed `pkg_resources` that `passlib` (a
Flask-Security-Too dependency) still needs. Fixed in `requirements.txt` (pins
`setuptools<82`) — if you installed before this fix, just run:
```bash
pip install "setuptools<82" --force-reinstall
```
then re-run `python app.py`.

**Redis: `Could not create server TCP listening socket *:6379: bind: Address
already in use`** — this means a Redis server is *already* running (often
auto-started by WSL/your OS). That's fine — you don't need to start another one.
Confirm with `redis-cli ping` (should reply `PONG`) and just skip Terminal 1.

**`python -m smtpd`: `No module named 'smtpd'`** — the `smtpd` module was
removed in Python 3.12. Use MailHog or `aiosmtpd` instead (see Prerequisites/
Terminal 2 above). If you'd rather not install anything, you can skip the SMTP
server entirely — the app catches mail-send failures and keeps working
(registrations, approvals, applications, etc. all still succeed), you just
won't see the emails.

**Browser error `ERR_INVALID_HTTP_RESPONSE` when opening `http://127.0.0.1:1025`**
— that port is the raw SMTP protocol port the *backend* sends mail to, not a
webpage. If you're using MailHog, its inbox webpage is on a different port —
open **`http://localhost:8025`** instead. If you're using `aiosmtpd`, there's
no web page at all; emails just print as text in the terminal it's running in.

**`OSError: address already in use` on port 1025 (or Redis on 6379)** — something
is already listening there, most likely a MailHog/aiosmtpd instance (or Redis)
left running from an earlier attempt. That's not an error to fix — just reuse
it (or `lsof -i :1025` / `redis-cli ping` to confirm what's already up and skip
starting a second one).

**Celery `Unable to load celery application`** — this error's own traceback
always points to the *real* underlying exception a few lines up (in the report
you shared, it was the same `pkg_resources` issue above). Fix the root exception
shown in the traceback and Celery will load fine — the `app.celery` reference
itself is correct.

## Notes

- Caching: approved-drives listings and the admin dashboard stats are cached in
  Redis (`Flask-Caching`) with short TTLs, and busted on any relevant mutation
  (approve/reject/blacklist).
- The database file lives at `backend/instance/placement.sqlite3` and is created
  fresh on first run — delete it (with the app stopped) to reset all data.

## Security notes

- **Auth is token-based, not cookie-based** — the SPA stores the
  `Authentication-Token` Flask-Security issues on login and sends it as a
  header on every request (`frontend/src/services/api.js`). There are no
  session cookies to steal via CSRF, which is why `WTF_CSRF_ENABLED = False`
  is safe here — CSRF tokens exist to protect cookie-based sessions.
- **CORS is locked to the known dev origins** (`http://localhost:8080` /
  `127.0.0.1:8080`) in `app.py` — not a wildcard. Update this list (and the
  frontend's `VITE_API_URL`) if you ever deploy somewhere else.
- **Every dashboard route is role-gated twice**: once client-side (Vue Router
  `beforeEach` in `frontend/src/router/index.js`, redirects unauthenticated or
  wrong-role users before a page even renders) and again server-side
  (`@role_required("admin"/"company"/"student")` on every API route) — the
  client-side check is a UX nicety, the server-side one is the real boundary.
- **File exports are ownership-checked**: `/api/exports/<path>` only serves a
  file if a `Notification` proves it belongs to the requesting user, so one
  account can't download another's CSV export by guessing a filename.
- **The new `/api/contact` endpoint is the one deliberate exception** to "every
  route requires a token" — see "Contact form endpoint" above for its specific
  guards (rate limit, honeypot, validated email, stripped control characters
  before anything reaches an email header).
- **Before any real deployment** (this project ships configured for local dev
  only): move `SECRET_KEY` and `SECURITY_PASSWORD_SALT` in
  `application/config.py` out of source and into environment variables, put
  the app behind HTTPS, and set `SESSION_COOKIE_SECURE`/`PREFERRED_URL_SCHEME`
  accordingly. None of this is needed to run the project locally for the
  MAD-II submission, but it's not production-hardened as committed.
