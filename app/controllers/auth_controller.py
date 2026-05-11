from time import time

from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_refresh_cookies,
    unset_refresh_cookies,
)

from app.common.exceptions import AppError
from app.common.responses import created, error, success
from app.common.security.decorators import login_required, roles_required
from app.infrastructure.oauth import get_oauth_client
from app.services.auth_service import AuthService
from app.services.social_auth_service import SocialAuthService, normalize_social_profile


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _user_to_dict(user):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "roles": user.roles,
    }


def _handle_app_error(exc: AppError):
    return error(
        message=exc.message,
        code=exc.error_code,
        status_code=exc.status_code,
    )


@auth_bp.post("/signup")
def signup():
    """
    일반 회원가입
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: password1234
            name:
              type: string
              example: 장은재
    responses:
      201:
        description: 회원가입 성공
      400:
        description: 요청값 오류
      409:
        description: 이미 가입된 이메일
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return error("email과 password는 필수입니다.", "VALIDATION_ERROR", 400)

    try:
        user = AuthService().signup(email=email, password=password, name=name)
        return created({"user": _user_to_dict(user)}, "회원가입이 완료되었습니다.")
    except AppError as exc:
        return _handle_app_error(exc)


@auth_bp.post("/login")
def login():
    """
    일반 로그인
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: password1234
    responses:
      200:
        description: 로그인 성공. refresh_token은 HttpOnly Cookie로 저장됩니다.
      400:
        description: 요청값 오류
      401:
        description: 인증 실패
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return error("email과 password는 필수입니다.", "VALIDATION_ERROR", 400)

    try:
        user, access_token, refresh_token = AuthService().login(email=email, password=password)
    except AppError as exc:
        return _handle_app_error(exc)

    response = jsonify(
        {
            "message": "로그인이 완료되었습니다.",
            "data": {
                "access_token": access_token,
                "user": _user_to_dict(user),
            },
        }
    )
    set_refresh_cookies(response, refresh_token)
    return response, 200


@auth_bp.get("/me")
@login_required
def me():
    """
    내 정보 조회
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    responses:
      200:
        description: 현재 사용자 정보
      401:
        description: 인증 실패
      404:
        description: 사용자 없음
    """
    user_id = int(get_jwt_identity())

    try:
        user = AuthService().get_current_user(user_id)
        return success({"user": _user_to_dict(user)}, "사용자 정보를 조회했습니다.")
    except AppError as exc:
        return _handle_app_error(exc)


@auth_bp.post("/refresh")
@jwt_required(refresh=True, locations=["cookies"])
def refresh():
    """
    Access Token 재발급
    ---
    tags:
      - Auth
    responses:
      200:
        description: Access Token 재발급 성공
      401:
        description: Refresh Token 없음 또는 유효하지 않음
    """
    user_id = int(get_jwt_identity())

    try:
        user = AuthService().get_current_user(user_id)
        access_token = AuthService().create_access_token_only(user)
        return success({"access_token": access_token}, "Access Token이 재발급되었습니다.")
    except AppError as exc:
        return _handle_app_error(exc)


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """
    로그아웃
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    responses:
      200:
        description: 로그아웃 성공
      401:
        description: 인증 실패
    """
    jwt_payload = get_jwt()
    jti = jwt_payload.get("jti")
    exp = jwt_payload.get("exp")

    response = jsonify({"message": "로그아웃되었습니다."})
    unset_refresh_cookies(response)

    if current_app.config.get("JWT_USE_REDIS_BLOCKLIST"):
        redis_client = current_app.extensions.get("redis")
        if redis_client and jti and exp:
            ttl = exp - int(time())
            if ttl > 0:
                redis_client.setex(f"jwt_blocklist:{jti}", ttl, "true")

    return response, 200


@auth_bp.get("/admin-check")
@roles_required("Admin")
def admin_check():
    """
    관리자 권한 확인
    ---
    tags:
      - Auth
    security:
      - BearerAuth: []
    responses:
      200:
        description: 관리자 권한 확인 성공
      403:
        description: 권한 없음
    """
    return success(message="관리자 권한이 확인되었습니다.")


@auth_bp.get("/social/<provider>/login")
def social_login(provider):
    """
    소셜 로그인 시작
    ---
    tags:
      - Auth
    parameters:
      - in: path
        name: provider
        required: true
        type: string
        enum: [google, kakao, naver]
    responses:
      302:
        description: 소셜 로그인 페이지로 이동
    """
    try:
        client = get_oauth_client(provider)
        redirect_uri = url_for("api.auth.social_callback", provider=provider, _external=True)
        return client.authorize_redirect(redirect_uri)
    except Exception as exc:
        return error(str(exc), "SOCIAL_LOGIN_INIT_FAILED", 400)


@auth_bp.get("/social/<provider>/callback")
def social_callback(provider):
    """
    소셜 로그인 콜백
    ---
    tags:
      - Auth
    parameters:
      - in: path
        name: provider
        required: true
        type: string
        enum: [google, kakao, naver]
    responses:
      200:
        description: 소셜 로그인 성공
      400:
        description: 소셜 로그인 실패
    """
    try:
        client = get_oauth_client(provider)
        token = client.authorize_access_token()

        if provider == "google":
            raw_profile = token.get("userinfo")
            if raw_profile is None:
                raw_profile = client.get("https://openidconnect.googleapis.com/v1/userinfo").json()
        elif provider == "kakao":
            raw_profile = client.get("v2/user/me").json()
        elif provider == "naver":
            raw_profile = client.get("v1/nid/me").json()
        else:
            return error("지원하지 않는 소셜 로그인 제공자입니다.", "UNSUPPORTED_PROVIDER", 400)

        profile = normalize_social_profile(provider, raw_profile)
        user, access_token, refresh_token = SocialAuthService().login_or_signup(provider, profile)

        # API 서버만 먼저 구현하는 경우 JSON 응답.
        # 프론트로 redirect하고 싶으면 FRONTEND_AUTH_CALLBACK_URL 정책에 맞게 변경한다.
        response = jsonify(
            {
                "message": "소셜 로그인이 완료되었습니다.",
                "data": {
                    "access_token": access_token,
                    "user": _user_to_dict(user),
                },
            }
        )
        set_refresh_cookies(response, refresh_token)
        return response, 200

    except AppError as exc:
        return _handle_app_error(exc)
    except Exception as exc:
        return error(str(exc), "SOCIAL_LOGIN_CALLBACK_FAILED", 400)
