from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .schemas import UserCreate, UserUpdate
from .services import create_user, delete_user, list_users, require_token, update_user


router = APIRouter()
bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/add_user")
def add_user(
    payload: UserCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    require_token(credentials)
    return create_user(payload.model_dump())


@router.get("/get_users")
def get_users(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme),
) -> dict:
    if credentials:
        require_token(credentials)
    return list_users()


@router.put("/update_user/{user_id}")
def update_existing_user(
    user_id: int,
    payload: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    require_token(credentials)
    return update_user(user_id, payload.model_dump(exclude_unset=True))


@router.delete("/delete_user/{user_id}")
def delete_existing_user(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    require_token(credentials)
    return delete_user(user_id)
