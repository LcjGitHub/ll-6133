"""家庭发酵实验日志 — FastAPI 入口。"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db
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


@app.get("/api/batches", response_model=list[schemas.BatchOut])
def list_batches(db: Session = Depends(get_db)):
    """获取全部批次。"""
    return db.query(models.Batch).order_by(models.Batch.start_date.desc()).all()


@app.post("/api/batches", response_model=schemas.BatchOut, status_code=201)
def create_batch(payload: schemas.BatchCreate, db: Session = Depends(get_db)):
    """创建批次。"""
    batch = models.Batch(**payload.model_dump())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@app.get("/api/batches/{batch_id}", response_model=schemas.BatchDetail)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    """获取批次详情（含笔记）。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    return batch


@app.put("/api/batches/{batch_id}", response_model=schemas.BatchOut)
def update_batch(
    batch_id: int,
    payload: schemas.BatchUpdate,
    db: Session = Depends(get_db),
):
    """更新批次。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(batch, key, value)

    db.commit()
    db.refresh(batch)
    return batch


@app.delete("/api/batches/{batch_id}", status_code=204)
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    """删除批次。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    db.delete(batch)
    db.commit()


@app.post(
    "/api/batches/{batch_id}/notes",
    response_model=schemas.NoteOut,
    status_code=201,
)
def create_note(
    batch_id: int,
    payload: schemas.NoteCreate,
    db: Session = Depends(get_db),
):
    """为批次追加观察笔记。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    note = models.Note(batch_id=batch_id, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """删除笔记。"""
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    db.delete(note)
    db.commit()


@app.get("/api/recipes", response_model=list[schemas.RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    """获取全部配方。"""
    return db.query(models.Recipe).order_by(models.Recipe.created_at.desc()).all()


@app.post("/api/recipes", response_model=schemas.RecipeDetail, status_code=201)
def create_recipe(payload: schemas.RecipeCreate, db: Session = Depends(get_db)):
    """创建配方。"""
    recipe = models.Recipe(
        name=payload.name,
        ferment_type=payload.ferment_type,
        ingredients=payload.ingredients,
    )
    db.add(recipe)
    db.flush()

    for step_data in payload.steps:
        step = models.RecipeStep(
            recipe_id=recipe.id,
            step_order=step_data.step_order,
            description=step_data.description,
        )
        db.add(step)

    db.commit()
    db.refresh(recipe)
    return recipe


@app.get("/api/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """获取配方详情（含步骤）。"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    return recipe


@app.put("/api/recipes/{recipe_id}", response_model=schemas.RecipeDetail)
def update_recipe(
    recipe_id: int,
    payload: schemas.RecipeUpdate,
    db: Session = Depends(get_db),
):
    """更新配方。"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")

    update_data = payload.model_dump(exclude_unset=True)
    steps_data = update_data.pop("steps", None)

    for key, value in update_data.items():
        setattr(recipe, key, value)

    if steps_data is not None:
        db.query(models.RecipeStep).filter(
            models.RecipeStep.recipe_id == recipe_id
        ).delete()

        for step_data in steps_data:
            step = models.RecipeStep(
                recipe_id=recipe.id,
                step_order=step_data["step_order"],
                description=step_data["description"],
            )
            db.add(step)

    db.commit()
    db.refresh(recipe)
    return recipe


@app.delete("/api/recipes/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """删除配方。"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    db.delete(recipe)
    db.commit()
