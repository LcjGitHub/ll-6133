"""变更记录路由模块。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/change-logs", tags=["变更记录"])


@router.get("", response_model=schemas.ChangeLogListResponse)
def list_change_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    """按时间倒序分页查询变更记录。"""
    total = db.query(func.count(models.ChangeLog.id)).scalar()
    items = (
        db.query(models.ChangeLog)
        .order_by(models.ChangeLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return schemas.ChangeLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
