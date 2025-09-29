# -*- coding: utf-8 -*-

import os
from pathlib import Path
from decimal import Decimal
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Food, Meal, MealItem
from schemas import (
    FoodCreate, FoodOut,
    MealCreate, MealOut,
    MealItemCreate, MealItemOut,
    MealSummaryOut, MealTotals, DaySummaryOut,
)

# ----------------------------- DB -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/app.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------- FastAPI --------------------------
app = FastAPI(title="FastAPI + Firebase", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要なら http://localhost:3002 などへ絞ってOK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase（鍵が無ければ黙ってスキップ）
try:
    cred_path = os.getenv("FIREBASE_APPLICATION_CREDENTIALS")
    if cred_path and Path(cred_path).exists():
        import firebase_admin
        from firebase_admin import credentials
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(cred_path))
except Exception as e:
    print(f"[Firebase] Initialization skipped: {e}")

# --------------------------- Health ---------------------------
@app.get("/health")
def health() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        return {"status": "degraded", "detail": str(e)}
    return {"status": "ok"}

# ---------------------------- Foods ---------------------------
@app.get("/foods", response_model=list[FoodOut])
def list_foods(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    return db.query(Food).order_by(Food.id.desc()).limit(limit).offset(offset).all()

@app.post("/foods", response_model=FoodOut, status_code=201)
def create_food(payload: FoodCreate, db: Session = Depends(get_db)):
    f = Food(**payload.model_dump())
    db.add(f)
    db.commit()
    db.refresh(f)
    return f

# ---------------------------- Meals ---------------------------
@app.get("/meals", response_model=list[MealOut])
def list_meals(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    date: Optional[str] = None,
    meal_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    q = db.query(Meal)
    if user_id is not None:
        q = q.filter(Meal.user_id == user_id)
    if date is not None:
        q = q.filter(Meal.date == date)
    if meal_type is not None:
        q = q.filter(Meal.meal_type == meal_type)
    return q.order_by(Meal.date.desc(), Meal.id.desc()).limit(limit).offset(offset).all()

@app.post("/meals", response_model=MealOut, status_code=201)
def create_meal(payload: MealCreate, db: Session = Depends(get_db)):
    m = Meal(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@app.delete("/meals/{meal_id}", status_code=204)
def delete_meal(meal_id: int, db: Session = Depends(get_db)):
    m = db.get(Meal, meal_id)
    if not m:
        raise HTTPException(status_code=404, detail="meal not found")
    db.delete(m)
    db.commit()
    return

# ------------------------- Meal Items -------------------------
def _calc_weight_and_macros(*, food: Optional[Food], amount: Decimal, unit: str) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    if unit == "g":
        weight_g = amount
    elif unit == "ml":
        weight_g = amount
    elif unit == "個":
        if not food or food.piece_grams is None:
            raise HTTPException(status_code=400, detail="piece_grams is required for unit='個'")
        weight_g = amount * food.piece_grams
    else:
        raise HTTPException(status_code=400, detail="invalid unit")

    def per100(v: Optional[Decimal]) -> Decimal:
        return (v or Decimal(0)) * weight_g / Decimal(100)

    protein = per100(food.per_100g_protein) if food else Decimal(0)
    fat     = per100(food.per_100g_fat)     if food else Decimal(0)
    carb    = per100(food.per_100g_carb)    if food else Decimal(0)
    kcal    = per100(food.per_100g_kcal)    if food else Decimal(0)
    return weight_g, protein, fat, carb, kcal

@app.get("/meal_items", response_model=list[MealItemOut])
def list_meal_items(meal_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(MealItem)
    if meal_id is not None:
        q = q.filter(MealItem.meal_id == meal_id)
    return q.order_by(MealItem.id.desc()).all()

@app.post("/meal_items", response_model=MealItemOut, status_code=201)
def create_meal_item(payload: MealItemCreate, db: Session = Depends(get_db)):
    meal = db.get(Meal, payload.meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="meal not found")

    food = db.get(Food, payload.food_id) if payload.food_id else None
    if not food and not payload.custom_name:
        raise HTTPException(status_code=400, detail="custom_name is required when food_id is null")

    weight_g, protein, fat, carb, kcal = _calc_weight_and_macros(
        food=food, amount=payload.amount, unit=payload.unit
    )

    mi = MealItem(
        meal_id=payload.meal_id,
        food_id=payload.food_id,
        amount=payload.amount,
        unit=payload.unit,
        weight_g=weight_g,
        protein_g=protein, fat_g=fat, carb_g=carb, kcal=kcal,
        custom_name=payload.custom_name,
    )
    db.add(mi)
    db.commit()
    db.refresh(mi)
    return mi

@app.delete("/meal_items/{item_id}", status_code=204)
def delete_meal_item(item_id: int, db: Session = Depends(get_db)):
    mi = db.get(MealItem, item_id)
    if not mi:
        raise HTTPException(status_code=404, detail="meal_item not found")
    db.delete(mi)
    db.commit()
    return

# ---------------------------- 集計 ----------------------------
@app.get("/meals/{meal_id}/summary", response_model=MealSummaryOut)
def meal_summary(meal_id: int, db: Session = Depends(get_db)):
    w, p, f, c, k = db.query(
        func.coalesce(func.sum(MealItem.weight_g), 0),
        func.coalesce(func.sum(MealItem.protein_g), 0),
        func.coalesce(func.sum(MealItem.fat_g), 0),
        func.coalesce(func.sum(MealItem.carb_g), 0),
        func.coalesce(func.sum(MealItem.kcal), 0),
    ).filter(MealItem.meal_id == meal_id).one()
    totals = MealTotals(weight_g=w, protein_g=p, fat_g=f, carb_g=c, kcal=k)
    return MealSummaryOut(meal_id=meal_id, totals=totals)

@app.get("/days/{d}/summary", response_model=DaySummaryOut)
def day_summary(d: str, user_id: int, db: Session = Depends(get_db)):
    w, p, f, c, k = db.query(
        func.coalesce(func.sum(MealItem.weight_g), 0),
        func.coalesce(func.sum(MealItem.protein_g), 0),
        func.coalesce(func.sum(MealItem.fat_g), 0),
        func.coalesce(func.sum(MealItem.carb_g), 0),
        func.coalesce(func.sum(MealItem.kcal), 0),
    ).join(Meal, MealItem.meal_id == Meal.id).filter(
        Meal.user_id == user_id, Meal.date == d
    ).one()

    rows = db.query(
        Meal.meal_type,
        func.coalesce(func.sum(MealItem.weight_g), 0),
        func.coalesce(func.sum(MealItem.protein_g), 0),
        func.coalesce(func.sum(MealItem.fat_g), 0),
        func.coalesce(func.sum(MealItem.carb_g), 0),
        func.coalesce(func.sum(MealItem.kcal), 0),
    ).join(Meal, MealItem.meal_id == Meal.id).filter(
        Meal.user_id == user_id, Meal.date == d
    ).group_by(Meal.meal_type).all()

    by = {
        t: {"weight_g": wg, "protein_g": pr, "fat_g": ft, "carb_g": cb, "kcal": kc}
        for (t, wg, pr, ft, cb, kc) in rows
    }
    totals = MealTotals(weight_g=w, protein_g=p, fat_g=f, carb_g=c, kcal=k)
    return DaySummaryOut(user_id=user_id, date=d, totals=totals, by_meal_type=by)
# ----- Simple /items endpoints for the Items page (maps to Food) -----
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.orm import Session

class ItemIn(BaseModel):
    name: str

class ItemOut(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    foods = db.query(Food).order_by(Food.id).all()
    return [ItemOut(id=f.id, name=f.name) for f in foods]

@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn, db: Session = Depends(get_db)):
    # “名前だけ”で作れるようにデフォルト値で Food を作成
    food = Food(
        name=payload.name,
        per_100g_protein=0,
        per_100g_fat=0,
        per_100g_carb=0,
        per_100g_kcal=0,
        piece_grams=100,
    )
    db.add(food)
    db.commit()
    db.refresh(food)
    return ItemOut.model_validate(food)
# ---------------------------------------------------------------------
