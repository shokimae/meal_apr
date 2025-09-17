# -*- coding: utf-8 -*-
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Text, Enum, Numeric,
    ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ==================== Foods ====================
class Food(Base):
    __tablename__ = "foods"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uk_foods_user_name"),
        {"sqlite_autoincrement": True},  # SQLiteで確実にAUTOINCREMENT
    )

    id = Column(Integer, primary_key=True, autoincrement=True)  # ★ここが重要
    user_id = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    per_100g_protein = Column(Numeric(6, 2), nullable=False, server_default="0")
    per_100g_fat     = Column(Numeric(6, 2), nullable=False, server_default="0")
    per_100g_carb    = Column(Numeric(6, 2), nullable=False, server_default="0")
    per_100g_kcal    = Column(Numeric(7, 2), nullable=False, server_default="0")
    piece_grams      = Column(Numeric(7, 2), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

# ==================== Meals ====================
class Meal(Base):
    __tablename__ = "meals"
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)  # ★
    user_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(Enum("朝", "昼", "夕", "間食", name="meal_type"), nullable=False)
    consumed_at = Column(DateTime, nullable=True)
    source = Column(Enum("manual", "plan", name="meal_source"), nullable=False, server_default="manual")
    plan_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

# ==================== Meal Items ====================
class MealItem(Base):
    __tablename__ = "meal_items"
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)  # ★
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=True)
    amount = Column(Numeric(10, 3), nullable=False)
    unit = Column(Enum("g", "個", "ml", name="amount_unit"), nullable=False)
    weight_g = Column(Numeric(10, 3), nullable=False)
    protein_g = Column(Numeric(10, 3), nullable=False, server_default="0")
    fat_g     = Column(Numeric(10, 3), nullable=False, server_default="0")
    carb_g    = Column(Numeric(10, 3), nullable=False, server_default="0")
    kcal      = Column(Numeric(10, 3), nullable=False, server_default="0")
    custom_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
