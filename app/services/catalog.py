from fastapi import Depends
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_async_session
from app.models import catalog as models
from app.schemas import catalog as schemas


class ProductService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def create_product(self, product_in: schemas.ProductCreate) -> models.Product:
        product = models.Product(**product_in.model_dump())
        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def get_product_by_id(self, product_id: int, with_category: bool = False) -> models.Product | None:
        statement = select(models.Product).where(models.Product.id == product_id)

        if with_category:
            statement = statement.options(joinedload(models.Product.category))

        result = await self.session.exec(statement)
        return result.first()

    async def get_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int | None = None,
    ) -> list[models.Product]:
        statement = select(models.Product).offset(skip).limit(limit)

        if category_id is not None:
            statement = statement.where(models.Product.category_id == category_id)

        result = await self.session.exec(statement)
        return result.all()

    async def update_product(
        self,
        db_product: models.Product,
        product_in: schemas.ProductUpdate,
    ) -> models.Product:
        update_data = product_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_product, key, value)

        self.session.add(db_product)
        await self.session.commit()
        await self.session.refresh(db_product)

        return db_product

    async def delete_product(self, db_product: models.Product) -> None:
        if db_product:
            await self.session.delete(db_product)
            await self.session.commit()


class CategoryService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def create_category(self, category_in: schemas.CategoryCreate) -> models.Category:
        category = models.Category(**category_in.model_dump())
        self.session.add(category)

        await self.session.commit()
        await self.session.refresh(category)

        return category

    async def get_category_by_id(self, id: int) -> models.Category | None:
        return await self.session.get(models.Category, id)

    async def update_category(
        self,
        db_category: models.Category,
        category_in: schemas.CategoryUpdate,
    ) -> models.Category:
        update_data = category_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_category, key, value)

        self.session.add(db_category)
        await self.session.commit()
        await self.session.refresh(db_category)

        return db_category

    async def get_categories(self, skip: int = 0, limit: int = 100) -> list[models.Category]:
        statement = select(models.Category).offset(skip).limit(limit)

        result = await self.session.exec(statement)

        return result.all()

    async def delete_category(self, db_category: models.Category) -> None:
        if db_category:
            await self.session.delete(db_category)
            await self.session.commit()
