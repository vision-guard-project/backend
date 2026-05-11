backend/
├─ app/
│  ├─ common/
│  │  ├─ config.py
│  │  ├─ responses.py
│  │  └─ security/
│  │
│  ├─ controllers/
│  │  ├─ api.py
│  │  └─ auth_controller.py
│  │
│  ├─ domains/
│  │  └─ user/
│  │     ├─ enums.py
│  │     └─ schemas.py
│  │
│  ├─ infrastructure/
│  │  ├─ extensions.py
│  │  ├─ database/
│  │  │  └─ models/
│  │  │     ├─ user_model.py
│  │  │     └─ social_account_model.py
│  │  ├─ oauth/
│  │  ├─ external/
│  │  └─ ai/
│  │
│  ├─ repositories/
│  │  ├─ user_repository.py
│  │  └─ social_account_repository.py
│  │
│  └─ services/
│     ├─ auth_service.py
│     └─ social_auth_service.py