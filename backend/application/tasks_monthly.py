# backend/application/tasks_monthly.py
# Scheduled Job (b): monthly placement activity report for the admin (HTML email + PDF).
from datetime import datetime
from app import celery
from flask import current_app as app, render_template

from application.models import (
    db, User, CompanyProfile, PlacementDrive, Application,
    DriveStatus, ApplicationStatus, ApprovalStatus,
)
from application.mail_helper import send_email
from application.chart_helper import generate_bar_chart
from application.pdf_helper import generate_monthly_report_pdf


def _month_bounds(year=None, month=None):
    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    return start, end


def latest_activity_month():
    """(year, month) of the most recent month that actually has portal activity.

    The admin's monthly panel used to hard-default to the current calendar month,
    which reads as a broken page ("0 / 0 / 0 / 0, no top companies") on any day
    before the month's first drive or application lands. Defaulting to the newest
    month that has data instead means the panel always opens on something useful;
    the admin can still pick any other month manually.

    Falls back to the current month when the portal has no activity at all.
    """
    newest = None
    for value in (
        db.session.query(db.func.max(Application.applied_at)).scalar(),
        db.session.query(db.func.max(PlacementDrive.created_at)).scalar(),
    ):
        if value and (newest is None or value > newest):
            newest = value

    ref = newest or datetime.utcnow()
    return ref.year, ref.month


def build_monthly_report_data(year=None, month=None):
    start, end = _month_bounds(year, month)

    drives_created = PlacementDrive.query.filter(
        PlacementDrive.created_at >= start, PlacementDrive.created_at < end).count()
    drives_conducted = PlacementDrive.query.filter(
        PlacementDrive.status == DriveStatus.APPROVED,
        PlacementDrive.created_at >= start, PlacementDrive.created_at < end).count()

    applications = Application.query.filter(
        Application.applied_at >= start, Application.applied_at < end).all()
    students_applied = len({a.student_id for a in applications})
    students_selected = len({a.student_id for a in applications if a.status == ApplicationStatus.SELECTED})

    companies_onboarded = CompanyProfile.query.filter(
        CompanyProfile.approval_status == ApprovalStatus.APPROVED,
        CompanyProfile.created_at >= start, CompanyProfile.created_at < end).count()

    company_counts = {}
    for a in applications:
        cname = a.drive.company.company_name if a.drive and a.drive.company else "Unknown"
        company_counts[cname] = company_counts.get(cname, 0) + 1
    top_companies = sorted(company_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    top_companies_rows = [
        [name, PlacementDrive.query.join(CompanyProfile).filter(
            CompanyProfile.company_name == name,
            PlacementDrive.created_at >= start, PlacementDrive.created_at < end).count(), count]
        for name, count in top_companies
    ]

    status_breakdown = {s.value: 0 for s in ApplicationStatus}
    for a in applications:
        status_breakdown[a.status.value] += 1

    now = datetime.utcnow()
    return {
        "period": start.strftime("%B %Y"),
        "year": start.year,
        "month": start.month,
        "is_current_month": (start.year, start.month) == (now.year, now.month),
        "generated_at": now.strftime("%Y-%m-%d %H:%M UTC"),
        "drives_created": drives_created,
        "drives_conducted": drives_conducted,
        "applications_count": len(applications),
        "students_applied": students_applied,
        "students_selected": students_selected,
        "companies_onboarded": companies_onboarded,
        "top_companies": top_companies_rows,
        "status_breakdown": status_breakdown,
    }


@celery.task(name="application.tasks_monthly.send_monthly_report")
def send_monthly_report(year=None, month=None):
    data = build_monthly_report_data(year, month)

    chart_path, chart_rel = None, None
    if any(data["status_breakdown"].values()):
        chart_path, chart_rel = generate_bar_chart(
            {k.replace("_", " ").title(): v for k, v in data["status_breakdown"].items()},
            title=f"Applications by status — {data['period']}", filename_prefix="monthly")

    pdf_path, pdf_rel = generate_monthly_report_pdf(data, chart_path=chart_path)

    try:
        html_body = render_template("emails/monthly_report.html", data=data,
                                     chart_url=(f"cid:chart" if chart_path else None))
    except Exception:
        html_body = f"<h2>Monthly report — {data['period']}</h2><pre>{data}</pre>"

    admin_user = User.query.join(User.roles).filter_by(name="admin").first()
    sent = False
    if admin_user and admin_user.email:
        sent = send_email(admin_user.email, f"Monthly placement activity report — {data['period']}",
                           html_body, html=True, attachment_path=pdf_path)

    app.logger.info(f"[MonthlyReport] generated for {data['period']}, emailed={sent}")
    return {"status": "ok", "period": data["period"], "emailed": sent,
            "pdf_path": pdf_rel, "chart_path": chart_rel, "data": data}
