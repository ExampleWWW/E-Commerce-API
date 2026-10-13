from decimal import Decimal

from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_async_session
from app.core.redis import get_redis
from app.models.catalog import Product
from app.schemas import cart as schemas


class CartService:
    def __init__(self, session: AsyncSession = Depends(get_async_session), redis: Redis = Depends(get_redis)):
        self.session = session
        self.redis = redis

    async def add_item(self, user_id: int, item_in: schemas.CartItemAdd) -> None:
        """Добавляет товар в корзину или увеличивает его количество."""

        await self.redis.hincrby(f"cart:{user_id}", str(item_in.product_id), item_in.quantity)

    async def update_item(self, user_id: int, product_id: int, quantity: int) -> bool:
        """Обновляет количество товара. Возвращает False, если товара нет в корзине."""

        exists = await self.redis.hexists(f"cart:{user_id}", str(product_id))
        if not exists:
            return False

        await self.redis.hset(f"cart:{user_id}", str(product_id), quantity)
        return True

    async def remove_item(self, user_id: int, product_id: int) -> None:
        """Удаляет товар из корзины."""

        await self.redis.hdel(f"cart:{user_id}", str(product_id))

    async def clear_cart(self, user_id: int) -> None:
        """Полностью очищает корзину пользователя."""

        await self.redis.delete(f"cart:{user_id}")

    async def get_cart(self, user_id: int) -> schemas.CartRead:
        """Получает корзину из Redis и заполняет ее данными о продуктах из PostgreSQL."""

        # Достаем все пары {product_id: quantity} из Redis
        raw_cart = await self.redis.hgetall(f"cart:{user_id}")
        if not raw_cart:
            return schemas.CartRead(items=[], total_cart_price=Decimal("0.00"))

        # Преобразуем ключи и значение из строк в int
        product_quantities = {
            int(product_id_key): int(quantity_value) for product_id_key, quantity_value in raw_cart.items()
        }
        product_ids = list(product_quantities.keys())

        # Достаем одним запросом все товары из PostgreSQL, через WHERE id IN (...)
        statement = select(Product).where(Product.id.in_(product_ids))
        result = await self.session.exec(statement)
        products = result.all()

        # Собираем элементы CartItemRead и считаем цены
        cart_items: list[schemas.CartItemRead] = []
        total_price = Decimal("0.00")

        for product in products:
            quantity = product_quantities.get(product.id, 0)
            item_total = product.price * quantity

            cart_items.append(
                schemas.CartItemRead(
                    product_id=product.id,
                    title=product.title,
                    price=product.price,
                    quantity=quantity,
                    total_price=item_total,
                )
            )

            total_price += item_total

        return schemas.CartRead(items=cart_items, total_cart_price=total_price)
