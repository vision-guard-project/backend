from dataclasses import dataclass, field

from app.domains.user.enums import UserRole


@dataclass(frozen=True)
class User:
    id: int | None
    email: str | None
    name: str | None
    roles: list[str] = field(default_factory=lambda: [UserRole.USER.value])
    is_active: bool = True
