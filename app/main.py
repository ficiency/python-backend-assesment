from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_tables
from app.routes import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # The tables have to exist before the first request arrives.
    create_tables()
    yield


# Entry point of the caching service.
app = FastAPI(title="Caching Service", lifespan=lifespan)
app.include_router(router)
