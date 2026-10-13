import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category_success(client: AsyncClient):
    """Тест 1 - Создание новой категории."""

    category_data = {"title": "Электроника", "description": "Бытовая и мобильная техника"}

    response = await client.post("/api/v1/catalog/categories", json=category_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == category_data["title"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_product_success(client: AsyncClient):
    """Тест 2 - Создание товара с привязкой к существующей категории."""

    cat_res = await client.post(
        "/api/v1/catalog/categories", json={"title": "Смартфоны", "description": "Мобильные телефоны"}
    )
    category_id = cat_res.json()["id"]

    product_data = {
        "title": "iPhone 15 Pro",
        "description": "Флагманский смартфон",
        "price": "999.99",
        "stock": 10,
        "category_id": category_id,
    }

    response = await client.post("/api/v1/catalog/products", json=product_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == product_data["title"]
    assert data["category_id"] == category_id
    assert "id" in data


@pytest.mark.asyncio
async def test_get_products_list_and_pagination(client: AsyncClient):
    """Тест 3 - Получение списка товаров и проверка пагинации."""

    cat_res = await client.post(
        "/api/v1/catalog/categories", json={"title": "Книги", "description": "Печатная продукция"}
    )
    category_id = cat_res.json()["id"]

    for i in range(2):
        await client.post(
            "/api/v1/catalog/products",
            json={
                "title": f"Книга {i + 1}",
                "description": "Описание",
                "price": "100.00",
                "stock": 5,
                "category_id": category_id,
            },
        )

    response = await client.get("/api/v1/catalog/products?skip=0&limit=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_product_by_id_with_category(client: AsyncClient):
    """Тест 4 - Получение товара по ID с жадной подгрузкой категории."""

    cat_res = await client.post(
        "/api/v1/catalog/categories", json={"title": "Ноутбуки", "description": "Компьютерная техника"}
    )
    category_id = cat_res.json()["id"]

    prod_res = await client.post(
        "/api/v1/catalog/products",
        json={
            "title": "MacBook Pro",
            "description": "M3 Max",
            "price": "2499.00",
            "stock": 3,
            "category_id": category_id,
        },
    )
    product_id = prod_res.json()["id"]

    response = await client.get(f"/api/v1/catalog/products/{product_id}?with_category=true")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert "category" in data
    assert data["category"]["title"] == "Ноутбуки"
