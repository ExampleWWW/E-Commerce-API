from decimal import Decimal

import pydantic
import pytest

from app.schemas import cart as schemas


def test_cart_item_read_creation():
    """Тест 1 - Проверяем работу схемы CartItemRead"""

    cart = schemas.CartItemRead(
        product_id=1, title="Laptop", price=Decimal("200000.0"), quantity=5, total_price=Decimal("1000000.0")
    )

    assert cart.product_id == 1
    assert cart.title == "Laptop"
    assert cart.price == Decimal("200000.0")
    assert cart.total_price == Decimal("1000000.0")


def test_cart_item_add_negative_values():
    """Тест 2 - Проверяем, что CartItemAdd не пропускает количество меньше нуля"""

    with pytest.raises(pydantic.ValidationError):
        schemas.CartItemAdd(product_id=1, quantity=0)

    with pytest.raises(pydantic.ValidationError):
        schemas.CartItemAdd(product_id=1, quantity=-5)


def test_cart_read_total_cart_price():
    """Тест 3 - Проверяем создание итоговой схемы всей корзины CartRead"""

    item1 = schemas.CartItemRead(
        product_id=1, title="Mouse", price=Decimal("1000.00"), quantity=2, total_price=Decimal("2000.00")
    )
    item2 = schemas.CartItemRead(
        product_id=2, title="Keyboard", price=Decimal("3000.00"), quantity=1, total_price=Decimal("3000.00")
    )

    cart = schemas.CartRead(items=[item1, item2], total_cart_price=Decimal("5000.00"))

    assert len(cart.items) == 2
    assert cart.total_cart_price == Decimal("5000.00")
