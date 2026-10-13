import pytest
from httpx import AsyncClient


async def _get_auth_headers_and_product_id(client: AsyncClient) -> tuple[dict, int]:
    """Вспомогательная функция для регистрации юзера и создания товара."""

    user_data = {"email": "cart_user@example.com", "password": "password123"}
    await client.post("/api/v1/auth/register", json=user_data)
    login_res = await client.post("/api/v1/auth/login", json=user_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cat_res = await client.post(
        "/api/v1/catalog/categories", json={"title": "Электроника", "description": "Бытовая техника"}
    )
    category_id = cat_res.json()["id"]

    prod_res = await client.post(
        "/api/v1/catalog/products",
        json={
            "title": "Наушники",
            "description": "Беспроводные",
            "price": "150.00",
            "stock": 10,
            "category_id": category_id,
        },
    )
    product_id = prod_res.json()["id"]

    return headers, product_id


@pytest.mark.asyncio
async def test_add_item_to_cart(client: AsyncClient):
    """Тест 1 - Успешное добавление товара в корзину (Redis)."""

    headers, product_id = await _get_auth_headers_and_product_id(client)

    response = await client.post(
        "/api/v1/cart/items", json={"product_id": product_id, "quantity": 2}, headers=headers
    )

    assert response.status_code == 200 or response.status_code == 201


@pytest.mark.asyncio
async def test_get_cart_success(client: AsyncClient):
    """Тест 2 - Получение содержимого корзины с перерасчетом стоимости."""

    headers, product_id = await _get_auth_headers_and_product_id(client)

    # Добавляем товар в количество 2 шт (цена 150.00 * 2 = 300.00)
    await client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 2}, headers=headers)

    response = await client.get("/api/v1/cart/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product_id
    assert float(data["total_cart_price"]) == 300.0


@pytest.mark.asyncio
async def test_update_cart_item_quantity(client: AsyncClient):
    """Тест 3 - Обновление количества товара в корзине."""
    headers, product_id = await _get_auth_headers_and_product_id(client)

    # Добавляем 1 шт
    await client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 1}, headers=headers)

    # Меняем количество на 5 шт
    update_res = await client.patch(f"/api/v1/cart/items/{product_id}", json={"quantity": 5}, headers=headers)
    assert update_res.status_code == 200

    # Проверяем обновленную корзину
    cart_res = await client.get("/api/v1/cart/", headers=headers)
    data = cart_res.json()
    assert data["items"][0]["quantity"] == 5
    assert float(data["total_cart_price"]) == 750.0  # 150.00 * 5


@pytest.mark.asyncio
async def test_clear_cart(client: AsyncClient):
    """Тест 4 - Полная очистка корзины в Redis."""
    headers, product_id = await _get_auth_headers_and_product_id(client)

    # Добавляем товар
    await client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 3}, headers=headers)

    # Очищаем корзину
    clear_res = await client.delete("/api/v1/cart/", headers=headers)
    assert clear_res.status_code == 204

    # Проверяем, что корзина пуста
    cart_res = await client.get("/api/v1/cart/", headers=headers)
    data = cart_res.json()
    assert len(data["items"]) == 0
    assert float(data["total_cart_price"]) == 0.0
