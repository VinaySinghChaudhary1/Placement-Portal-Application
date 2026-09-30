# backend/application/models.py
from datetime import datetime
import enum

from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DriveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"


class ApplicationStatus(enum.Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    SELECTED = "selected"
    REJECTED = "rejected"


class InterviewMode(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class InterviewResult(enum.Enum):
    PENDING = "pending"
    CLEARED = "cleared"
    NOT_CLEARED = "not_cleared"


# ---------------------------------------------------------------------------
# Auth (unified user model, Flask-Security-Too)
# ---------------------------------------------------------------------------

class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"))


class User(db.Model, UserMixin):
    """Unified user model shared by admin / company / student.
    The concrete role is determined by `roles` (Flask-Security RoleMixin)."""
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship("Role", secondary="user_roles",
                             backref=db.backref("users", lazy="dynamic"))
    student_profile = db.relationship("StudentProfile", back_populates="user",
                                       uselist=False, cascade="all, delete-orphan",
                                       passive_deletes=True)
    company_profile = db.relationship("CompanyProfile", back_populates="user",
                                       uselist=False, cascade="all, delete-orphan",
                                       passive_deletes=True)
    notifications = db.relationship("Notification", back_populates="user",
                                     cascade="all, delete-orphan", passive_deletes=True,
                                     order_by="Notification.created_at.desc()")

    def role_name(self):
        return self.roles[0].name if self.roles else None

    def has_role_name(self, name):
        return any(r.name == name for r in self.roles)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

class StudentProfile(db.Model):
    __tablename__ = "student_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"),
                         unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)          # graduation / current year
    cgpa = db.Column(db.Float, nullable=False, default=0.0)
    phone = db.Column(db.String(20), nullable=True)
    resume_path = db.Column(db.String(255), nullable=True)
    resume_filename = db.Column(db.String(255), nullable=True)
    blacklisted = db.Column(db.Boolean, default=False)
    blacklist_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="student_profile")
    applications = db.relationship("Application", back_populates="student",
                                    cascade="all, delete-orphan", passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.user.email if self.user else None,
            "username": self.user.username if self.user else None,
            "active": self.user.active if self.user else None,
            "full_name": self.full_name,
            "branch": self.branch,
            "year": self.year,
            "cgpa": self.cgpa,
            "phone": self.phone,
            "resume_filename": self.resume_filename,
            "has_resume": bool(self.resume_path),
            "blacklisted": self.blacklisted,
            "blacklist_reason": self.blacklist_reason,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }


class CompanyProfile(db.Model):
    __tablename__ = "company_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"),
                         unique=True, nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact_name = db.Column(db.String(150), nullable=True)
    hr_email = db.Column(db.String(120), nullable=True)
    hr_phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    approval_status = db.Column(db.Enum(ApprovalStatus, native_enum=False),
                                 default=ApprovalStatus.PENDING)
    rejection_reason = db.Column(db.String(255), nullable=True)
    blacklisted = db.Column(db.Boolean, default=False)
    blacklist_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="company_profile")
    drives = db.relationship("PlacementDrive", back_populates="company",
                              cascade="all, delete-orphan", passive_deletes=True)

    def to_dict(self, include_counts=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.user.email if self.user else None,
            "username": self.user.username if self.user else None,
            "active": self.user.active if self.user else None,
            "company_name": self.company_name,
            "hr_contact_name": self.hr_contact_name,
            "hr_email": self.hr_email,
            "hr_phone": self.hr_phone,
            "website": self.website,
            "description": self.description,
            "industry": self.industry,
            "approval_status": self.approval_status.value if self.approval_status else None,
            "rejection_reason": self.rejection_reason,
            "blacklisted": self.blacklisted,
            "blacklist_reason": self.blacklist_reason,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }
        if include_counts:
            data["drive_count"] = len(self.drives)
        return data


# ---------------------------------------------------------------------------
# Placement drive & applications
# ---------------------------------------------------------------------------

