from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# ================= CATEGORY SCHEMAS =================


class CategoryCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)


class CategoryUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = Field(default=None)
    is_active: bool


# ================= PRODUCT SCHEMAS =================


class ProductCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    price: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    stock: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    category_id: int | None = Field(default=None)


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None)
    price: Decimal | None = Field(default=None, ge=Decimal("0.00"))
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = Field(default=None)
    category_id: int | None = Field(default=None)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = Field(default=None)
    price: Decimal
    stock: int
    is_active: bool
    category_id: int | None = None


class ProductReadWithCategory(ProductRead):
    category: CategoryRead | None = None
