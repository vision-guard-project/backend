from datetime import datetime, timezone

from app.infrastructure.extensions import db


class TimestampMixin:
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class UserModel(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.Text, nullable=True)
    roles = db.Column(db.JSON, nullable=False, default=list)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    social_accounts = db.relationship(
        "SocialAccountModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class SocialAccountModel(TimestampMixin, db.Model):
    __tablename__ = "social_accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    provider = db.Column(db.String(50), nullable=False)
    provider_user_id = db.Column(db.String(255), nullable=False)
    provider_email = db.Column(db.String(255), nullable=True)

    user = db.relationship("UserModel", back_populates="social_accounts")

    __table_args__ = (
        db.UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
    )
