import requests
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from .config import AUTH_SERVICE_VERIFY_URL


def verify_token(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    authorization = f"{credentials.scheme} {credentials.credentials}"
    try:
        response = requests.get(
            AUTH_SERVICE_VERIFY_URL,
            headers={"Authorization": authorization},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Auth service is unavailable") from exc

    if response.status_code != 200:
        try:
            detail = response.json().get("detail", "Token verification failed")
        except ValueError:
            detail = "Token verification failed"
        raise HTTPException(status_code=401, detail=detail)

    return response.json()
