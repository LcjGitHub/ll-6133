"""初始化种子数据。"""

from datetime import date

from sqlalchemy.orm import Session

from models import Batch, Note


def seed_data(db: Session) -> None:
    """若数据库为空，写入 3 条示例批次及笔记。"""
    if db.query(Batch).count() > 0:
        return

    batches = [
        Batch(
            type="康普茶",
            start_date=date(2026, 5, 20),
            temperature=26.0,
            status="发酵中",
            ph=3.2,
        ),
        Batch(
            type="泡菜",
            start_date=date(2026, 6, 1),
            temperature=22.0,
            status="观察中",
            ph=None,
        ),
        Batch(
            type="酸面包",
            start_date=date(2026, 5, 15),
            temperature=28.0,
            status="已完成",
            ph=4.5,
        ),
    ]

    db.add_all(batches)
    db.flush()

    notes = [
        Note(
            batch_id=batches[0].id,
            content="SCOBY 浮于液面，气泡活跃，气味酸甜。",
        ),
        Note(
            batch_id=batches[0].id,
            content="第 5 天：pH 降至 3.2，准备试饮。",
        ),
        Note(
            batch_id=batches[1].id,
            content="白菜出水良好，无明显异味。",
        ),
        Note(
            batch_id=batches[2].id,
            content="面团膨胀正常，已转入冷藏慢发酵。",
        ),
    ]

    db.add_all(notes)
    db.commit()
