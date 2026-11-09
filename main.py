import os
from contextlib import asynccontextmanager
from datetime import datetime

import sentry_sdk
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel, create_engine, select

load_dotenv()
sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"))


class LinkCreate(SQLModel):
    original_url: str = Field(min_length=1)
    short_name: str = Field(min_length=1)


class Link(LinkCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    short_name: str = Field(unique=True)
    created_at: datetime | None = Field(
        default=None, sa_column_kwargs={"server_default": func.now()}
    )


BASE_URL = os.environ["BASE_URL"].rstrip("/")


class LinkPublic(SQLModel):
    id: int
    original_url: str
    short_name: str
    short_url: str


def to_public(link: Link) -> LinkPublic:
    return LinkPublic(
        id=link.id,
        original_url=link.original_url,
        short_name=link.short_name,
        short_url=f"{BASE_URL}/r/{link.short_name}",
    )


def normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(normalize_db_url(os.environ["DATABASE_URL"]))


def get_session():
    with Session(engine) as session:
        yield session


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


@app.post("/api/links", status_code=201)
def create_links(
    data: LinkCreate, session: Session = Depends(get_session)
) -> LinkPublic:
    link = Link.model_validate(data)
    session.add(link)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Short name already exists")
    session.refresh(link)
    return to_public(link)


@app.get("/api/links/{link_id}")
def get_link(link_id: int, session: Session = Depends(get_session)) -> LinkPublic:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return to_public(link)


@app.get("/api/links")
def list_links(session: Session = Depends(get_session)) -> list[LinkPublic]:
    links = session.exec(select(Link)).all()
    return [to_public(link) for link in links]


@app.put("/api/links/{link_id}")
def update_link(
    link_id: int, data: LinkCreate, session: Session = Depends(get_session)
) -> LinkPublic:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    link.sqlmodel_update(data.model_dump())
    session.add(link)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Short name already exists")
    session.refresh(link)
    return to_public(link)


@app.delete("/api/links/{link_id}", status_code=204)
def delete_link(link_id: int, session: Session = Depends(get_session)) -> None:
    link = session.get(Link, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    session.delete(link)
    session.commit()
