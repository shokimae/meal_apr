from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

# ------ Foods ------
class FoodBase(BaseModel):
    name: str
    per_100g_protein: Decimal = Field(default=0)
    per_100g_fat: Decimal = Field(default=0)
    per_100g_carb: Decimal = Field(default=0)
    per_100g_kcal: Decimal = Field(default=0)
    piece_grams: Optional[Decimal] = None

class FoodCreate(FoodBase):
    user_id: Optional[int] = None

class FoodOut(FoodBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# ------ Meals ------
MealType = Literal['朝', '昼', '夕', '間食']
class MealCreate(BaseModel):
    user_id: int
    date: date
    meal_type: MealType
    consumed_at: Optional[datetime] = None
    source: Literal['manual','plan'] = 'manual'
    plan_id: Optional[int] = None
    notes: Optional[str] = None

class MealOut(MealCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# ------ Meal Items ------
Unit = Literal['g','個','ml']

class MealItemCreate(BaseModel):
    meal_id: int
    food_id: Optional[int] = None  # 手入力のとき None
    amount: Decimal                 # 入力数量（g / 個 / ml）
    unit: Unit
    custom_name: Optional[str] = None

class MealItemOut(BaseModel):
    id: int
    meal_id: int
    food_id: Optional[int]
    amount: Decimal
    unit: Unit
    weight_g: Decimal
    protein_g: Decimal
    fat_g: Decimal
    carb_g: Decimal
    kcal: Decimal
    custom_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# ------ Aggregation ------
class MealTotals(BaseModel):
    weight_g: Decimal
    protein_g: Decimal
    fat_g: Decimal
    carb_g: Decimal
    kcal: Decimal

class MealSummaryOut(BaseModel):
    meal_id: int
    totals: MealTotals

class DaySummaryOut(BaseModel):
    user_id: int
    date: date
    totals: MealTotals
    by_meal_type: dict  # {"朝": {...}, "昼": {...}, ...}
