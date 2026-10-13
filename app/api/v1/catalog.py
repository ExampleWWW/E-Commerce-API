from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import catalog as schemas
from app.services.catalog import CategoryService, ProductService

router = APIRouter(prefix="/catalog", tags=["Catalog 📕"])


# ----- PRODUCT ENDPOINTS -----


@router.post(
    "/products",
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать товар",
)
async def product_create(
    product_in: schemas.ProductCreate,
    product_service: ProductService = Depends(ProductService),
):
    return await product_service.create_product(product_in=product_in)


@router.get(
    "/products",
    response_model=list[schemas.ProductRead],
    summary="Получить список товаров с фильтрацией и пагинацией",
)
async def product_list(
    skip: int = 0,
    limit: int = 100,
    category_id: int | None = None,
    product_service: ProductService = Depends(ProductService),
):
    return await product_service.get_products(skip=skip, limit=limit, category_id=category_id)


@router.get(
    "/products/{product_id}",
    response_model=schemas.ProductReadWithCategory | schemas.ProductRead,
    summary="Получить товар по ID",
)
async def product_by_id(
    product_id: int,
    with_category: bool = False,
    product_service: ProductService = Depends(ProductService),
):
    product = await product_service.get_product_by_id(product_id=product_id, with_category=with_category)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product with that ID exists")

    return product


@router.patch(
    "/products/{product_id}",
    response_model=schemas.ProductRead,
    summary="Обновить данные о товаре по ID",
)
async def product_patch(
    product_id: int,
    product_in: schemas.ProductUpdate,
    product_service: ProductService = Depends(ProductService),
):
    product = await product_service.get_product_by_id(product_id=product_id, with_category=False)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product with that ID exists")

    return await product_service.update_product(db_product=product, product_in=product_in)


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар по ID",
)
async def product_delete(
    product_id: int,
    product_service: ProductService = Depends(ProductService),
):
    product = await product_service.get_product_by_id(product_id=product_id, with_category=False)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No product with that ID exists")

    await product_service.delete_product(db_product=product)


# ----- CATEGORY ENDPOINTS -----


@router.post(
    "/categories",
    response_model=schemas.CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать категорию товаров",
)
async def categories_create(
    category_in: schemas.CategoryCreate,
    category_service: CategoryService = Depends(CategoryService),
):
    return await category_service.create_category(category_in=category_in)


@router.get(
    "/categories",
    response_model=list[schemas.CategoryRead],
    summary="Получить список категорий с пагинацией",
)
async def categories_get(
    skip: int = 0,
    limit: int = 100,
    category_service: CategoryService = Depends(CategoryService),
):
    return await category_service.get_categories(skip=skip, limit=limit)


@router.get(
    "/categories/{category_id}",
    response_model=schemas.CategoryRead,
    summary="Получить категорию по ID",
)
async def category_by_id(
    category_id: int,
    category_service: CategoryService = Depends(CategoryService),
):
    category = await category_service.get_category_by_id(category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No category with that ID exists")

    return category


@router.patch(
    "/categories/{category_id}",
    response_model=schemas.CategoryRead,
    summary="Частичное обновление категории по ID",
)
async def category_by_id_patch(
    category_id: int,
    category_in: schemas.CategoryUpdate,
    category_service: CategoryService = Depends(CategoryService),
):
    category = await category_service.get_category_by_id(category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No category with that ID exists")

    return await category_service.update_category(db_category=category, category_in=category_in)


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить категорию по ID",
)
async def category_delete(
    category_id: int,
    category_service: CategoryService = Depends(CategoryService),
):
    category = await category_service.get_category_by_id(category_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No category with that ID exists")

    await category_service.delete_category(db_category=category)
