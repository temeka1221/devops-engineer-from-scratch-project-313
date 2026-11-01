import os
from contextlib import asynccontextmanager

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from sqlmodel import SQLModel, create_engine

load_dotenv()
sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"))


def normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(normalize_db_url(os.environ["DATABASE_URL"]))


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"


@app.get("/error", response_class=PlainTextResponse)
def error():
    return 1 / 0
