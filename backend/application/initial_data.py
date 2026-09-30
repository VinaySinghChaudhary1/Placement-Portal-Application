# backend/application/initial_data.py
# Creates the DB schema + the ONE pre-existing admin (no admin registration route exists)
# plus a little demo data so the app is immediately explorable after first boot.
#
# NOTE: this runs once from the Flask process AND once from every Celery worker/beat
# process (they all import app.py to get a configured app + celery instance). If two
# of these start at almost the same moment on a brand-new database, they can race on
# the same INSERT. Every block below is wrapped so a duplicate-insert race just backs
# off instead of crashing the process that lost the race.
from datetime import datetime, timedelta, date
from flask import current_app as app
from flask_security.utils import hash_password
from sqlalchemy.exc import IntegrityError

from application.models import (
    db, Role, User, StudentProfile, CompanyProfile, PlacementDrive, Application,
    ApprovalStatus, DriveStatus, ApplicationStatus,
)


def _safe(step_fn):
    """Run a seeding step; on a concurrent-insert race, roll back and move on."""
    try:
        step_fn()
    except IntegrityError:
        db.session.rollback()
    except Exception:
        db.session.rollback()
        app.logger.exception("initial_data seeding step failed")


def initialize_data():
    with app.app_context():
        db.create_all()
        datastore = app.security.datastore

        def _seed_roles():
            for role_name, desc in [("admin", "Institute placement cell"),
                                     ("company", "Recruiting organisation"),
                                     ("student", "Student / candidate")]:
                if not datastore.find_role(role_name):
                    datastore.create_role(name=role_name, description=desc)
            db.session.commit()
        _safe(_seed_roles)

        # --- the ONE admin -------------------------------------------------
        def _seed_admin():
            if not datastore.find_user(email="admin@placement.edu"):
                datastore.create_user(
                    username="admin",
                    email="admin@placement.edu",
                    password=hash_password("Admin@123"),
                    fs_uniquifier="fs-admin-0001",
                    roles=["admin"],
                )
                db.session.commit()
        _safe(_seed_admin)

        # --- demo companies --------------------------------------------------
        def _seed_technova():
            if not datastore.find_user(email="hr@technova.com"):
                u = datastore.create_user(
                    username="technova_hr",
                    email="hr@technova.com",
                    password=hash_password("Company@123"),
                    fs_uniquifier="fs-company-0001",
                    roles=["company"],
                )
                db.session.commit()
                db.session.add(CompanyProfile(
                    user_id=u.id, company_name="TechNova Solutions",
                    hr_contact_name="Riya Sharma", hr_email="hr@technova.com",
                    website="https://technova.example.com",
                    description="A product company building developer tooling.",
                    industry="Information Technology",
                    approval_status=ApprovalStatus.APPROVED,
                ))
                db.session.commit()
        _safe(_seed_technova)

        def _seed_finedge():
            if not datastore.find_user(email="hr@finedge.com"):
                u2 = datastore.create_user(
                    username="finedge_hr",
                    email="hr@finedge.com",
                    password=hash_password("Company@123"),
                    fs_uniquifier="fs-company-0002",
                    roles=["company"],
                )
                db.session.commit()
                db.session.add(CompanyProfile(
                    user_id=u2.id, company_name="FinEdge Analytics",
                    hr_contact_name="Karan Mehta", hr_email="hr@finedge.com",
                    website="https://finedge.example.com",
                    description="Fintech analytics platform, hiring across engineering & data roles.",
                    industry="Financial Technology",
                    approval_status=ApprovalStatus.PENDING,
                ))
                db.session.commit()
        _safe(_seed_finedge)

        # --- demo students -----------------------------------------------
        def _seed_asha():
            if not datastore.find_user(email="asha.rao@student.edu"):
                u3 = datastore.create_user(
                    username="asha_rao",
                    email="asha.rao@student.edu",
                    password=hash_password("Student@123"),
                    fs_uniquifier="fs-student-0001",
                    roles=["student"],
                )
                db.session.commit()
                db.session.add(StudentProfile(
                    user_id=u3.id, full_name="Asha Rao", branch="Computer Science",
                    year=2026, cgpa=8.7, phone="9876543210",
                ))
                db.session.commit()
        _safe(_seed_asha)

        def _seed_vikram():
            if not datastore.find_user(email="vikram.j@student.edu"):
                u4 = datastore.create_user(
                    username="vikram_j",
                    email="vikram.j@student.edu",
                    password=hash_password("Student@123"),
                    fs_uniquifier="fs-student-0002",
                    roles=["student"],
                )
                db.session.commit()
                db.session.add(StudentProfile(
                    user_id=u4.id, full_name="Vikram Joshi", branch="Electronics",
                    year=2026, cgpa=7.4, phone="9876500000",
                ))
                db.session.commit()
        _safe(_seed_vikram)

        # --- demo drive (approved, open) ----------------------------------
        def _seed_drive():
            company = CompanyProfile.query.filter_by(company_name="TechNova Solutions").first()
            if company and not PlacementDrive.query.filter_by(job_title="Software Development Engineer").first():
                drive = PlacementDrive(
                    company_id=company.id,
                    job_title="Software Development Engineer",
                    job_description="Work on backend services in Python/Flask and REST APIs.",
                    eligible_branches="Computer Science,Information Technology",
                    eligible_years="2026",
                    min_cgpa=7.0,
                    salary_package=12.5,
                    location="Bengaluru",
                    application_deadline=datetime.utcnow() + timedelta(days=10),
                    status=DriveStatus.APPROVED,
                )
                db.session.add(drive)
                db.session.commit()

                asha = StudentProfile.query.join(User).filter(User.email == "asha.rao@student.edu").first()
                if asha:
                    db.session.add(Application(student_id=asha.id, drive_id=drive.id,
                                                status=ApplicationStatus.APPLIED))
                    db.session.commit()
        _safe(_seed_drive)

        # --- default schedule settings ------------------------------------
        def _seed_settings():
            from application.models import SystemSetting

            def ensure_default(key, value, desc=None):
                if SystemSetting.get_value(key) is None:
                    SystemSetting.set_value(key, value, description=desc)

            ensure_default("daily_reminder_hour", app.config.get("DAILY_REMINDER_HOUR", 9))
            ensure_default("daily_reminder_minute", app.config.get("DAILY_REMINDER_MINUTE", 0))
            ensure_default("daily_reminder_window_days", app.config.get("DAILY_REMINDER_WINDOW_DAYS", 3))
            ensure_default("monthly_report_day", app.config.get("MONTHLY_REPORT_DAY", 1))
            ensure_default("monthly_report_hour", app.config.get("MONTHLY_REPORT_HOUR", 6))
            ensure_default("monthly_report_minute", app.config.get("MONTHLY_REPORT_MINUTE", 0))
        _safe(_seed_settings)
