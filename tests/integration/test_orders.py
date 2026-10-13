import pytest
from httpx import AsyncClient


async def _setup_user_and_product(client: AsyncClient, stock: int = 10) -> tuple[dict, int]:
    """Вспомогательная функция: регистрация, логин и создание товара с остатком stock."""

    user_data = {"email": "order_user@example.com", "password": "password123"}
    await client.post("/api/v1/auth/register", json=user_data)
    login_res = await client.post("/api/v1/auth/login", json=user_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cat_res = await client.post(
        "/api/v1/catalog/categories", json={"title": "Электроника", "description": "Техника"}
    )
    category_id = cat_res.json()["id"]

    prod_res = await client.post(
        "/api/v1/catalog/products",
        json={
            "title": "Смартфон",
            "description": "Новый",
            "price": "500.00",
            "stock": stock,
            "category_id": category_id,
        },
    )
    product_id = prod_res.json()["id"]

    return headers, product_id


@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient):
    """Тест 1 - Успешное создание заказа из корзины, списание остатка и очистка Redis."""

    headers, product_id = await _setup_user_and_product(client, stock=10)

    await client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 2}, headers=headers)

    order_res = await client.post("/api/v1/order/", headers=headers)
    assert order_res.status_code == 201
    order_data = order_res.json()

    assert order_data["status"] == "pending"
    assert float(order_data["total_price"]) == 1000.0

    cart_res = await client.get("/api/v1/cart/", headers=headers)
    assert len(cart_res.json()["items"]) == 0

    product_res = await client.get(f"/api/v1/catalog/products/{product_id}")
    assert product_res.json()["stock"] == 8


@pytest.mark.asyncio
async def test_create_order_empty_cart_failure(client: AsyncClient):
    """Тест 2 - Ошибка 400 Bad Request при попытке сделать заказ с пустой корзиной."""

    user_data = {"email": "empty_cart_user@example.com", "password": "password123"}
    await client.post("/api/v1/auth/register", json=user_data)
    login_res = await client.post("/api/v1/auth/login", json=user_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    order_res = await client.post("/api/v1/order/", headers=headers)
    assert order_res.status_code == 400
    assert order_res.json()["detail"] == "Cart is empty"


@pytest.mark.asyncio
async def test_create_order_insufficient_stock_failure(client: AsyncClient):
    """Тест 3 - Ошибка 400 Bad Request, если запрашиваемое количество превышает stock."""

    headers, product_id = await _setup_user_and_product(client, stock=3)

    await client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 5}, headers=headers)

    # Пробуем оформить заказ
    order_res = await client.post("/api/v1/order/", headers=headers)
    assert order_res.status_code == 400
    assert "Not enough stock" in order_res.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_orders_list_and_by_id(client: AsyncClient):
    """Тест 4 - Получение списка заказов и детальной информации по order_id с позициями."""

    headers, product_id = await _setup_user_and_product(client, stock=5)

    await client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 1}, headers=headers)
    created_order = (await client.post("/api/v1/order/", headers=headers)).json()
    order_id = created_order["id"]

    orders_list_res = await client.get("/api/v1/order/", headers=headers)
    assert orders_list_res.status_code == 200
    assert len(orders_list_res.json()) == 1

    order_detail_res = await client.get(f"/api/v1/order/{order_id}", headers=headers)
    assert order_detail_res.status_code == 200
    detail_data = order_detail_res.json()

    assert detail_data["id"] == order_id
    assert len(detail_data["items"]) == 1
    assert detail_data["items"][0]["product_id"] == product_id
