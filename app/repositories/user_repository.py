from app.infrastructure.extensions import db
from app.infrastructure.models import SocialAccountModel, UserModel


class UserRepository:
    """
    User 관련 DB 접근 계층.
    더 엄격한 Clean Architecture를 원하면 Protocol/Interface와 구현체를 분리해도 된다.
    """

    def find_by_id(self, user_id: int) -> UserModel | None:
        return db.session.get(UserModel, user_id)

    def find_by_email(self, email: str) -> UserModel | None:
        return UserModel.query.filter_by(email=email).first()

    def find_by_social(self, provider: str, provider_user_id: str) -> UserModel | None:
        social_account = SocialAccountModel.query.filter_by(
            provider=provider,
            provider_user_id=provider_user_id,
        ).first()

        if not social_account:
            return None

        return social_account.user

    def create_local_user(self, email: str, password_hash: str, name: str | None = None) -> UserModel:
        user = UserModel(
            email=email,
            name=name,
            password_hash=password_hash,
            roles=["User"],
        )
        db.session.add(user)
        return user

    def create_social_user(
        self,
        provider: str,
        provider_user_id: str,
        email: str | None,
        name: str | None,
    ) -> UserModel:
        user = UserModel(
            email=email,
            name=name,
            password_hash=None,
            roles=["User"],
        )
        db.session.add(user)
        db.session.flush()

        social_account = SocialAccountModel(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=email,
        )
        db.session.add(social_account)

        return user

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
