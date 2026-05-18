import os
from app.common.constants import UserRole, AuthProvider
from app.repositories import user_repository


def seed_admin_user():
    email = os.getenv("ADMIN_EMAIL", "admin@flare.com")
    password = os.getenv("ADMIN_PASSWORD", "1234")
    name = os.getenv("ADMIN_NAME", "관리자")

    exists = user_repository.find_by_email(email)

    if exists:
        return exists

    admin = user_repository.create_user(
        email=email,
        name=name,
        password=password,
        role=UserRole.ADMIN,
        provider=AuthProvider.LOCAL,
    )

    print(f"[SEED] 관리자 계정 생성 완료: {admin.email}")
    return admin