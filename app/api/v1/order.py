from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas import order as schemas
from app.services.order import OrderService

router = APIRouter(prefix="/order", tags=["Orders 📦"])


# ----- ORDER ENDPOINTS -----


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.OrderReadWithItems | schemas.OrderRead,
    summary="Оформить новый заказ из корзины",
)
async def order_create(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(OrderService),
):
    order = await order_service.create_order(user_id=current_user.id)

    return order


@router.get(
    "/",
    response_model=list[schemas.OrderRead],
    summary="Получение истории заказов текущего пользователя",
)
async def order_get(
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(OrderService),
):
    orders = await order_service.get_user_orders(user_id=current_user.id)

    return orders


@router.get(
    "/{order_id}",
    response_model=schemas.OrderReadWithItems,
    summary="Получение информации о заказе с позициями",
)
async def order_get_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(OrderService),
):
    order = await order_service.get_order_by_id(order_id=order_id, user_id=current_user.id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order
