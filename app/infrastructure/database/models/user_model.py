from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app.infrastructure.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # -------------------------------------------------
    # 기본 사용자 정보
    # -------------------------------------------------
    username = db.Column(db.String(100), nullable=True, index=True)

    email = db.Column(db.String(255), unique=True, nullable=True, index=True)

    password_hash = db.Column(db.String(255), nullable=True)

    profile_image_url = db.Column(db.Text, nullable=True)

    # -------------------------------------------------
    # 권한 / 상태
    # -------------------------------------------------
    role = db.Column(db.String(30), nullable=False, default="USER")

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    email_verified = db.Column(db.Boolean, nullable=False, default=False)

    # -------------------------------------------------
    # 로그인 관련
    # -------------------------------------------------
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # 이 사용자가 주로 어떤 방식으로 가입했는지 기록
    # local, kakao, naver, google
    primary_provider = db.Column(db.String(30), nullable=False, default="local")

    # -------------------------------------------------
    # 시간 정보
    # -------------------------------------------------
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # -------------------------------------------------
    # 관계
    # -------------------------------------------------
    social_accounts = db.relationship(
        "SocialAccountModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # -------------------------------------------------
    # Password
    # -------------------------------------------------
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password: str):
        if password:
            self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False

        return check_password_hash(self.password_hash, password)

    # -------------------------------------------------
    # Utils
    # -------------------------------------------------
    def mark_login(self):
        self.last_login_at = utc_now()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_image_url": self.profile_image_url,
            "role": self.role,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "primary_provider": self.primary_provider,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }