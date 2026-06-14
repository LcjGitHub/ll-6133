"""配方路由模块。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db, write_change_log

router = APIRouter(prefix="/api/recipes", tags=["配方"])


@router.get("", response_model=list[schemas.RecipeOut])
def list_recipes(
    search: str | None = Query(None, description="按配方名称关键字模糊搜索"),
    ferment_type: str | None = Query(None, description="按发酵类型精确筛选"),
    db: Session = Depends(get_db),
):
    """获取全部配方，可按名称关键字模糊搜索，或按发酵类型精确筛选。"""
    query = db.query(models.Recipe)
    if search:
        query = query.filter(models.Recipe.name.contains(search))
    if ferment_type:
        query = query.filter(models.Recipe.ferment_type == ferment_type)
    return query.order_by(models.Recipe.created_at.desc()).all()


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
    write_change_log(db, "create", "recipe", recipe.id, f"创建配方：{recipe.name}")
    db.commit()
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

    change_parts = [f"{k}={v}" for k, v in update_data.items()]
    if steps_data is not None:
        change_parts.append("steps")
    summary = f"更新配方 #{recipe_id}：{', '.join(change_parts)}"

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
    write_change_log(db, "update", "recipe", recipe_id, summary)
    db.commit()
    return recipe


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """删除配方。"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="配方不存在")
    recipe_name = recipe.name
    db.delete(recipe)
    db.commit()
    write_change_log(db, "delete", "recipe", recipe_id, f"删除配方：{recipe_name}")
    db.commit()