class PlacementDrive(db.Model):
    __tablename__ = "placement_drive"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profile.id", ondelete="CASCADE"),
                            nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)

    # Eligibility criteria
    eligible_branches = db.Column(db.String(255), nullable=True)   # comma separated, empty = all
    eligible_years = db.Column(db.String(100), nullable=True)      # comma separated, empty = all
    min_cgpa = db.Column(db.Float, nullable=False, default=0.0)

    salary_package = db.Column(db.Float, nullable=True)            # CTC in LPA
    location = db.Column(db.String(150), nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(DriveStatus, native_enum=False), default=DriveStatus.PENDING)
    rejection_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = db.relationship("CompanyProfile", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive",
                                    cascade="all, delete-orphan", passive_deletes=True)

    def branch_list(self):
        return [b.strip() for b in (self.eligible_branches or "").split(",") if b.strip()]

    def year_list(self):
        return [int(y.strip()) for y in (self.eligible_years or "").split(",") if y.strip().isdigit()]

    def is_eligible(self, student: "StudentProfile"):
        if student.blacklisted:
            return False, "You are blacklisted and cannot apply."
        if student.cgpa < self.min_cgpa:
            return False, f"Minimum CGPA required is {self.min_cgpa}."
        branches = self.branch_list()
        if branches and student.branch not in branches:
            return False, "Your branch is not eligible for this drive."
        years = self.year_list()
        if years and student.year not in years:
            return False, "Your graduation year is not eligible for this drive."
        if self.application_deadline and datetime.utcnow() > self.application_deadline:
            return False, "Application deadline has passed."
        if self.status != DriveStatus.APPROVED:
            return False, "This drive is not open for applications."
        return True, None

    def to_dict(self, include_applicant_count=False):
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company.company_name if self.company else None,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "eligible_branches": self.branch_list(),
            "eligible_years": self.year_list(),
            "min_cgpa": self.min_cgpa,
            "salary_package": self.salary_package,
            "location": self.location,
            "application_deadline": self.application_deadline.strftime("%Y-%m-%d %H:%M")
            if self.application_deadline else None,
            "status": self.status.value if self.status else None,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }
        if include_applicant_count:
            data["applicant_count"] = len(self.applications)
        return data


class Application(db.Model):
    __tablename__ = "application"
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),
    )
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profile.id", ondelete="CASCADE"),
                            nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id", ondelete="CASCADE"),
                          nullable=False)
    status = db.Column(db.Enum(ApplicationStatus, native_enum=False),
                        default=ApplicationStatus.APPLIED)
    resume_snapshot_path = db.Column(db.String(255), nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship("StudentProfile", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")
    interviews = db.relationship("Interview", back_populates="application",
                                  cascade="all, delete-orphan", passive_deletes=True,
                                  order_by="Interview.scheduled_at")

    def to_dict(self, include_student=False, include_drive=False):
        data = {
            "id": self.id,
            "student_id": self.student_id,
            "drive_id": self.drive_id,
            "status": self.status.value if self.status else None,
            "applied_at": self.applied_at.strftime("%Y-%m-%d %H:%M") if self.applied_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else None,
        }
        if include_student and self.student:
            data["student"] = self.student.to_dict()
        if include_drive and self.drive:
            data["drive"] = self.drive.to_dict()
            data["company_name"] = self.drive.company.company_name if self.drive.company else None
            data["job_title"] = self.drive.job_title
        return data


class Interview(db.Model):
    __tablename__ = "interview"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id", ondelete="CASCADE"),
                                nullable=False)
    round_name = db.Column(db.String(100), nullable=False, default="Interview")
    scheduled_at = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.Enum(InterviewMode, native_enum=False), default=InterviewMode.ONLINE)
    location_or_link = db.Column(db.String(255), nullable=True)
    remarks = db.Column(db.String(255), nullable=True)
    result = db.Column(db.Enum(InterviewResult, native_enum=False), default=InterviewResult.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship("Application", back_populates="interviews")

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "round_name": self.round_name,
            "scheduled_at": self.scheduled_at.strftime("%Y-%m-%d %H:%M") if self.scheduled_at else None,
            "mode": self.mode.value if self.mode else None,
            "location_or_link": self.location_or_link,
            "remarks": self.remarks,
            "result": self.result.value if self.result else None,
        }


# ---------------------------------------------------------------------------
# Notifications & system settings
# ---------------------------------------------------------------------------

class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=True)   # export_ready / reminder / status_update / system
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "link": self.link,
            "is_read": self.is_read,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }


class PortalVisit(db.Model):
    """One row per successful login. Powers admin "student visits" trend chart.
    Deliberately minimal (no session/duration tracking) — just enough for a
    month-wise activity count per role."""
    __tablename__ = "portal_visit"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class SystemSetting(db.Model):
    __tablename__ = "system_setting"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_value(cls, key, default=None):
        row = cls.query.filter_by(key=key).first()
        if row is None or row.value is None:
            return default
        val = row.value
        if str(val).lstrip("-").isdigit():
            return int(val)
        return val

    @classmethod
    def set_value(cls, key, value, description=None):
        row = cls.query.filter_by(key=key).first()
        if row:
            row.value = str(value)
            if description:
                row.description = description
        else:
            row = cls(key=key, value=str(value), description=description)
            db.session.add(row)
        db.session.commit()
        return row
