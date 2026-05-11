from functools import wraps

from flask_jwt_extended import get_jwt, jwt_required

from app.common.responses import error


def login_required(fn):
    """프로젝트 코드에서 @jwt_required() 대신 @login_required 형태로 쓰기 위한 래퍼."""

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def roles_required(*allowed_roles):
    """JWT additional_claims.roles 기준의 간단한 역할 기반 인가 데코레이터."""

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_roles = set(claims.get("roles", []))

            if not user_roles.intersection(set(allowed_roles)):
                return error(
                    message="접근 권한이 없습니다.",
                    code="FORBIDDEN",
                    status_code=403,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
