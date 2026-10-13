import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    """Тест 1 - Успешная регистрация нового пользователя."""

    user_data = {"email": "integration_user@example.com", "password": "strongpassword123"}

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email_failure(client: AsyncClient):
    """Тест 2 - Ошибка 400 Bad Request при повторной регистрации с тем же email."""

    user_data = {"email": "duplicate_user@example.com", "password": "password123"}

    res1 = await client.post("/api/v1/auth/register", json=user_data)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/auth/register", json=user_data)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success_and_get_me(client: AsyncClient):
    """Тест 3 - Логин, получение JWT и запрос к защищенному роуту /auth/me."""

    user_data = {"email": "authed_user@example.com", "password": "password123"}

    await client.post("/api/v1/auth/register", json=user_data)

    login_res = await client.post("/api/v1/auth/login", json=user_data)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)

    assert me_res.status_code == 200
    assert me_res.json()["email"] == user_data["email"]
