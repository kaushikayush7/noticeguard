from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

from . import config, db, pipeline, tinyfish_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init()
    if config.DEMO_MODE:
        pipeline.refresh(demo=True)
    yield


app = FastAPI(title="NoticeGuard", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"ok": True, "demo_mode": config.DEMO_MODE}


@app.get("/api/alerts")
def alerts(type: str = Query("all")):
    return db.list_alerts(type)


@app.post("/api/refresh")
def refresh(demo: bool | None = None, check_links: bool = False):
    new = pipeline.refresh(demo=config.DEMO_MODE if demo is None else demo, check_links=check_links)
    return {"new": len(new), "alerts": new}


@app.get("/api/discover")
def discover(q: str):
    return tinyfish_client.discover(q)


app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "static", html=True), name="static")
