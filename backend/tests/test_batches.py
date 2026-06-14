"""批次接口自动化测试用例。"""

from datetime import date, timedelta

import pytest

import models


BASE_URL = "/api/batches"


def _batch_payload(**overrides):
    """构造批次创建请求体。"""
    payload = {
        "type": "红茶菌",
        "start_date": date.today().isoformat(),
        "temperature": 25.0,
        "status": "发酵中",
        "ph": None,
    }
    payload.update(overrides)
    return payload


def _create_batch(client, **overrides):
    """辅助方法：通过 API 创建一个批次并返回响应。"""
    return client.post(BASE_URL, json=_batch_payload(**overrides))


class TestCreateBatch:
    """创建批次接口测试。"""

    def test_create_batch_success(self, client):
        """成功创建批次应返回 201 和正确数据。"""
        payload = _batch_payload(type="开菲尔", temperature=22.5, status="发酵中", ph=4.2)
        response = client.post(BASE_URL, json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] > 0
        assert data["type"] == "开菲尔"
        assert data["temperature"] == 22.5
        assert data["status"] == "发酵中"
        assert data["ph"] == 4.2
        assert data["start_date"] == payload["start_date"]
        assert "created_at" in data
        assert "fermentation_days" in data

    def test_create_batch_without_ph(self, client):
        """创建批次时 pH 可选，不传应为 null。"""
        payload = _batch_payload()
        payload.pop("ph")
        response = client.post(BASE_URL, json=payload)

        assert response.status_code == 201
        assert response.json()["ph"] is None

    def test_create_batch_empty_type_should_fail(self, client):
        """类型为空字符串应返回 422。"""
        payload = _batch_payload(type="")
        response = client.post(BASE_URL, json=payload)
        assert response.status_code == 422

    def test_create_batch_missing_required_field_should_fail(self, client):
        """缺少必填字段 temperature 应返回 422。"""
        payload = _batch_payload()
        payload.pop("temperature")
        response = client.post(BASE_URL, json=payload)
        assert response.status_code == 422


