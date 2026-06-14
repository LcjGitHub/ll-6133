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


@router.put(
    "/api/batches/{batch_id}/measurements/{measurement_id}",
    response_model=schemas.MeasurementOut,
)
def update_measurement(
    batch_id: int,
    measurement_id: int,
    payload: schemas.MeasurementUpdate,
    db: Session = Depends(get_db),
):
    """更新指定批次下的单条测量记录。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    measurement = (
        db.query(models.Measurement)
        .filter(
            models.Measurement.id == measurement_id,
            models.Measurement.batch_id == batch_id,
        )
        .first()
    )
    if not measurement:
        raise HTTPException(status_code=404, detail="测量记录不存在或不属于该批次")

    if payload.recorded_at is not None:
        measurement.recorded_at = payload.recorded_at
    if payload.temperature is not None:
        measurement.temperature = payload.temperature
    if payload.ph is not None:
        measurement.ph = payload.ph

    db.commit()
    db.refresh(measurement)
    return measurement


@router.delete(
    "/api/batches/{batch_id}/measurements/{measurement_id}",
    status_code=204,
)
def delete_measurement(
    batch_id: int,
    measurement_id: int,
    db: Session = Depends(get_db),
):
    """删除指定批次下的单条测量记录。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    measurement = (
        db.query(models.Measurement)
        .filter(
            models.Measurement.id == measurement_id,
            models.Measurement.batch_id == batch_id,
        )
        .first()
    )
    if not measurement:
        raise HTTPException(status_code=404, detail="测量记录不存在或不属于该批次")

    db.delete(measurement)
    db.commit()
