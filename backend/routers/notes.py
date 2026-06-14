"""笔记路由模块。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db, write_change_log

router = APIRouter(tags=["笔记"])

batch_notes_router = APIRouter(tags=["笔记"])


@batch_notes_router.post(
    "/api/batches/{batch_id}/notes",
    response_model=schemas.NoteOut,
    status_code=201,
)
def create_note(
    batch_id: int,
    payload: schemas.NoteCreate,
    db: Session = Depends(get_db),
):
    """为批次追加观察笔记。"""
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    note = models.Note(batch_id=batch_id, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    write_change_log(db, "create", "note", note.id, f"为批次 #{batch_id} 添加笔记")
    db.commit()
    return note


@router.put("/api/notes/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    payload: schemas.NoteUpdate,
    db: Session = Depends(get_db),
):
    """更新笔记内容。"""
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    note.content = payload.content
    db.commit()
    db.refresh(note)
    write_change_log(db, "update", "note", note_id, f"更新笔记 #{note_id}（批次 #{note.batch_id}）")
    db.commit()
    return note


@router.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """删除笔记。"""
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    batch_id = note.batch_id
    db.delete(note)
    db.commit()
    write_change_log(db, "delete", "note", note_id, f"删除笔记 #{note_id}（批次 #{batch_id}）")
    db.commit()
