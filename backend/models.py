from sqlalchemy import BigInteger, String, DECIMAL, Date, DateTime, Enum, ForeignKey, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base

meal_type_enum = Enum('朝','昼','夕','間食', name='meal_type')
source_enum    = Enum('manual','plan', name='source_enum')
unit_enum      = Enum('g','個','ml', name='unit_enum')

class Food(Base):
    __tablename__ = "foods"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    per_100g_protein: Mapped[float] = mapped_column(DECIMAL(6,2), nullable=False, default=0)
    per_100g_fat:     Mapped[float] = mapped_column(DECIMAL(6,2), nullable=False, default=0)
    per_100g_carb:    Mapped[float] = mapped_column(DECIMAL(6,2), nullable=False, default=0)
    per_100g_kcal:    Mapped[float] = mapped_column(DECIMAL(7,2), nullable=False, default=0)
    piece_grams:      Mapped[float | None] = mapped_column(DECIMAL(7,2))
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    __table_args__ = (Index("uk_foods_user_name","user_id","name", unique=True),)

class Meal(Base):
    __tablename__ = "meals"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(meal_type_enum, nullable=False)
    consumed_at: Mapped[str | None] = mapped_column(DateTime)
    source: Mapped[str] = mapped_column(source_enum, nullable=False, server_default="manual")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    items: Mapped[list["MealItem"]] = relationship("MealItem", back_populates="meal", cascade="all, delete-orphan")
    __table_args__ = (Index("idx_meals_user_date","user_id","date","meal_type"),)

class MealItem(Base):
    __tablename__ = "meal_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    food_id: Mapped[int | None] = mapped_column(ForeignKey("foods.id", ondelete="SET NULL"))
    amount: Mapped[float] = mapped_column(DECIMAL(10,3), nullable=False)
    unit: Mapped[str] = mapped_column(unit_enum, nullable=False)
    weight_g: Mapped[float] = mapped_column(DECIMAL(10,3), nullable=False)
    protein_g: Mapped[float] = mapped_column(DECIMAL(10,3), nullable=False, default=0)
    fat_g:     Mapped[float] = mapped_column(DECIMAL(10,3), nullable=False, default=0)
    carb_g:    Mapped[float] = mapped_column(DECIMAL(10,3), nullable=False, default=0)
    kcal:      Mapped[float] = mapped_column(DECIMAL(10,3), nullable=False, default=0)
    custom_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    meal = relationship("Meal", back_populates="items")
    food = relationship("Food")
