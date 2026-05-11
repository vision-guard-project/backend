from app.common.exceptions import UnauthorizedError
from app.infrastructure.models import UserModel
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


class SocialAuthService:
    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()
        self.auth_service = AuthService(self.user_repository)

    def login_or_signup(self, provider: str, profile: dict) -> tuple[UserModel, str, str]:
        provider_user_id = profile.get("provider_user_id")
        if not provider_user_id:
            raise UnauthorizedError(
                "소셜 사용자 식별자를 가져오지 못했습니다.",
                error_code="SOCIAL_PROFILE_INVALID",
            )

        user = self.user_repository.find_by_social(provider, provider_user_id)
        if user:
            access_token, refresh_token = self.auth_service.create_tokens(user)
            return user, access_token, refresh_token

        email = profile.get("email")
        name = profile.get("name")

        # 같은 이메일로 일반 가입한 사용자가 있는 경우 정책 결정 필요.
        # 여기서는 자동 연결하지 않고, 보수적으로 에러를 반환한다.
        if email and self.user_repository.find_by_email(email):
            raise UnauthorizedError(
                "이미 같은 이메일로 가입된 계정이 있습니다. 계정 연결 정책을 먼저 구현하세요.",
                error_code="EMAIL_ALREADY_EXISTS_NEEDS_LINKING",
            )

        user = self.user_repository.create_social_user(
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
        )
        self.user_repository.commit()

        access_token, refresh_token = self.auth_service.create_tokens(user)
        return user, access_token, refresh_token


def normalize_social_profile(provider: str, raw_profile: dict) -> dict:
    """Provider별 응답을 내부 공통 profile 형태로 변환한다."""

    if provider == "google":
        return {
            "provider_user_id": str(raw_profile.get("sub")),
            "email": raw_profile.get("email"),
            "name": raw_profile.get("name"),
        }

    if provider == "kakao":
        kakao_account = raw_profile.get("kakao_account", {}) or {}
        profile = kakao_account.get("profile", {}) or {}
        return {
            "provider_user_id": str(raw_profile.get("id")),
            "email": kakao_account.get("email"),
            "name": profile.get("nickname"),
        }

    if provider == "naver":
        response = raw_profile.get("response", {}) or {}
        return {
            "provider_user_id": str(response.get("id")),
            "email": response.get("email"),
            "name": response.get("name") or response.get("nickname"),
        }

    raise ValueError(f"unsupported provider: {provider}")
