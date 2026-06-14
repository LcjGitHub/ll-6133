"""测量记录路由模块。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(tags=["测量"])


@router.get(
    "/api/batches/{batch_id}/measurements",
    response_model=list[schemas.MeasurementOut],
)
def list_measurements(batch_id: int, db: Session = Depends(get_db)):
    """按批次查询全部测量记录。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    return (
        db.query(models.Measurement)
        .filter(models.Measurement.batch_id == batch_id)
        .order_by(models.Measurement.recorded_at.desc())
        .all()
    )


@router.post(
    "/api/batches/{batch_id}/measurements",
    response_model=schemas.MeasurementOut,
    status_code=201,
)
def create_measurement(
    batch_id: int,
    payload: schemas.MeasurementCreate,
    db: Session = Depends(get_db),
):
    """为批次新增单条测量记录。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    measurement = models.Measurement(
        batch_id=batch_id,
        recorded_at=payload.recorded_at,
        temperature=payload.temperature,
        ph=payload.ph,
    )
    db.add(measurement)
    db.commit()
    db.refresh(measurement)
    return measurement
