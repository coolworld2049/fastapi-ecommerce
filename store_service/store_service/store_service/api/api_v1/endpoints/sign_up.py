from typing import Optional

from fastapi import APIRouter
from prisma.models import User
from prisma.partials import UserWithoutRelations, UserCreateOpen

from store_service.core.auth import hash_password
from store_service.db.base import dbapp
from store_service.validator.user import UserValidator

router = APIRouter()


@router.post(
    "/customer",
    response_model=UserWithoutRelations,
)
async def sign_up_customer(user_in: UserCreateOpen) -> Optional[User]:
    UserValidator(user_in).validate()
    user_in.password = hash_password(user_in.password)
    user = await User.prisma().create(user_in.dict())
    await dbapp.command(
        "createUser",
        user_in.username,
        pwd=hash_password(user_in.password),
        roles=[{"role": "customer", "db": dbapp.name}],
    )
    return user
