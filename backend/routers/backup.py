"""数据备份与恢复路由模块。"""

import json
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/backup", tags=["备份与恢复"])

BACKUP_VERSION = "1.0"
BACKUP_TABLES = [
    "batches",
    "notes",
    "strains",
    "recipes",
    "recipe_steps",
    "measurements",
    "reminders",
]


def _serialize_instance(instance) -> dict:
    """将 SQLAlchemy 模型实例序列化为字典（保留原始ID）。"""
    data = {}
    for column in instance.__table__.columns:
        value = getattr(instance, column.name)
        if value is None:
            data[column.name] = None
        elif isinstance(value, datetime):
            data[column.name] = value.isoformat()
        elif hasattr(value, "isoformat"):
            data[column.name] = value.isoformat()
        else:
            data[column.name] = value
    return data


def _deserialize_value(column_type, value):
    """根据列类型反序列化值。"""
    if value is None:
        return None
    python_type = column_type.python_type
    if python_type is datetime and isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    if hasattr(python_type, "fromisoformat") and isinstance(value, str):
        return python_type.fromisoformat(value)
    return value


@router.get("")
def download_backup(db: Session = Depends(get_db)):
    """导出全部表数据为 JSON 备份文件。"""
    tables: dict[str, list[dict]] = {}

    tables["batches"] = [_serialize_instance(b) for b in db.query(models.Batch).order_by(models.Batch.id).all()]
    tables["notes"] = [_serialize_instance(n) for n in db.query(models.Note).order_by(models.Note.id).all()]
    tables["measurements"] = [
        _serialize_instance(m) for m in db.query(models.Measurement).order_by(models.Measurement.id).all()
    ]
    tables["recipes"] = [_serialize_instance(r) for r in db.query(models.Recipe).order_by(models.Recipe.id).all()]
    tables["recipe_steps"] = [
        _serialize_instance(s) for s in db.query(models.RecipeStep).order_by(models.RecipeStep.id).all()
    ]
    tables["reminders"] = [_serialize_instance(r) for r in db.query(models.Reminder).order_by(models.Reminder.id).all()]
    tables["strains"] = [_serialize_instance(s) for s in db.query(models.Strain).order_by(models.Strain.id).all()]

    backup_data = {
        "version": BACKUP_VERSION,
        "exported_at": datetime.utcnow().isoformat(),
        "tables": tables,
    }

    json_bytes = json.dumps(backup_data, ensure_ascii=False, indent=2).encode("utf-8")
    bio = BytesIO(json_bytes)
    bio.seek(0)

    filename = f"ferment_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        bio,
        media_type="application/json",
        headers=headers,
    )


def _parse_backup_file(file: UploadFile) -> dict:
    """解析并校验上传的备份文件，返回解析后的数据字典。"""
    if not (file.filename and file.filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="仅支持 .json 格式的备份文件")
    try:
        contents = file.file.read()
        backup_data = json.loads(contents.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="备份文件格式错误，无法解析 JSON")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"读取备份文件失败: {exc}")

    if not isinstance(backup_data, dict):
        raise HTTPException(status_code=400, detail="备份文件根结构无效")
    if "version" not in backup_data:
        raise HTTPException(status_code=400, detail="备份文件缺少 version 字段")
    if "tables" not in backup_data or not isinstance(backup_data["tables"], dict):
        raise HTTPException(status_code=400, detail="备份文件缺少 tables 字段")

    missing = [t for t in BACKUP_TABLES if t not in backup_data["tables"]]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"备份文件缺少数据表: {', '.join(missing)}",
        )
    return backup_data


def _summarize_backup(backup_data: dict) -> schemas.BackupSummary:
    """统计备份文件中各表的记录数量。"""
    tables = backup_data["tables"]
    return schemas.BackupSummary(
        batches=len(tables.get("batches", [])),
        notes=len(tables.get("notes", [])),
        measurements=len(tables.get("measurements", [])),
        recipes=len(tables.get("recipes", [])),
        recipe_steps=len(tables.get("recipe_steps", [])),
        reminders=len(tables.get("reminders", [])),
        strains=len(tables.get("strains", [])),
    )


@router.post("/preview", response_model=schemas.BackupSummary)
def preview_backup(file: UploadFile = File(...)):
    """校验备份文件格式并返回其中各表的记录数量摘要（不写入数据库）。"""
    backup_data = _parse_backup_file(file)
    return _summarize_backup(backup_data)


@router.post("/restore", response_model=schemas.BackupRestoreResult)
def restore_backup(
    file: UploadFile = File(...),
    confirm_overwrite: bool = Query(
        False,
        description="是否确认覆盖现有全部数据，必须设为 true 才会执行恢复",
    ),
    db: Session = Depends(get_db),
):
    """从备份文件恢复数据。需要 confirm_overwrite=true 才会清空并覆盖现有数据。"""
    if not confirm_overwrite:
        raise HTTPException(
            status_code=400,
            detail="恢复操作将覆盖现有全部数据，请确认后将 confirm_overwrite 设为 true",
        )

    backup_data = _parse_backup_file(file)
    summary = _summarize_backup(backup_data)
    tables = backup_data["tables"]

    try:
        db.query(models.Reminder).delete()
        db.query(models.Measurement).delete()
        db.query(models.Note).delete()
        db.query(models.RecipeStep).delete()
        db.query(models.Recipe).delete()
        db.query(models.Batch).delete()
        db.query(models.Strain).delete()
        db.flush()

        for row in tables.get("strains", []):
            obj = models.Strain()
            for col in models.Strain.__table__.columns:
                if col.name in row:
                    setattr(obj, col.name, _deserialize_value(col.type, row[col.name]))
            db.add(obj)
        db.flush()

        for row in tables.get("batches", []):
            obj = models.Batch()
            for col in models.Batch.__table__.columns:
                if col.name in row:
                    setattr(obj, col.name, _deserialize_value(col.type, row[col.name]))
            db.add(obj)
        db.flush()

        for row in tables.get("recipes", []):
            obj = models.Recipe()
            for col in models.Recipe.__table__.columns:
                if col.name in row:
                    setattr(obj, col.name, _deserialize_value(col.type, row[col.name]))
            db.add(obj)
        db.flush()

        for row in tables.get("notes", []):
            obj = models.Note()
            for col in models.Note.__table__.columns:
                if col.name in row:
                    setattr(obj, col.name, _deserialize_value(col.type, row[col.name]))
            db.add(obj)

        for row in tables.get("recipe_steps", []):
            obj = models.RecipeStep()
            for col in models.RecipeStep.__table__.columns:
                if col.name in row:
                    setattr(obj, col.name, _deserialize_value(col.type, row[col.name]))
            db.add(obj)

        for row in tables.get("measurements", []):
            obj = models.Measurement()
            for col in models.Measurement.__table__.columns:
                if col.name in row:
                    setattr(obj, col.name, _deserialize_value(col.type, row[col.name]))
            db.add(obj)

        for row in tables.get("reminders", []):
            obj = models.Reminder()
            for col in models.Reminder.__table__.columns:
                if col.name in row:
                    setattr(obj, col.name, _deserialize_value(col.type, row[col.name]))
            db.add(obj)

        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"恢复数据时发生错误: {exc}")

    return schemas.BackupRestoreResult(
        success=True,
        message="数据恢复成功",
        summary=summary,
    )
