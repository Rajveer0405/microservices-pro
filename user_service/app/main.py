from fastapi import FastAPI

from .database import init_db
from .routes import router


app = FastAPI(title="User Service")
app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    init_db()
