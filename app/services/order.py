from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_async_session
from app.core.redis import get_redis
from app.models.catalog import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.services.cart import CartService


class OrderService:
    def __init__(self, session: AsyncSession = Depends(get_async_session), redis: Redis = Depends(get_redis)):
        self.session = session
        self.redis = redis

    async def create_order(self, user_id: int) -> Order:
        """Создает заказ из товаров в корзине пользователя с проверкой остатков на складе."""

        cart_service = CartService(session=self.session, redis=self.redis)
        cart = await cart_service.get_cart(user_id=user_id)
        if not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        product_ids = [item.product_id for item in cart.items]

        statement = select(Product).where(Product.id.in_(product_ids)).with_for_update()
        result = await self.session.exec(statement)

        products_map = {p.id: p for p in result.all()}

        for item in cart.items:
            product = products_map.get(item.product_id)
            if not product or product.stock < item.quantity:
                available_stock = product.stock if product else 0

                await self.session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for product '{item.title}' (available: {available_stock})",
                )

        order = Order(user_id=user_id, total_price=cart.total_cart_price, status=OrderStatus.PENDING)
        self.session.add(order)
        await self.session.flush()

        for item in cart.items:
            order_item = OrderItem(
                order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=item.price
            )
            self.session.add(order_item)

            product = products_map[item.product_id]
            product.stock -= item.quantity
            self.session.add(product)

        await self.session.commit()
        await self.session.refresh(order)

        await cart_service.clear_cart(user_id=user_id)

        return order

    async def get_user_orders(self, user_id: int) -> list[Order]:
        """Возвращает список всех заказов текущего пользователя."""

        statement = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        result = await self.session.exec(statement)
        return result.all()

    async def get_order_by_id(self, order_id: int, user_id: int) -> Order | None:
        """Возвращает конкретный заказ пользователя с подгрузкой позиций (items)."""

        statement = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .options(joinedload(Order.items))
        )
        result = await self.session.exec(statement)

        return result.unique().first()
