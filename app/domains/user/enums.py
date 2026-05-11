from enum import StrEnum


class UserRole(StrEnum):
    USER = "User"
    ADMIN = "Admin"


class AuthProvider(StrEnum):
    LOCAL = "local"
    GOOGLE = "google"
    KAKAO = "kakao"
    NAVER = "naver"
