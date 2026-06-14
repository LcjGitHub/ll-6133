"""容器路由模块。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/containers", tags=["容器"])


@router.get("", response_model=list[schemas.ContainerOut])
def list_containers(db: Session = Depends(get_db)):
    """获取全部容器。"""
    return db.query(models.Container).order_by(models.Container.created_at.desc()).all()


@router.post("", response_model=schemas.ContainerOut, status_code=201)
def create_container(payload: schemas.ContainerCreate, db: Session = Depends(get_db)):
    """创建容器。"""
    if payload.current_batch_id is not None:
        batch = db.query(models.Batch).filter(models.Batch.id == payload.current_batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="批次不存在")
    container = models.Container(
        name=payload.name,
        capacity_ml=payload.capacity_ml,
        material=payload.material,
        in_use=payload.in_use,
        current_batch_id=payload.current_batch_id,
    )
    db.add(container)
    db.commit()
    db.refresh(container)
    return container


@router.put("/{container_id}", response_model=schemas.ContainerOut)
def update_container(
    container_id: int,
    payload: schemas.ContainerUpdate,
    db: Session = Depends(get_db),
):
    """更新容器。"""
    container = db.query(models.Container).filter(models.Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="容器不存在")

    update_data = payload.model_dump(exclude_unset=True)

    if "current_batch_id" in update_data and update_data["current_batch_id"] is not None:
        batch = db.query(models.Batch).filter(models.Batch.id == update_data["current_batch_id"]).first()
        if not batch:
            raise HTTPException(status_code=404, detail="批次不存在")

    for key, value in update_data.items():
        setattr(container, key, value)

    db.commit()
    db.refresh(container)
    return container


@router.delete("/{container_id}", status_code=204)
def delete_container(container_id: int, db: Session = Depends(get_db)):
    """删除空闲容器。"""
    container = db.query(models.Container).filter(models.Container.id == container_id).first()
    if not container:
        raise HTTPException(status_code=404, detail="容器不存在")
    if container.in_use:
        raise HTTPException(status_code=400, detail="使用中的容器无法删除")
    db.delete(container)
    db.commit()
