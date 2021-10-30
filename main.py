from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
from datetime import datetime
from config import db_config, app_config

from typing import Sequence

from base import do

app = FastAPI(
    title=app_config.title,
    docs_url=app_config.docs_url,
)

database = Database(db_config.host, port=db_config.port, user=db_config.username, password=db_config.password,
                    database=db_config.db_name)

origins = [
    "https://rdogs.dodofk.xyz/",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def database_connect():
    await database.connect()


@app.on_event("shutdown")
async def database_disconnect():
    await database.disconnect()


@app.get("/", response_class=HTMLResponse)
async def default_page():
    doc_path = "<a href=\"/docs\">/docs</a>"
    return doc_path


from api import include_routers
include_routers(app)
