from fastapi import Depends
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.exceptions import HTTPException

from gateway_service.core.config import settings

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)


def check_api_key(key: str = Depends(api_key_header)):
    if key:
        return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"You didn't pass the api key in the header! Header: {settings.API_KEY_NAME}",
    )
