"""配方路由模块。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/recipes", tags=["配方"])


@router.get("", response_model=list[schemas.RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    """获取全部配方。"""
    return db.query(models.Recipe).order_by(models.Recipe.created_at.desc()).all()


@router.post("", response_model=schemas.RecipeDetail, status_code=201)
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


@router.get("/{recipe_id}", response_model=schemas.RecipeDetail)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """获取配方详情（含步骤）。"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    return recipe


@router.put("/{recipe_id}", response_model=schemas.RecipeDetail)
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


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """删除配方。"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    db.delete(recipe)
    db.commit()
