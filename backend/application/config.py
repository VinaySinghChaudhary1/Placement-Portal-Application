# backend/application/config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class LocalDevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "placement.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask, the Celery worker and Celery beat each open their own connection to the
    # same SQLite file. A generous busy timeout avoids spurious "database is locked"
    # errors when two of them write at almost the same moment (e.g. on first boot).
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"timeout": 15}}

    SECRET_KEY = "placement-portal-secret-key"
    SECURITY_PASSWORD_SALT = "placement-portal-salt"
    SECURITY_PASSWORD_HASH = "argon2"

    # Token based auth (Authentication-Token header) - no session cookies needed for the SPA
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_TOKEN_MAX_AGE = 60 * 60 * 8  # 8 hours

    # Flask-Security-Too misc
    SECURITY_REGISTERABLE = False   # we roll our own register endpoints (student / company)
    SECURITY_RECOVERABLE = False
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = False
    SECURITY_CSRF_PROTECT_MECHANISMS = []
    WTF_CSRF_ENABLED = False

    # Caching (Redis)
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/2")
    CACHE_DEFAULT_TIMEOUT = 60

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "resumes")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx"}

    # Business rules (used by seed data + scheduled jobs, editable via SystemSetting)
    DAILY_REMINDER_HOUR = 9
    DAILY_REMINDER_MINUTE = 0
    DAILY_REMINDER_WINDOW_DAYS = 3   # remind students about drives whose deadline is within N days
    MONTHLY_REPORT_DAY = 1
    MONTHLY_REPORT_HOUR = 6
    MONTHLY_REPORT_MINUTE = 0

    # Mail (local dev SMTP debugging server, e.g. MailHog or `python -m smtpd`)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 1025))
    SENDER_ADDRESS = "no-reply@placement-portal.local"

    # Google Chat webhook (optional, used by daily reminder job if configured)
    GCHAT_WEBHOOK_URL = os.environ.get("GCHAT_WEBHOOK_URL", "")
