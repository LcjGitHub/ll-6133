"""统计数据路由模块。"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/statistics", tags=["统计"])


@router.get("", response_model=schemas.StatisticsOut)
def get_statistics(db: Session = Depends(get_db)):
    """获取数据统计概览。"""
    status_counts = dict(
        db.query(models.Batch.status, func.count(models.Batch.id))
        .group_by(models.Batch.status)
        .all()
    )

    type_counts = dict(
        db.query(models.Batch.type, func.count(models.Batch.id))
        .group_by(models.Batch.type)
        .all()
    )

    now_local = datetime.now()
    seven_days_ago_date = now_local.date() - timedelta(days=7)
    seven_days_ago = datetime.combine(seven_days_ago_date, datetime.min.time())
    recent_notes_count = (
        db.query(func.count(models.Note.id))
        .filter(models.Note.created_at >= seven_days_ago)
        .scalar()
        or 0
    )

    return {
        "status_counts": status_counts,
        "type_counts": type_counts,
        "recent_notes_count": recent_notes_count,
    }
