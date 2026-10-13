from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from app.models.catalog import Product


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    total_price: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    items: list["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int | None = Field(default=None, foreign_key="orders.id", ondelete="CASCADE")
    product_id: int | None = Field(default=None, foreign_key="products.id", ondelete="SET NULL")
    quantity: int = Field(default=1, gt=0)
    price: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)

    # Обратные связи
    order: Order | None = Relationship(back_populates="items")
    product: Product | None = Relationship()
