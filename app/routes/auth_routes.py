from urllib.parse import urlencode
from flask import Blueprint, request, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.common.response import success, fail
from app.services import auth_service, oauth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    body = request.get_json() or {}

    try:
        result = auth_service.register_user(
            email=body.get("email"),
            name=body.get("name"),
            password=body.get("password"),
            department=body.get("department"),
            phone=body.get("phone"),
        )
        return success(result, "회원가입 성공", 201)
    except Exception as e:
        return fail(str(e), 400)


@auth_bp.post("/login")
def login():
    body = request.get_json() or {}

    try:
        result = auth_service.login_user(
            email=body.get("email"),
            password=body.get("password"),
        )
        return success(result, "로그인 성공")
    except Exception as e:
        return fail(str(e), 401)


@auth_bp.get("/me")
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()
        user = auth_service.get_current_user(user_id)
        return success(user, "내 정보 조회 성공")
    except Exception as e:
        return fail(str(e), 404)


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return success(None, "로그아웃 성공")


@auth_bp.get("/oauth/<provider>/login")
def oauth_login(provider):
    try:
        url = oauth_service.get_oauth_login_url(provider)
        return redirect(url)
    except Exception as e:
        return fail(str(e), 400)


@auth_bp.get("/oauth/<provider>/callback")
def oauth_callback(provider):
    code = request.args.get("code")

    if not code:
        return redirect(f"{current_app.config['FRONTEND_URL']}/login?error=oauth_no_code")

    try:
        result = oauth_service.handle_oauth_callback(provider, code)

        query = urlencode({
            "accessToken": result["accessToken"],
        })

        return redirect(f"{current_app.config['FRONTEND_URL']}/oauth/callback?{query}")
    except Exception:
        return redirect(f"{current_app.config['FRONTEND_URL']}/login?error=oauth_failed")