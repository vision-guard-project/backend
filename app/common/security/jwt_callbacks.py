from flask import current_app


def register_jwt_callbacks(jwt_manager):
    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """
        Redis Blocklist를 붙이기 전까지는 항상 False.
        운영에서 로그아웃된 access token을 즉시 폐기하려면 Redis 조회 로직을 연결한다.
        """
        if not current_app.config.get("JWT_USE_REDIS_BLOCKLIST"):
            return False

        redis_client = current_app.extensions.get("redis")
        if not redis_client:
            return False

        jti = jwt_payload.get("jti")
        return redis_client.get(f"jwt_blocklist:{jti}") is not None
