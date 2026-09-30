# backend/application/tasks_reminder.py
# Scheduled Job (a): daily reminders to students about upcoming application deadlines.
from datetime import datetime, timedelta
from app import celery
from flask import current_app as app, render_template

from application.models import db, PlacementDrive, StudentProfile, DriveStatus, Notification, SystemSetting
from application.mail_helper import send_email, send_gchat_webhook


@celery.task(name="application.tasks_reminder.send_deadline_reminders")
def send_deadline_reminders(window_days=None):
    window = int(window_days or SystemSetting.get_value(
        "daily_reminder_window_days", app.config.get("DAILY_REMINDER_WINDOW_DAYS", 3)))
    now = datetime.utcnow()
    cutoff = now + timedelta(days=window)

    drives = PlacementDrive.query.filter(
        PlacementDrive.status == DriveStatus.APPROVED,
        PlacementDrive.application_deadline >= now,
        PlacementDrive.application_deadline <= cutoff,
    ).all()

    students = StudentProfile.query.filter_by(blacklisted=False).all()
    reminders_sent = 0

    for drive in drives:
        already_applied_ids = {a.student_id for a in drive.applications}
        for student in students:
            if student.id in already_applied_ids:
                continue
            eligible, _ = drive.is_eligible(student)
            if not eligible:
                continue
            if not student.user or not student.user.email:
                continue

            days_left = (drive.application_deadline - now).days
            subject = f"Reminder: '{drive.job_title}' application closes soon"
            try:
                body = render_template("emails/deadline_reminder.html", student=student, drive=drive,
                                        days_left=max(days_left, 0))
            except Exception:
                body = (f"Hi {student.full_name}, the application deadline for "
                        f"'{drive.job_title}' at {drive.company.company_name} is "
                        f"{drive.application_deadline.strftime('%Y-%m-%d %H:%M')}. Apply soon!")
            send_email(student.user.email, subject, body, html=True)
            send_gchat_webhook(
                f"Reminder for {student.full_name}: '{drive.job_title}' closes on "
                f"{drive.application_deadline.strftime('%Y-%m-%d %H:%M')}.")
            db.session.add(Notification(
                user_id=student.user_id, title="Deadline reminder",
                message=f"'{drive.job_title}' at {drive.company.company_name} closes on "
                        f"{drive.application_deadline.strftime('%Y-%m-%d %H:%M')}.",
                type="reminder"))
            reminders_sent += 1

    db.session.commit()
    app.logger.info(f"[DailyReminders] sent {reminders_sent} reminder(s) for {len(drives)} drive(s)")
    return {"status": "ok", "reminders_sent": reminders_sent, "drives_checked": len(drives)}
