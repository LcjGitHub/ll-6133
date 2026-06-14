"""菌种路由模块。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/strains", tags=["菌种"])


@router.get("", response_model=list[schemas.StrainOut])
def list_strains(db: Session = Depends(get_db)):
    """获取全部菌种。"""
    return db.query(models.Strain).order_by(models.Strain.created_at.desc()).all()


@router.post("", response_model=schemas.StrainOut, status_code=201)
def create_strain(payload: schemas.StrainCreate, db: Session = Depends(get_db)):
    """创建菌种。"""
    strain = models.Strain(
        name=payload.name,
        ferment_type=payload.ferment_type,
        activation_date=payload.activation_date,
        storage_location=payload.storage_location,
        notes=payload.notes,
    )
    db.add(strain)
    db.commit()
    db.refresh(strain)
    return strain


@router.put("/{strain_id}", response_model=schemas.StrainOut)
def update_strain(
    strain_id: int,
    payload: schemas.StrainUpdate,
    db: Session = Depends(get_db),
):
    """更新菌种。"""
    strain = db.query(models.Strain).filter(models.Strain.id == strain_id).first()
    if not strain:
        raise HTTPException(status_code=404, detail="菌种不存在")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(strain, key, value)

    db.commit()
    db.refresh(strain)
    return strain


@router.delete("/{strain_id}", status_code=204)
def delete_strain(strain_id: int, db: Session = Depends(get_db)):
    """删除菌种。"""
    strain = db.query(models.Strain).filter(models.Strain.id == strain_id).first()
    if not strain:
        raise HTTPException(status_code=404, detail="菌种不存在")
    db.delete(strain)
    db.commit()
