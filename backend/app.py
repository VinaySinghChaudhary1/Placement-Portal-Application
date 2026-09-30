# backend/app.py
import os
from flask import Flask
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore

from application.models import db, User, Role
from application.config import LocalDevelopmentConfig
from application.cache import cache
from application.celery_init import celery_init_app


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(LocalDevelopmentConfig)
    os.makedirs(os.path.dirname(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    cache.init_app(app)
    app.config.setdefault("beat_scheduler", "application.dynamic_scheduler.DynamicDatabaseScheduler")

    db.init_app(app)

    CORS(app, supports_credentials=True, expose_headers=["Authentication-Token"],
         origins=["http://localhost:8080", "http://127.0.0.1:8080"])

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore=datastore, register_blueprint=False)

    @app.security.unauthn_handler
    def unauthn_handler(mechanisms, headers=None):
        return {"message": "Authentication required. Please log in."}, 401

    @app.security.unauthz_handler
    def unauthz_handler(func_name, params):
        return {"message": "You don't have access to this resource."}, 403

    app.app_context().push()
    return app


app = create_app()

celery = celery_init_app(app)

# Celery tasks must be imported so `celery.autodiscover_tasks` / worker registration sees them.
import application.tasks_reminder      # noqa: E402,F401
import application.tasks_monthly       # noqa: E402,F401
import application.tasks_export        # noqa: E402,F401

from application.initial_data import initialize_data  # noqa: E402
initialize_data()

from application.routes_auth import auth_bp        # noqa: E402
from application.routes_admin import admin_bp       # noqa: E402
from application.routes_company import company_bp   # noqa: E402
from application.routes_student import student_bp   # noqa: E402
from application.routes_common import common_bp      # noqa: E402

for bp in (auth_bp, admin_bp, company_bp, student_bp, common_bp):
    app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
