from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

password_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    if not plain_password:
        raise ValueError("password must not be empty")
    return password_hasher.hash(plain_password)


def verify_password(plain_password: str, password_hash: str | None) -> bool:
    if not plain_password or not password_hash:
        return False

    try:
        return password_hasher.verify(password_hash, plain_password)
    except (VerifyMismatchError, VerificationError):
        return False
