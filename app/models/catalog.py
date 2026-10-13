from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=255)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)

    products: list["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=255)
    description: str | None = Field(default=None)
    price: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)

    category_id: int | None = Field(default=None, foreign_key="categories.id", ondelete="SET NULL")
    category: Category | None = Relationship(back_populates="products")
