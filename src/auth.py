"""Teacher credential helpers."""

import base64
import hashlib
import hmac
import json
import secrets
from pathlib import Path

PASSWORD_HASH_ITERATIONS = 310_000
TEACHERS_FILE = Path(__file__).with_name("teachers.json")


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _decode(value: str) -> bytes:
    return base64.b64decode(value, altchars=b"-_", validate=True)


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )


def create_teacher_record(username: str, password: str) -> dict[str, str]:
    salt = secrets.token_bytes(16)
    return {
        "username": username,
        "salt": _encode(salt),
        "password_hash": _encode(hash_password(password, salt)),
    }


def load_teachers(path: Path = TEACHERS_FILE) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as file:
        config = json.load(file)

    if not isinstance(config, dict) or not isinstance(config.get("teachers"), list):
        raise ValueError("Teacher credentials file must contain a teachers list")

    teachers = config["teachers"]
    usernames: set[str] = set()
    for teacher in teachers:
        if (
            not isinstance(teacher, dict)
            or not isinstance(teacher.get("username"), str)
            or not isinstance(teacher.get("salt"), str)
            or not isinstance(teacher.get("password_hash"), str)
        ):
            raise ValueError("Each teacher must have a username, salt, and password_hash")
        if teacher["username"] in usernames:
            raise ValueError("Teacher usernames must be unique")
        usernames.add(teacher["username"])
        _decode(teacher["salt"])
        _decode(teacher["password_hash"])

    return teachers


def verify_teacher_credentials(
    username: str, password: str, teachers: list[dict[str, str]]
) -> bool:
    teacher = next(
        (candidate for candidate in teachers if candidate["username"] == username),
        None,
    )
    salt = _decode(teacher["salt"]) if teacher else b"unknown-teacher-salt"
    expected_hash = _decode(teacher["password_hash"]) if teacher else bytes(32)
    actual_hash = hash_password(password, salt)
    return teacher is not None and hmac.compare_digest(expected_hash, actual_hash)
