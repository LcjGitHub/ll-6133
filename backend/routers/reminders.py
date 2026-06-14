"""提醒路由模块。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/reminders", tags=["提醒"])


@router.get("", response_model=list[schemas.ReminderOut])
def list_reminders(db: Session = Depends(get_db)):
    """获取全部提醒。"""
    return (
        db.query(models.Reminder)
        .order_by(models.Reminder.completed.asc(), models.Reminder.reminder_date.asc())
        .all()
    )


@router.post("", response_model=schemas.ReminderOut, status_code=201)
def create_reminder(payload: schemas.ReminderCreate, db: Session = Depends(get_db)):
    """创建提醒。"""
    batch = db.query(models.Batch).filter(models.Batch.id == payload.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    reminder = models.Reminder(**payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/{reminder_id}", response_model=schemas.ReminderOut)
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """获取提醒详情。"""
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    return reminder


@router.put("/{reminder_id}", response_model=schemas.ReminderOut)
def update_reminder(
    reminder_id: int,
    payload: schemas.ReminderUpdate,
    db: Session = Depends(get_db),
):
    """更新提醒。"""
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    update_data = payload.model_dump(exclude_unset=True)
    if "batch_id" in update_data:
        batch = db.query(models.Batch).filter(models.Batch.id == update_data["batch_id"]).first()
        if not batch:
            raise HTTPException(status_code=404, detail="批次不存在")

    for key, value in update_data.items():
        setattr(reminder, key, value)

    db.commit()
    db.refresh(reminder)
    return reminder


@router.patch("/{reminder_id}/toggle", response_model=schemas.ReminderOut)
def toggle_reminder_completed(reminder_id: int, db: Session = Depends(get_db)):
    """切换提醒完成状态。"""
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    reminder.completed = not reminder.completed
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """删除提醒。"""
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    db.delete(reminder)
    db.commit()
