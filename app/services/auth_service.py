from flask_jwt_extended import create_access_token, create_refresh_token

from app.common.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.common.security.password import hash_password, verify_password
from app.infrastructure.models import UserModel
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    def signup(self, email: str, password: str, name: str | None = None) -> UserModel:
        if self.user_repository.find_by_email(email):
            raise ConflictError("이미 가입된 이메일입니다.", error_code="EMAIL_ALREADY_EXISTS")

        user = self.user_repository.create_local_user(
            email=email,
            password_hash=hash_password(password),
            name=name,
        )
        self.user_repository.commit()
        return user

    def login(self, email: str, password: str) -> tuple[UserModel, str, str]:
        user = self.user_repository.find_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError(
                "이메일 또는 비밀번호가 올바르지 않습니다.",
                error_code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise UnauthorizedError("비활성화된 사용자입니다.", error_code="INACTIVE_USER")

        access_token, refresh_token = self.create_tokens(user)
        return user, access_token, refresh_token

    def get_current_user(self, user_id: int) -> UserModel:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundError("사용자를 찾을 수 없습니다.", error_code="USER_NOT_FOUND")
        return user

    def create_tokens(self, user: UserModel) -> tuple[str, str]:
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "roles": user.roles,
            },
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        return access_token, refresh_token

    def create_access_token_only(self, user: UserModel) -> str:
        return create_access_token(
            identity=str(user.id),
            additional_claims={
                "email": user.email,
                "roles": user.roles,
            },
        )
