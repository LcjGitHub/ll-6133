"""数据备份与恢复接口自动化测试用例。"""

import io
import json
from datetime import date, datetime

import pytest

import models

BACKUP_BASE_URL = "/api/backup"


def _create_test_data(db_session):
    """在数据库中创建测试数据。"""
    strain = models.Strain(
        name="乳酸菌A",
        ferment_type="蔬菜发酵",
        activation_date=date(2024, 1, 1),
        storage_location="冰箱上层",
        notes="活力旺盛",
    )
    db_session.add(strain)

    batch = models.Batch(
        type="韩式泡菜",
        start_date=date(2024, 6, 1),
        temperature=20.0,
        status="发酵中",
        ph=4.5,
    )
    db_session.add(batch)
    db_session.flush()

    note = models.Note(
        batch_id=batch.id,
        content="发酵初期，气泡开始产生",
    )
    db_session.add(note)

    measurement = models.Measurement(
        batch_id=batch.id,
        recorded_at=datetime(2024, 6, 2, 10, 0),
        temperature=20.5,
        ph=4.5,
    )
    db_session.add(measurement)

    reminder = models.Reminder(
        batch_id=batch.id,
        title="检查发酵状态",
        reminder_date=date(2024, 6, 5),
        completed=False,
    )
    db_session.add(reminder)

    recipe = models.Recipe(
        name="经典韩式泡菜",
        ferment_type="蔬菜发酵",
        ingredients="大白菜、辣椒粉、大蒜、生姜、鱼露",
    )
    db_session.add(recipe)
    db_session.flush()

    recipe_step = models.RecipeStep(
        recipe_id=recipe.id,
        step_order=1,
        description="将大白菜洗净切块，用盐腌制2小时",
    )
    db_session.add(recipe_step)

    db_session.commit()
    return batch.id


class TestDownloadBackup:
    """备份下载接口测试。"""

    def test_download_backup_success(self, client, db_session):
        """成功下载备份应返回 JSON 文件。"""
        _create_test_data(db_session)

        response = client.get(BACKUP_BASE_URL)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        assert "attachment" in response.headers["content-disposition"]
        assert ".json" in response.headers["content-disposition"]

        backup_data = response.json()
        assert backup_data["version"] == "1.0"
        assert "exported_at" in backup_data
        assert "tables" in backup_data

        tables = backup_data["tables"]
        assert len(tables["batches"]) == 1
        assert len(tables["notes"]) == 1
        assert len(tables["measurements"]) == 1
        assert len(tables["recipes"]) == 1
        assert len(tables["recipe_steps"]) == 1
        assert len(tables["reminders"]) == 1
        assert len(tables["strains"]) == 1

        batch = tables["batches"][0]
        assert batch["type"] == "韩式泡菜"
        assert batch["temperature"] == 20.0
        assert batch["ph"] == 4.5

    def test_download_backup_empty_db(self, client):
        """空数据库也应能生成备份文件。"""
        response = client.get(BACKUP_BASE_URL)

        assert response.status_code == 200
        backup_data = response.json()
        tables = backup_data["tables"]
        assert len(tables["batches"]) == 0
        assert len(tables["notes"]) == 0
        assert len(tables["measurements"]) == 0


