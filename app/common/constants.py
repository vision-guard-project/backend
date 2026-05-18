class UserRole:
    # 프론트 타입과 맞추기 위해 소문자 사용.
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AuthProvider:
    LOCAL = "local"
    GOOGLE = "google"
    NAVER = "naver"
    KAKAO = "kakao"