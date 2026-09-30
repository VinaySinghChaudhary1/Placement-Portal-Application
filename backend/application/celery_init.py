# backend/application/celery_init.py
import sys
from pathlib import Path
from celery import Celery, Task


def celery_init_app(app) -> Celery:
    base_dir = Path(__file__).resolve().parents[1]
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.import_name, task_cls=FlaskTask)
    celery_app.config_from_object("celery_config")
    celery_app.autodiscover_tasks(["application"])
    app.extensions["celery"] = celery_app
    return celery_app
