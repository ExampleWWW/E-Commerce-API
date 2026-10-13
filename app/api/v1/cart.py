from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas import cart as schemas
from app.services.cart import CartService
from app.services.catalog import ProductService

router = APIRouter(prefix="/cart", tags=["Cart 🛒"])


# ----- CART ENDPOINTS -----


@router.get(
    "/",
    response_model=schemas.CartRead,
    status_code=status.HTTP_200_OK,
    summary="Получить корзину",
)
async def cart_get(
    current_user: User = Depends(get_current_user), cart_service: CartService = Depends(CartService)
):
    cart = await cart_service.get_cart(user_id=current_user.id)

    return cart


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить товар в корзину",
)
async def create_item(
    item_in: schemas.CartItemAdd,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(CartService),
    product_service: ProductService = Depends(ProductService),
):
    product = await product_service.get_product_by_id(item_in.product_id, with_category=False)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await cart_service.add_item(user_id=current_user.id, item_in=item_in)

    return {"detail": "Item added to cart"}


@router.patch(
    "/items/{product_id}",
    summary="Изменить количество товара в корзине",
)
async def change_item_quantity(
    product_id: int,
    item_in: schemas.CartItemUpdate,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(CartService),
    product_service: ProductService = Depends(ProductService),
):
    updated = await cart_service.update_item(
        user_id=current_user.id, product_id=product_id, quantity=item_in.quantity
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")

    return {"detail": "Cart updated"}


@router.delete(
    "/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить товар из корзины",
)
async def delete_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(CartService),
):
    await cart_service.remove_item(user_id=current_user.id, product_id=product_id)

    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Очистить всю корзину")
async def delete_cart(
    current_user: User = Depends(get_current_user), cart_service: CartService = Depends(CartService)
):
    await cart_service.clear_cart(user_id=current_user.id)

    return None
