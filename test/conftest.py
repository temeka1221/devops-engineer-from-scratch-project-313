import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

load_dotenv()
os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
os.environ["BASE_URL"] = "http://testserver"


@pytest.fixture
def client():
    from main import app, engine

    with TestClient(app) as test_client:
        yield test_client
    SQLModel.metadata.drop_all(engine)
