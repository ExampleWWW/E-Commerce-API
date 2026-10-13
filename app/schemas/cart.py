from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemRead(BaseModel):
    product_id: int
    title: str
    price: Decimal
    quantity: int
    total_price: Decimal  # price * quantity


class CartRead(BaseModel):
    items: list[CartItemRead]
    total_cart_price: Decimal
