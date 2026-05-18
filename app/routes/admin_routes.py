from flask import Blueprint, request
from app.common.decorators import admin_required
from app.common.response import success, fail
from app.repositories import user_repository

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/users")
@admin_required
def get_users():
    users = user_repository.find_all()
    return success([user.to_dict() for user in users], "회원 목록 조회 성공")


@admin_bp.patch("/users/<user_id>/role")
@admin_required
def change_user_role(user_id):
    body = request.get_json() or {}
    new_role = body.get("newRole")

    if new_role not in ["admin", "operator", "viewer"]:
        return fail("잘못된 권한입니다.", 400)

    user = user_repository.find_by_id(user_id)

    if not user:
        return fail("사용자를 찾을 수 없습니다.", 404)

    user.role = new_role
    user_repository.save(user)

    return success(user.to_dict(), "권한 변경 성공")