from datetime import timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password


def test_password_hashing_success():
    """Тест 1 - проверяем что верный пароль успешно проходит валидацию"""

    raw_password = "examplepassword"
    hashed = hash_password(password=raw_password)

    assert verify_password(plain_password=raw_password, hashed_password=hashed) is True


def test_password_hashing_failure():
    """Тест 2 - проверяем что неверный пароль не проходит валидацию"""

    raw_password = "examplepassword"
    hashed = hash_password(password=raw_password)

    assert verify_password(plain_password=raw_password + "fail", hashed_password=hashed) is False


def test_create_access_token():
    """Тест 3 - проверяем создание и правильное декодирование JWT токена"""

    user_id = 24

    token = create_access_token(subject=user_id)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload.get("sub") == str(user_id)


def test_jwt_expired():
    """Тест 4 - проверяем что просроченный токен вызывает ExpiredSignatureError"""

    user_id = 24
    token = create_access_token(subject=user_id, expires_delta=timedelta(minutes=-10))

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
