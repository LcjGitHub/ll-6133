"""初始化种子数据。"""

from datetime import date, datetime

from sqlalchemy.orm import Session

from models import Batch, Note, Recipe, RecipeStep, Measurement


def seed_data(db: Session) -> None:
    """若数据库为空，写入示例数据。"""
    if db.query(Batch).count() == 0:
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

    if db.query(Measurement).count() == 0:
        first_batch = db.query(Batch).order_by(Batch.id.asc()).first()
        if first_batch:
            measurements = [
                Measurement(
                    batch_id=first_batch.id,
                    recorded_at=datetime(2026, 5, 22, 10, 30),
                    temperature=25.5,
                    ph=3.8,
                ),
                Measurement(
                    batch_id=first_batch.id,
                    recorded_at=datetime(2026, 5, 25, 9, 15),
                    temperature=26.2,
                    ph=3.4,
                ),
            ]
            db.add_all(measurements)

    if db.query(Recipe).count() == 0:
        recipes = [
            Recipe(
                name="经典康普茶",
                ferment_type="康普茶",
                ingredients="红茶 10g、白砂糖 100g、纯净水 1.5L、SCOBY 1 个、康普茶原液 200ml",
            ),
            Recipe(
                name="四川风味泡菜",
                ferment_type="泡菜",
                ingredients="大白菜 1 颗、胡萝卜 2 根、大蒜 1 头、生姜 1 块、辣椒 5 个、海盐 50g、清水 2L",
            ),
            Recipe(
                name="基础酸面包",
                ferment_type="酸面包",
                ingredients="高筋面粉 500g、天然酵种 150g、海盐 10g、纯净水 350g",
            ),
        ]

        db.add_all(recipes)
        db.flush()

        recipe_steps = [
            RecipeStep(
                recipe_id=recipes[0].id,
                step_order=1,
                description="将红茶用沸水冲泡，加入白砂糖搅拌至完全溶解，放凉至室温。",
            ),
            RecipeStep(
                recipe_id=recipes[0].id,
                step_order=2,
                description="将茶水倒入干净的玻璃容器中，加入 SCOBY 和康普茶原液。",
            ),
            RecipeStep(
                recipe_id=recipes[0].id,
                step_order=3,
                description="用透气纱布盖住瓶口，放置在 25-28°C 的阴凉处发酵 7-10 天。",
            ),
            RecipeStep(
                recipe_id=recipes[0].id,
                step_order=4,
                description="当 pH 降至 3.0-3.5 时，即可装瓶进行二次发酵，加入水果或香料调味。",
            ),
            RecipeStep(
                recipe_id=recipes[1].id,
                step_order=1,
                description="大白菜洗净切大块，胡萝卜切片，用盐腌制 2 小时让蔬菜出水。",
            ),
            RecipeStep(
                recipe_id=recipes[1].id,
                step_order=2,
                description="将腌制好的蔬菜挤干水分，分层装入干净的泡菜坛中，每层加入蒜片、姜片和辣椒。",
            ),
            RecipeStep(
                recipe_id=recipes[1].id,
                step_order=3,
                description="用剩余盐水（或清水加盐）没过蔬菜，压上重物确保蔬菜完全浸在液体中。",
            ),
            RecipeStep(
                recipe_id=recipes[1].id,
                step_order=4,
                description="密封后置于阴凉处，20°C 左右发酵 5-7 天即可食用。",
            ),
            RecipeStep(
                recipe_id=recipes[2].id,
                step_order=1,
                description="将面粉、水和天然酵种混合，揉成光滑面团，静置 30 分钟让面筋形成。",
            ),
            RecipeStep(
                recipe_id=recipes[2].id,
                step_order=2,
                description="加入海盐，继续揉面至面团能拉出薄膜，进行第一次发酵 3-4 小时至体积翻倍。",
            ),
            RecipeStep(
                recipe_id=recipes[2].id,
                step_order=3,
                description="取出面团排气，整形成圆形或椭圆形，放入发酵篮中进行第二次发酵 1-2 小时。",
            ),
            RecipeStep(
                recipe_id=recipes[2].id,
                step_order=4,
                description="烤箱预热至 230°C，将面团割口后放入烤盘中，喷入蒸汽，烤 35-40 分钟至表皮金黄。",
            ),
        ]

        db.add_all(recipe_steps)

    db.commit()
