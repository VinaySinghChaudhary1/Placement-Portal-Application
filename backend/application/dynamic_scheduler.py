# backend/application/dynamic_scheduler.py
# Lets the admin change the daily-reminder / monthly-report schedule at runtime
# (stored in SystemSetting) without restarting `celery beat`.
import logging
from celery.beat import Scheduler, ScheduleEntry
from celery.schedules import crontab
from flask import current_app as flask_app
from application.models import SystemSetting

logger = logging.getLogger("DynamicScheduler")

DAILY_TASK = "application.tasks_reminder.send_deadline_reminders"
MONTHLY_TASK = "application.tasks_monthly.send_monthly_report"


class DynamicDatabaseScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        self._last_daily = None
        self._last_monthly = None
        self._initialized = False
        super().__init__(*args, **kwargs)

    def setup_schedule(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        logger.info("[DynamicScheduler] initialized")

    def get_schedule(self):
        try:
            return super().get_schedule()
        except Exception:
            return getattr(self._store, "entries", {}) or {}

    def _find_entry(self, task_name):
        for key, entry in self.get_schedule().items():
            if getattr(entry, "task", None) == task_name:
                return key, entry
        return None, None

    def _load_daily(self):
        app = flask_app._get_current_object()
        h = int(SystemSetting.get_value("daily_reminder_hour", app.config.get("DAILY_REMINDER_HOUR", 9)))
        m = int(SystemSetting.get_value("daily_reminder_minute", app.config.get("DAILY_REMINDER_MINUTE", 0)))
        w = int(SystemSetting.get_value("daily_reminder_window_days", app.config.get("DAILY_REMINDER_WINDOW_DAYS", 3)))
        return h, m, w

    def _load_monthly(self):
        app = flask_app._get_current_object()
        day = int(SystemSetting.get_value("monthly_report_day", app.config.get("MONTHLY_REPORT_DAY", 1)))
        hour = int(SystemSetting.get_value("monthly_report_hour", app.config.get("MONTHLY_REPORT_HOUR", 6)))
        minute = int(SystemSetting.get_value("monthly_report_minute", app.config.get("MONTHLY_REPORT_MINUTE", 0)))
        return day, hour, minute

    def _refresh_daily(self):
        hour, minute, window = self._load_daily()
        new = (hour, minute, window)
        if new == self._last_daily:
            return
        self._last_daily = new
        _, entry = self._find_entry(DAILY_TASK)
        if not entry:
            self.schedule[DAILY_TASK] = ScheduleEntry(
                name=DAILY_TASK, task=DAILY_TASK,
                schedule=crontab(hour=hour, minute=minute), args=(window,))
            logger.info(f"[DynamicScheduler] daily reminder scheduled {hour:02d}:{minute:02d} window={window}")
            return
        entry.schedule = crontab(hour=hour, minute=minute)
        entry.args = (window,)

    def _refresh_monthly(self):
        day, hour, minute = self._load_monthly()
        new = (day, hour, minute)
        if new == self._last_monthly:
            return
        self._last_monthly = new
        _, entry = self._find_entry(MONTHLY_TASK)
        if not entry:
            self.schedule[MONTHLY_TASK] = ScheduleEntry(
                name=MONTHLY_TASK, task=MONTHLY_TASK,
                schedule=crontab(day_of_month=day, hour=hour, minute=minute), args=())
            logger.info(f"[DynamicScheduler] monthly report scheduled day={day} {hour:02d}:{minute:02d}")
            return
        entry.schedule = crontab(day_of_month=day, hour=hour, minute=minute)

    def tick(self, *args, **kwargs):
        try:
            self._refresh_daily()
            self._refresh_monthly()
        except Exception:
            logger.exception("DynamicScheduler refresh failed")
        return super().tick(*args, **kwargs)
