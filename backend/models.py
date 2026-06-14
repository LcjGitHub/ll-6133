"""SQLAlchemy 数据模型。"""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Batch(Base):
    """发酵批次。"""

    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="batch", cascade="all, delete-orphan"
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        "Measurement",
        back_populates="batch",
        cascade="all, delete-orphan",
        order_by="Measurement.recorded_at.desc()",
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="batch", cascade="all, delete-orphan"
    )

    @property
    def fermentation_days(self) -> int:
        """已发酵天数：从开始日期到当前日期的天数差。"""
        return (date.today() - self.start_date).days


class Note(Base):
    """观察笔记。"""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    batch: Mapped["Batch"] = relationship("Batch", back_populates="notes")


class Recipe(Base):
    """配方。"""

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    ferment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    ingredients: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    steps: Mapped[list["RecipeStep"]] = relationship(
        "RecipeStep", back_populates="recipe", cascade="all, delete-orphan", order_by="RecipeStep.step_order"
    )


class RecipeStep(Base):
    """配方步骤。"""

    __tablename__ = "recipe_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="steps")


class Measurement(Base):
    """温湿度测量记录。"""

    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    batch: Mapped["Batch"] = relationship("Batch", back_populates="measurements")


class Reminder(Base):
    """发酵提醒待办。"""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    reminder_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    batch: Mapped["Batch"] = relationship("Batch", back_populates="reminders")
