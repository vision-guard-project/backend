from app import create_app
from app.extensions import db
from app.seeds.seed_admin import seed_admin_user

app = create_app()

with app.app_context():
    # 개발 단계용. 나중에는 flask db migrate/upgrade로 전환.
    db.create_all()

    # 관리자 더미 계정 자동 생성.
    seed_admin_user()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)