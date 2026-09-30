# backend/celery_config.py
import os

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

timezone = "Asia/Kolkata"
enable_utc = False
broker_connection_retry_on_startup = True

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

beat_scheduler = "application.dynamic_scheduler:DynamicDatabaseScheduler"
beat_schedule_filename = "celerybeat-schedule"
beat_max_loop_interval = 10
