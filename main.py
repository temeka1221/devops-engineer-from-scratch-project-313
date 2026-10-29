import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

sentry_sdk.init(dsn=os.environ.get("SENTRY_DSN"))
app = FastAPI()


@app.get("/ping", response_class=PlainTextResponse)
def ping():
    return "pong"


@app.get("/error", response_class=PlainTextResponse)
def error():
    return 1 / 0
