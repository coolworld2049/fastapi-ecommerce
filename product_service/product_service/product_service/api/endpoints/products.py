from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response

from product_service.models.product import ProductCreate
from product_service import crud
from product_service.api.dependencies import auth
from product_service.api.dependencies import params
from product_service.models.product import Product
from product_service.models.request_params import RequestParams
from product_service.models.user import User

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[Product])
async def read_products(
    response: Response,

    current_user: User = Depends(auth.get_current_active_user),
    request_params: RequestParams = Depends(
        params.parse_query_params(),
    ),
) -> Any:
    """
    Retrieve products.
    """
    products, total = await crud.product.get_multi(request_params)
    response.headers[
        "Content-Range"
    ] = f"{request_params.skip}-{request_params.skip + len(products)}/{total}"
    return products


# noinspection PyUnusedLocal
@router.post("/", response_model=Product)
async def create_product(
    *,

    product_in: ProductCreate,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Create new product.
    """

    product = await crud.product.create(obj_in=product_in)
    return product


# noinspection PyUnusedLocal
@router.get("/{title}", response_model=Product)
async def read_product_by_id(
    title: Any,
    current_user: User = Depends(auth.get_current_active_user),

) -> Any:
    """
    Get a specific product.
    """
    product = await crud.product.get(title)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="The product does not exist",
        )
    return product


# noinspection PyUnusedLocal
@router.delete("/{title}", status_code=200)
async def delete_product(
    *,
    title: Any,
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    """
    Delete product.
    """
    product = await crud.product.get(title)
    if not product:
        raise HTTPException(status_code=404, detail="Item not found")
    product = await crud.product.remove(id=id)
    return {'deatils': 'Successfully deleted'}
