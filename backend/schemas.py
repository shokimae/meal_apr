from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class FoodBase(BaseModel):
    name: str
    per_100g_protein: float = 0
    per_100g_fat: float = 0
    per_100g_carb: float = 0
    per_100g_kcal: float = 0
    piece_grams: Optional[float] = None
    user_id: Optional[int] = None
class FoodCreate(FoodBase): pass
class FoodOut(FoodBase):
    id: int
    class Config: from_attributes = True

class MealBase(BaseModel):
    user_id: int
    date: date
    meal_type: str
    consumed_at: Optional[datetime] = None
    source: str = "manual"
    notes: Optional[str] = None
class MealCreate(MealBase): pass
class MealOut(MealBase):
    id: int
    class Config: from_attributes = True

class MealItemCreate(BaseModel):
    meal_id: int
    food_id: Optional[int] = None
    custom_name: Optional[str] = None
    amount: float
    unit: str  # 'g' | '個' | 'ml'
class MealItemOut(BaseModel):
    id: int
    meal_id: int
    food_id: Optional[int]
    custom_name: Optional[str]
    amount: float
    unit: str
    weight_g: float
    protein_g: float
    fat_g: float
    carb_g: float
    kcal: float
    class Config: from_attributes = True
