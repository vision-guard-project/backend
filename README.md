```
[ 현재까지 작업 트리 구조 ]
app/
│
├── config.py
│   # Flask 전체 환경설정 파일
│   # .env 값을 읽어서 DB 주소, JWT 키, OAuth 키, ITS API 주소 등을 설정한다.
│
├── extensions.py
│   # Flask 확장 객체를 한 곳에서 생성하는 파일
│   # db, migrate, cors, jwt 등을 정의한다.
│   # create_app()에서 init_app()으로 연결된다.
│
├── __init__.py
│   # Flask 앱 팩토리 파일
│   # create_app()을 정의한다.
│   # config 로딩, extensions 초기화, Blueprint 등록을 담당한다.
│
├── common/
│   │
│   ├── constants.py
│   │   # 프로젝트 전역 상수 관리 파일
│   │   # 예: 역할명, Provider명, 상태값 등을 관리할 수 있다.
│   │
│   ├── decorators.py
│   │   # 인증/권한 검사 데코레이터 파일
│   │   # 예: 로그인 필요, 관리자 권한 필요 같은 공통 검증 로직을 담당한다.
│   │
│   ├── response.py
│   │   # 공통 API 응답 포맷 관리 파일
│   │   # success(), fail() 형태로 프론트에 일관된 JSON 응답을 보낸다.
│   │
│   └── __init__.py
│       # common 패키지 인식용 파일
│
├── models/
│   │
│   ├── user.py
│   │   # 사용자 DB 모델
│   │   # 이메일, 이름, 비밀번호 해시, 역할, 활성화 여부 등을 관리한다.
│   │
│   ├── social_account.py
│   │   # 소셜 로그인 계정 연동 모델
│   │   # Google/Naver/Kakao provider 정보와 provider_user_id를 저장한다.
│   │
│   ├── cctv.py
│   │   # CCTV DB 모델
│   │   # CCTV 이름, 도로명, 주소, 위도/경도, 스트림 URL, 실행 상태 등을 저장한다.
│   │
│   └── __init__.py
│       # models 패키지 인식용 파일
│       # 필요 시 모델들을 한 번에 import하는 역할도 한다.
│
├── repositories/
│   │
│   ├── user_repository.py
│   │   # User 모델 DB 접근 전담 파일
│   │   # 이메일 조회, ID 조회, 사용자 저장, 목록 조회 등을 담당한다.
│   │
│   ├── social_account_repository.py
│   │   # SocialAccount 모델 DB 접근 전담 파일
│   │   # 소셜 계정 조회/저장/연동 확인 등을 담당한다.
│   │
│   ├── cctv_repository.py
│   │   # CCTV 모델 DB 접근 전담 파일
│   │   # CCTV 목록 조회, ID 조회, 저장, 2개 CCTV 교체 저장 등을 담당한다.
│   │
│   └── __init__.py
│       # repositories 패키지 인식용 파일
│
├── services/
│   │
│   ├── auth_service.py
│   │   # 로그인/회원가입 핵심 비즈니스 로직
│   │   # 비밀번호 해시 검증, JWT 발급, 내 정보 조회 등을 담당한다.
│   │
│   ├── oauth_service.py
│   │   # 소셜 로그인 비즈니스 로직
│   │   # Google/Naver/Kakao OAuth 인증 흐름과 사용자 연동을 담당한다.
│   │
│   ├── admin_service.py
│   │   # 관리자 기능 비즈니스 로직
│   │   # 사용자 목록 조회, 권한 변경 등을 담당한다.
│   │
│   ├── its_cctv_service.py
│   │   # ITS Open API 연동 서비스
│   │   # ITS CCTV 목록 호출, 응답 파싱, CCTV DB 저장, 시작/종료 상태 변경을 담당한다.
│   │
│   └── __init__.py
│       # services 패키지 인식용 파일
│
├── routes/
│   │
│   ├── auth_routes.py
│   │   # 인증 관련 API 라우트
│   │   # /api/auth/login, /api/auth/register, /api/auth/me, OAuth 로그인/콜백 등을 담당한다.
│   │
│   ├── admin_routes.py
│   │   # 관리자 관련 API 라우트
│   │   # /api/admin/users, 권한 변경 API 등을 담당한다.
│   │
│   ├── cctv_routes.py
│   │   # CCTV 관련 API 라우트
│   │   # /api/cctv, /api/cctv/sync, start/stop/snapshot API 등을 담당한다.
│   │
│   └── __init__.py
│       # routes 패키지 인식용 파일
│
└── seeds/
    │
    ├── seed_admin.py
    │   # 초기 관리자 계정 생성 파일
    │   # admin@flare.com 계정이 없으면 자동 생성한다.
    │
    └── __init__.py
        # seeds 패키지 인식용 파일
```