class TestPreviewBackup:
    """备份预览接口测试。"""

    def test_preview_valid_backup(self, client, db_session):
        """有效备份文件应能正确预览数据量。"""
        _create_test_data(db_session)
        backup_resp = client.get(BACKUP_BASE_URL)
        backup_content = backup_resp.content

        file = io.BytesIO(backup_content)
        response = client.post(
            f"{BACKUP_BASE_URL}/preview",
            files={"file": ("test_backup.json", file, "application/json")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["batches"] == 1
        assert data["notes"] == 1
        assert data["measurements"] == 1
        assert data["recipes"] == 1
        assert data["recipe_steps"] == 1
        assert data["reminders"] == 1
        assert data["strains"] == 1

    def test_preview_invalid_json(self, client):
        """无效 JSON 文件应返回 400。"""
        file = io.BytesIO(b"not a json")
        response = client.post(
            f"{BACKUP_BASE_URL}/preview",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 400
        assert "JSON" in response.json()["detail"]

    def test_preview_wrong_file_extension(self, client):
        """非 .json 文件应返回 400。"""
        file = io.BytesIO(b"{}")
        response = client.post(
            f"{BACKUP_BASE_URL}/preview",
            files={"file": ("test.txt", file, "text/plain")},
        )

        assert response.status_code == 400
        assert ".json" in response.json()["detail"]

    def test_preview_missing_version_field(self, client):
        """缺少 version 字段应返回 400。"""
        invalid_backup = {"tables": {"batches": []}}
        file = io.BytesIO(json.dumps(invalid_backup).encode("utf-8"))
        response = client.post(
            f"{BACKUP_BASE_URL}/preview",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 400
        assert "version" in response.json()["detail"]

    def test_preview_missing_tables_field(self, client):
        """缺少 tables 字段应返回 400。"""
        invalid_backup = {"version": "1.0"}
        file = io.BytesIO(json.dumps(invalid_backup).encode("utf-8"))
        response = client.post(
            f"{BACKUP_BASE_URL}/preview",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 400
        assert "tables" in response.json()["detail"]

    def test_preview_missing_table(self, client):
        """缺少某个数据表应返回 400。"""
        invalid_backup = {
            "version": "1.0",
            "tables": {
                "batches": [],
                "notes": [],
                "measurements": [],
                "recipes": [],
                "recipe_steps": [],
                "reminders": [],
            },
        }
        file = io.BytesIO(json.dumps(invalid_backup).encode("utf-8"))
        response = client.post(
            f"{BACKUP_BASE_URL}/preview",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 400
        assert "strains" in response.json()["detail"]


class TestRestoreBackup:
    """备份恢复接口测试。"""

    def test_restore_without_confirm_should_fail(self, client, db_session):
        """未设置 confirm_overwrite 应拒绝恢复。"""
        _create_test_data(db_session)
        backup_resp = client.get(BACKUP_BASE_URL)
        backup_content = backup_resp.content

        file = io.BytesIO(backup_content)
        response = client.post(
            f"{BACKUP_BASE_URL}/restore",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 400
        assert "confirm_overwrite" in response.json()["detail"]

    def test_restore_with_confirm_success(self, client, db_session):
        """确认覆盖后应成功恢复数据。"""
        _create_test_data(db_session)
        backup_resp = client.get(BACKUP_BASE_URL)
        backup_content = backup_resp.content

        db_session.query(models.Batch).delete()
        db_session.commit()
        assert db_session.query(models.Batch).count() == 0

        file = io.BytesIO(backup_content)
        response = client.post(
            f"{BACKUP_BASE_URL}/restore?confirm_overwrite=true",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "数据恢复成功"
        assert data["summary"]["batches"] == 1
        assert data["summary"]["notes"] == 1

        assert db_session.query(models.Batch).count() == 1
        assert db_session.query(models.Note).count() == 1
        assert db_session.query(models.Measurement).count() == 1
        assert db_session.query(models.Recipe).count() == 1
        assert db_session.query(models.RecipeStep).count() == 1
        assert db_session.query(models.Reminder).count() == 1
        assert db_session.query(models.Strain).count() == 1

        batch = db_session.query(models.Batch).first()
        assert batch.type == "韩式泡菜"
        assert batch.temperature == 20.0
        assert batch.ph == 4.5

    def test_restore_overwrites_existing_data(self, client, db_session):
        """恢复时应覆盖现有数据。"""
        _create_test_data(db_session)
        backup_resp = client.get(BACKUP_BASE_URL)
        backup_content = backup_resp.content

        extra_batch = models.Batch(
            type="额外批次",
            start_date=date(2024, 7, 1),
            temperature=25.0,
            status="已完成",
            ph=None,
        )
        db_session.add(extra_batch)
        db_session.commit()
        assert db_session.query(models.Batch).count() == 2

        file = io.BytesIO(backup_content)
        response = client.post(
            f"{BACKUP_BASE_URL}/restore?confirm_overwrite=true",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 200
        assert db_session.query(models.Batch).count() == 1
        remaining = db_session.query(models.Batch).first()
        assert remaining.type == "韩式泡菜"

    def test_restore_invalid_file(self, client):
        """无效文件即使确认也应失败。"""
        file = io.BytesIO(b"invalid content")
        response = client.post(
            f"{BACKUP_BASE_URL}/restore?confirm_overwrite=true",
            files={"file": ("test.json", file, "application/json")},
        )

        assert response.status_code == 400
        assert "JSON" in response.json()["detail"]

    def test_restore_data_types_correct(self, client, db_session):
        """恢复后的数据类型应正确。"""
        _create_test_data(db_session)
        backup_resp = client.get(BACKUP_BASE_URL)
        backup_content = backup_resp.content

        db_session.query(models.Batch).delete()
        db_session.commit()

        file = io.BytesIO(backup_content)
        client.post(
            f"{BACKUP_BASE_URL}/restore?confirm_overwrite=true",
            files={"file": ("test.json", file, "application/json")},
        )

        batch = db_session.query(models.Batch).first()
        assert isinstance(batch.start_date, date)
        assert isinstance(batch.temperature, float)
        assert isinstance(batch.ph, float)
        assert isinstance(batch.created_at, datetime)

        measurement = db_session.query(models.Measurement).first()
        assert isinstance(measurement.recorded_at, datetime)

        reminder = db_session.query(models.Reminder).first()
        assert isinstance(reminder.reminder_date, date)
        assert isinstance(reminder.completed, bool)
