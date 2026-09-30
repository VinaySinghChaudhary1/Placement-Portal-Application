# backend/application/pdf_helper.py
# Well-designed PDF version of the monthly activity report (optional/recommended feature).
import os
from datetime import datetime
from flask import current_app as app
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_monthly_report_pdf(report_data: dict, chart_path: str = None):
    export_dir = os.path.join(app.static_folder, "exports", "reports")
    os.makedirs(export_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"monthly_report_{ts}.pdf"
    filepath = os.path.join(export_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#0d6efd"))

    story = [
        Paragraph("Placement Portal — Monthly Activity Report", title_style),
        Paragraph(f"Period: {report_data['period']}", styles["Normal"]),
        Paragraph(f"Generated: {report_data['generated_at']}", styles["Normal"]),
        Spacer(1, 0.6 * cm),
    ]

    summary_rows = [
        ["Metric", "Value"],
        ["Drives conducted (approved)", report_data["drives_conducted"]],
        ["New drives created", report_data["drives_created"]],
        ["Students who applied", report_data["students_applied"]],
        ["Applications received", report_data["applications_count"]],
        ["Students selected", report_data["students_selected"]],
        ["Companies onboarded", report_data["companies_onboarded"]],
    ]
    table = Table(summary_rows, colWidths=[9 * cm, 6 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5ff")]),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.8 * cm))

    if chart_path and os.path.exists(chart_path):
        story.append(Paragraph("Drive status breakdown", styles["Heading3"]))
        story.append(Image(chart_path, width=15 * cm, height=7.5 * cm))
        story.append(Spacer(1, 0.6 * cm))

    if report_data.get("top_companies"):
        story.append(Paragraph("Top companies by applications received", styles["Heading3"]))
        rows = [["Company", "Drives", "Applications"]] + report_data["top_companies"]
        t2 = Table(rows, colWidths=[7 * cm, 4 * cm, 4 * cm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#198754")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(t2)

    doc.build(story)
    return filepath, f"exports/reports/{filename}"
