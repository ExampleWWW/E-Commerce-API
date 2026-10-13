from unittest.mock import AsyncMock

import pytest

from app.schemas.cart import CartItemAdd
from app.services.cart import CartService


@pytest.mark.asyncio
async def test_add_item_calls_redis_hincrby():
    """Тест 1 - Проверяем, что add_item вызывает метод hincrby у Redis с верными ключами."""

    mock_redis = AsyncMock()
    mock_session = AsyncMock()

    item_in = CartItemAdd(product_id=10, quantity=2)
    user_id = 1

    cart_service = CartService(session=mock_session, redis=mock_redis)
    await cart_service.add_item(user_id=user_id, item_in=item_in)

    mock_redis.hincrby.assert_called_once_with("cart:1", "10", 2)


@pytest.mark.asyncio
async def test_update_item_not_found():
    """Тест 2 - Проверяем, что если товара нет в корзине (hexists=False), update_item возвращает False."""

    mock_redis = AsyncMock()
    mock_redis.hexists.return_value = False
    mock_session = AsyncMock()

    cart_service = CartService(session=mock_session, redis=mock_redis)
    result = await cart_service.update_item(user_id=1, product_id=10, quantity=5)

    assert result is False
    mock_redis.hset.assert_not_called()


@pytest.mark.asyncio
async def test_update_item_success():
    """Тест 3 - Проверяем успешное обновление количества товара в Redis."""

    mock_redis = AsyncMock()
    mock_redis.hexists.return_value = True
    mock_session = AsyncMock()

    cart_service = CartService(session=mock_session, redis=mock_redis)
    result = await cart_service.update_item(user_id=1, product_id=10, quantity=5)

    assert result is True
    mock_redis.hset.assert_called_once_with("cart:1", "10", 5)


@pytest.mark.asyncio
async def test_clear_cart():
    """Тест 4 - Проверяем очистку корзины пользователя."""

    mock_redis = AsyncMock()
    mock_session = AsyncMock()

    cart_service = CartService(session=mock_session, redis=mock_redis)
    await cart_service.clear_cart(user_id=1)

    mock_redis.delete.assert_called_once_with("cart:1")
