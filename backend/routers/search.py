"""全局搜索路由模块。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/search", tags=["搜索"])


@router.get("", response_model=schemas.SearchResult)
def global_search(
    q: str = Query(..., min_length=1, description="搜索关键字"),
    db: Session = Depends(get_db),
):
    """全局搜索：按关键字同时模糊匹配批次类型、配方名称、观察笔记正文。"""
    keyword = q.strip()

    batches = (
        db.query(models.Batch)
        .filter(models.Batch.type.contains(keyword))
        .order_by(models.Batch.start_date.desc())
        .all()
    )

    recipes = (
        db.query(models.Recipe)
        .filter(models.Recipe.name.contains(keyword))
        .order_by(models.Recipe.created_at.desc())
        .all()
    )

    notes = (
        db.query(models.Note)
        .filter(models.Note.content.contains(keyword))
        .order_by(models.Note.created_at.desc())
        .all()
    )

    batch_items = [
        schemas.SearchBatchItem(
            id=batch.id,
            type=batch.type,
            start_date=batch.start_date,
            status=batch.status,
            fermentation_days=batch.fermentation_days,
        )
        for batch in batches
    ]

    recipe_items = [
        schemas.SearchRecipeItem(
            id=recipe.id,
            name=recipe.name,
            ferment_type=recipe.ferment_type,
        )
        for recipe in recipes
    ]

    note_items = [
        schemas.SearchNoteItem(
            id=note.id,
            batch_id=note.batch_id,
            content=note.content,
            created_at=note.created_at,
        )
        for note in notes
    ]

    batch_count = len(batch_items)
    recipe_count = len(recipe_items)
    note_count = len(note_items)

    return schemas.SearchResult(
        batches=batch_items,
        recipes=recipe_items,
        notes=note_items,
        batch_count=batch_count,
        recipe_count=recipe_count,
        note_count=note_count,
        total_count=batch_count + recipe_count + note_count,
    )
