# backend/application/tasks_export.py
# Scheduled Job (c): user-triggered async export of a student's application history as CSV.
import os
import csv
import time
from datetime import datetime
from app import celery
from flask import current_app as app

from application.models import db, StudentProfile, CompanyProfile, User, Notification
from application.mail_helper import send_email


@celery.task(name="application.tasks_export.generate_application_csv")
def generate_application_csv(student_id):
    try:
        export_dir = os.path.join(app.static_folder, "exports", "csv")
        os.makedirs(export_dir, exist_ok=True)

        student = StudentProfile.query.get(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"student_{student_id}_applications_{ts}.csv"
        filepath = os.path.join(export_dir, filename)

        headers = ["student_id", "company_name", "drive_title", "application_status",
                   "applied_date", "last_updated_date"]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for a in student.applications:
                writer.writerow([
                    student.id,
                    a.drive.company.company_name if a.drive and a.drive.company else "",
                    a.drive.job_title if a.drive else "",
                    a.status.value if a.status else "",
                    a.applied_at.strftime("%Y-%m-%d %H:%M") if a.applied_at else "",
                    a.updated_at.strftime("%Y-%m-%d %H:%M") if a.updated_at else "",
                ])

        # simulate a bit of processing time so the async nature is visible in the UI/demo
        time.sleep(1)

        rel_path = f"exports/csv/{filename}"
        db.session.add(Notification(
            user_id=student.user_id, title="CSV export ready",
            message="Your placement application history export is ready to download.",
            type="export_ready", link=f"/api/exports/csv/{filename}",
        ))
        db.session.commit()

        if student.user and student.user.email:
            send_email(student.user.email, "Your application export is ready",
                        f"Hi {student.full_name},\n\nYour CSV export of {len(student.applications)} "
                        f"application(s) is ready. Download it from your dashboard.\n\nRegards,\nPlacement Portal")

        return filename
    except Exception:
        app.logger.exception(f"generate_application_csv failed for student {student_id}")
        raise


@celery.task(name="application.tasks_export.generate_company_report_csv")
def generate_company_report_csv(company_id):
    try:
        export_dir = os.path.join(app.static_folder, "exports", "csv")
        os.makedirs(export_dir, exist_ok=True)

        company = CompanyProfile.query.get(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found")

        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"company_{company_id}_report_{ts}.csv"
        filepath = os.path.join(export_dir, filename)

        headers = ["drive_title", "drive_status", "application_deadline", "student_name",
                   "student_email", "branch", "cgpa", "application_status", "applied_date"]
        row_count = 0
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for drive in company.drives:
                if not drive.applications:
                    writer.writerow([
                        drive.job_title, drive.status.value if drive.status else "",
                        drive.application_deadline.strftime("%Y-%m-%d") if drive.application_deadline else "",
                        "", "", "", "", "", "",
                    ])
                    row_count += 1
                    continue
                for a in drive.applications:
                    writer.writerow([
                        drive.job_title,
                        drive.status.value if drive.status else "",
                        drive.application_deadline.strftime("%Y-%m-%d") if drive.application_deadline else "",
                        a.student.full_name if a.student else "",
                        a.student.user.email if a.student and a.student.user else "",
                        a.student.branch if a.student else "",
                        a.student.cgpa if a.student else "",
                        a.status.value if a.status else "",
                        a.applied_at.strftime("%Y-%m-%d %H:%M") if a.applied_at else "",
                    ])
                    row_count += 1

        time.sleep(1)

        rel_path = f"exports/csv/{filename}"
        db.session.add(Notification(
            user_id=company.user_id, title="CSV export ready",
            message="Your placement drives & applicants export is ready to download.",
            type="export_ready", link=f"/api/exports/csv/{filename}",
        ))
        db.session.commit()

        if company.user and company.user.email:
            send_email(company.user.email, "Your placement report export is ready",
                        f"Hi {company.company_name},\n\nYour CSV export covering {row_count} "
                        f"drive/applicant row(s) is ready. Download it from your dashboard.\n\nRegards,\nPlacement Portal")

        return filename
    except Exception:
        app.logger.exception(f"generate_company_report_csv failed for company {company_id}")
        raise


@celery.task(name="application.tasks_export.generate_admin_export_csv")
def generate_admin_export_csv(admin_user_id):
    """Portal-wide export for the admin: every student, every company, every
    drive, and every application, as one CSV split into labelled sections
    (a single sheet keeps this consistent with the student/company exports,
    which are also plain CSV rather than multi-sheet workbooks)."""
    try:
        export_dir = os.path.join(app.static_folder, "exports", "csv")
        os.makedirs(export_dir, exist_ok=True)

        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            raise ValueError(f"Admin user {admin_user_id} not found")

        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"admin_portal_export_{ts}.csv"
        filepath = os.path.join(export_dir, filename)

        students = StudentProfile.query.order_by(StudentProfile.full_name).all()
        companies = CompanyProfile.query.order_by(CompanyProfile.company_name).all()
        drives = [d for c in companies for d in c.drives]
        drives.sort(key=lambda d: (d.company.company_name if d.company else "", d.job_title))
        applications = [a for d in drives for a in d.applications]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow([f"PLACEMENT PORTAL — FULL DATA EXPORT ({datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')})"])
            writer.writerow([])

            writer.writerow([f"STUDENTS ({len(students)})"])
            writer.writerow(["student_id", "full_name", "email", "branch", "year", "cgpa",
                              "phone", "blacklisted", "blacklist_reason", "registered_on"])
            for s in students:
                writer.writerow([
                    s.id, s.full_name, s.user.email if s.user else "", s.branch, s.year, s.cgpa,
                    s.phone or "", "yes" if s.blacklisted else "no", s.blacklist_reason or "",
                    s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
                ])
            writer.writerow([])

            writer.writerow([f"COMPANIES ({len(companies)})"])
            writer.writerow(["company_id", "company_name", "hr_contact_name", "hr_email", "hr_phone",
                              "industry", "approval_status", "blacklisted", "blacklist_reason", "registered_on"])
            for c in companies:
                writer.writerow([
                    c.id, c.company_name, c.hr_contact_name or "", c.hr_email or "", c.hr_phone or "",
                    c.industry or "", c.approval_status.value if c.approval_status else "",
                    "yes" if c.blacklisted else "no", c.blacklist_reason or "",
                    c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "",
                ])
            writer.writerow([])

            writer.writerow([f"PLACEMENT DRIVES ({len(drives)})"])
            writer.writerow(["drive_id", "company_name", "job_title", "status", "min_cgpa",
                              "salary_lpa", "location", "application_deadline", "applicant_count", "created_on"])
            for d in drives:
                writer.writerow([
                    d.id, d.company.company_name if d.company else "", d.job_title,
                    d.status.value if d.status else "", d.min_cgpa,
                    d.salary_package if d.salary_package is not None else "", d.location or "",
                    d.application_deadline.strftime("%Y-%m-%d %H:%M") if d.application_deadline else "",
                    len(d.applications),
                    d.created_at.strftime("%Y-%m-%d %H:%M") if d.created_at else "",
                ])
            writer.writerow([])

            writer.writerow([f"APPLICATIONS ({len(applications)})"])
            writer.writerow(["application_id", "student_name", "student_email", "company_name",
                              "drive_title", "status", "applied_on", "last_updated"])
            for a in applications:
                writer.writerow([
                    a.id, a.student.full_name if a.student else "",
                    a.student.user.email if a.student and a.student.user else "",
                    a.drive.company.company_name if a.drive and a.drive.company else "",
                    a.drive.job_title if a.drive else "", a.status.value if a.status else "",
                    a.applied_at.strftime("%Y-%m-%d %H:%M") if a.applied_at else "",
                    a.updated_at.strftime("%Y-%m-%d %H:%M") if a.updated_at else "",
                ])

        time.sleep(1)

        db.session.add(Notification(
            user_id=admin_user.id, title="Portal export ready",
            message=f"Your full data export ({len(students)} students, {len(companies)} companies, "
                    f"{len(drives)} drives, {len(applications)} applications) is ready to download.",
            type="export_ready", link=f"/api/exports/csv/{filename}",
        ))
        db.session.commit()

        if admin_user.email:
            send_email(admin_user.email, "Your portal data export is ready",
                        f"Hi,\n\nYour full placement portal export is ready: {len(students)} students, "
                        f"{len(companies)} companies, {len(drives)} drives, {len(applications)} applications.\n\n"
                        f"Download it from your admin dashboard.\n\nRegards,\nPlacement Portal")

        return filename
    except Exception:
        app.logger.exception(f"generate_admin_export_csv failed for admin {admin_user_id}")
        raise
