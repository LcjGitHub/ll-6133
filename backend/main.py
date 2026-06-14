"""家庭发酵实验日志 — FastAPI 入口。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
from database import Base, engine, get_db
from routers.batches import router as batches_router
from routers.notes import router as notes_router
from routers.notes import batch_notes_router
from routers.measurements import router as measurements_router
from routers.recipes import router as recipes_router
from routers.statistics import router as statistics_router
from routers.reminders import router as reminders_router
from routers.strains import router as strains_router
from routers.search import router as search_router
from routers.backup import router as backup_router
from seed import seed_data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="家庭发酵实验日志 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5101",
        "http://127.0.0.1:5101",
        "http://localhost:5102",
        "http://127.0.0.1:5102",
        "http://localhost:5103",
        "http://127.0.0.1:5103",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """启动时写入种子数据。"""
    db = next(get_db())
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    """健康检查。"""
    return {"status": "ok"}


app.include_router(batches_router)
app.include_router(batch_notes_router)
app.include_router(notes_router)
app.include_router(measurements_router)
app.include_router(recipes_router)
app.include_router(statistics_router)
app.include_router(reminders_router)
app.include_router(strains_router)
app.include_router(search_router)
app.include_router(backup_router)
