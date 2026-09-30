# backend/application/report_utils.py
# Small shared helpers for the "Summary/Reports" chart pages (student, company, admin).
# Deliberately simple Python-side bucketing rather than SQL date-trunc functions —
# the data volumes in this app are small (a placement cell demo dataset), so this
# stays fast while working identically regardless of the underlying DB.
from datetime import datetime
from calendar import month_abbr


def last_n_months(n=6, end=None):
    """Return the last n (year, month) tuples in ascending order, ending at `end`
    (defaults to the current month)."""
    end = end or datetime.utcnow()
    months = []
    y, m = end.year, end.month
    for _ in range(n):
        months.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    months.reverse()
    return months


def month_key(year, month):
    return f"{year:04d}-{month:02d}"


def month_label(year, month):
    return f"{month_abbr[month]} {year}"


def bucket_by_month(dates, n=6):
    """Given an iterable of datetime objects, return a list of
    {month, label, count} covering the last n months (oldest first), including
    months with zero activity so line/bar charts don't have gaps."""
    counts = {}
    for d in dates:
        if not d:
            continue
        key = month_key(d.year, d.month)
        counts[key] = counts.get(key, 0) + 1

    result = []
    for y, m in last_n_months(n):
        key = month_key(y, m)
        result.append({"month": key, "label": month_label(y, m), "count": counts.get(key, 0)})
    return result