class TestGetBatch:
    """按编号查询批次详情接口测试。"""

    def test_get_batch_success(self, client):
        """查询存在的批次应返回 200 和详情数据。"""
        create_resp = _create_batch(client, type="味噌", status="发酵中")
        batch_id = create_resp.json()["id"]

        response = client.get(f"{BASE_URL}/{batch_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == batch_id
        assert data["type"] == "味噌"
        assert data["status"] == "发酵中"
        assert "notes" in data
        assert isinstance(data["notes"], list)
        assert "measurements" in data
        assert isinstance(data["measurements"], list)

    def test_get_batch_not_found(self, client):
        """查询不存在的批次应返回 404。"""
        response = client.get(f"{BASE_URL}/99999")
        assert response.status_code == 404
        assert "批次不存在" in response.json()["detail"]


class TestUpdateBatch:
    """更新批次字段接口测试。"""

    def test_update_single_field(self, client):
        """仅更新状态字段。"""
        create_resp = _create_batch(client, status="发酵中")
        batch_id = create_resp.json()["id"]

        response = client.put(f"{BASE_URL}/{batch_id}", json={"status": "已完成"})
        assert response.status_code == 200
        assert response.json()["status"] == "已完成"
        assert response.json()["type"] == create_resp.json()["type"]

    def test_update_multiple_fields(self, client):
        """同时更新类型、温度、pH 多个字段。"""
        create_resp = _create_batch(client, type="纳豆", temperature=30.0, ph=None)
        batch_id = create_resp.json()["id"]

        response = client.put(
            f"{BASE_URL}/{batch_id}",
            json={"type": "日本纳豆", "temperature": 35.5, "ph": 7.8},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "日本纳豆"
        assert data["temperature"] == 35.5
        assert data["ph"] == 7.8

    def test_update_start_date(self, client):
        """更新开始日期字段。"""
        create_resp = _create_batch(client)
        batch_id = create_resp.json()["id"]
        new_date = (date.today() - timedelta(days=5)).isoformat()

        response = client.put(f"{BASE_URL}/{batch_id}", json={"start_date": new_date})
        assert response.status_code == 200
        assert response.json()["start_date"] == new_date

    def test_update_batch_not_found(self, client):
        """更新不存在的批次应返回 404。"""
        response = client.put(f"{BASE_URL}/99999", json={"status": "已完成"})
        assert response.status_code == 404
        assert "批次不存在" in response.json()["detail"]

    def test_update_empty_type_should_fail(self, client):
        """将类型更新为空字符串应返回 422。"""
        create_resp = _create_batch(client)
        batch_id = create_resp.json()["id"]

        response = client.put(f"{BASE_URL}/{batch_id}", json={"type": ""})
        assert response.status_code == 422


class TestDeleteBatch:
    """删除批次接口测试。"""

    def test_delete_batch_success(self, client):
        """删除存在的批次应返回 204。"""
        create_resp = _create_batch(client)
        batch_id = create_resp.json()["id"]

        response = client.delete(f"{BASE_URL}/{batch_id}")
        assert response.status_code == 204
        assert response.text == ""

        get_resp = client.get(f"{BASE_URL}/{batch_id}")
        assert get_resp.status_code == 404

    def test_delete_batch_not_found(self, client):
        """删除不存在的批次应返回 404。"""
        response = client.delete(f"{BASE_URL}/99999")
        assert response.status_code == 404
        assert "批次不存在" in response.json()["detail"]

    def test_delete_removes_associated_notes(self, client, db_session):
        """删除批次时应级联删除关联的笔记。"""
        create_resp = _create_batch(client)
        batch_id = create_resp.json()["id"]

        note = models.Note(batch_id=batch_id, content="测试笔记")
        db_session.add(note)
        db_session.commit()

        assert db_session.query(models.Note).filter(models.Note.batch_id == batch_id).count() == 1

        client.delete(f"{BASE_URL}/{batch_id}")

        assert db_session.query(models.Note).filter(models.Note.batch_id == batch_id).count() == 0


class TestListBatches:
    """批次列表筛选与搜索接口测试。"""

    def _seed_batches(self, client):
        """写入测试批次数据。"""
        today = date.today()
        _create_batch(
            client,
            type="红茶菌",
            start_date=(today - timedelta(days=3)).isoformat(),
            status="发酵中",
        )
        _create_batch(
            client,
            type="开菲尔牛奶",
            start_date=(today - timedelta(days=2)).isoformat(),
            status="已完成",
        )
        _create_batch(
            client,
            type="开菲尔水",
            start_date=(today - timedelta(days=1)).isoformat(),
            status="发酵中",
        )
        _create_batch(
            client,
            type="味噌",
            start_date=today.isoformat(),
            status="已完成",
        )

    def test_list_all_batches(self, client):
        """不带筛选参数应返回全部批次，按开始日期倒序。"""
        self._seed_batches(client)

        response = client.get(BASE_URL)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        dates = [item["start_date"] for item in data]
        assert dates == sorted(dates, reverse=True)

    def test_filter_by_status_fermenting(self, client):
        """按状态筛选：仅返回「发酵中」的批次。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"status": "发酵中"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(item["status"] == "发酵中" for item in data)

    def test_filter_by_status_completed(self, client):
        """按状态筛选：仅返回「已完成」的批次。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"status": "已完成"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(item["status"] == "已完成" for item in data)

    def test_filter_by_type_exact(self, client):
        """按类型精确筛选。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"type": "味噌"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "味噌"

    def test_filter_by_status_and_type_combined(self, client):
        """同时按状态和类型筛选。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"status": "已完成", "type": "味噌"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "味噌"
        assert data[0]["status"] == "已完成"

    def test_filter_returns_empty_when_no_match(self, client):
        """筛选无匹配时返回空列表。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"status": "不存在的状态"})
        assert response.status_code == 200
        assert response.json() == []

    def test_search_by_type_keyword(self, client):
        """按类型关键字模糊搜索：匹配「开菲尔」。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"search": "开菲尔"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("开菲尔" in item["type"] for item in data)

    def test_search_by_type_keyword_partial(self, client):
        """按类型关键字模糊搜索：部分匹配。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"search": "茶"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "红茶菌"

    def test_search_returns_empty_when_no_match(self, client):
        """搜索关键字无匹配时返回空列表。"""
        self._seed_batches(client)

        response = client.get(BASE_URL, params={"search": "不存在关键字"})
        assert response.status_code == 200
        assert response.json() == []

    def test_list_empty_db(self, client):
        """数据库为空时返回空列表。"""
        response = client.get(BASE_URL)
        assert response.status_code == 200
        assert response.json() == []

    def test_fermentation_days_calculated(self, client):
        """列表响应中 fermentation_days 字段正确计算。"""
        _create_batch(client, start_date=date.today().isoformat())
        response = client.get(BASE_URL)
        assert response.json()[0]["fermentation_days"] >= 1
