
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="FastAPI + Firebase")

# CORS (allow direct calls from localhost:3000 if needed)
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase (Admin)
db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_APPLICATION_CREDENTIALS", "firebase_admin_key.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("[Firebase] Initialized Firestore client.")
        else:
            print(f"[Firebase] Service account JSON not found at {cred_path}. Running in fallback mode.")
    else:
        db = firestore.client()
except Exception as e:
    print(f"[Firebase] Initialization error (fallback mode): {e}")
    db = None


class ItemIn(BaseModel):
    name: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/items")
def list_items():
    if db:
        try:
            docs = db.collection("items").stream()
            return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Firestore error: {e}")
    # Fallback data when Firebase isn't configured
    return [{"id": "1", "name": "Sample A"}, {"id": "2", "name": "Sample B"}]


@app.post("/items")
def create_item(item: ItemIn):
    if db:
        try:
            doc_ref = db.collection("items").document()
            doc_ref.set({"name": item.name})
            return {"id": doc_ref.id, "name": item.name}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Firestore write error: {e}")
    # Fallback when Firebase isn't configured
    return {"id": "temp", "name": item.name, "warning": "Firebase not configured; item not persisted."}

# ---- DB CRUD ----
from fastapi import Depends
from sqlalchemy.orm import Session
from db import SessionLocal, engine, Base
from models import Food, Meal, MealItem
from schemas import FoodCreate, FoodOut, MealCreate, MealOut, MealItemCreate, MealItemOut

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/foods", response_model=list[FoodOut])
def list_foods(db: Session = Depends(get_db)):
    return db.query(Food).order_by(Food.id.desc()).all()

@app.post("/foods", response_model=FoodOut)
def create_food(payload: FoodCreate, db: Session = Depends(get_db)):
    food = Food(**payload.model_dump())
    db.add(food); db.commit(); db.refresh(food)
    return food

@app.get("/meals", response_model=list[MealOut])
def list_meals(user_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Meal)
    if user_id is not None: q = q.filter(Meal.user_id == user_id)
    return q.order_by(Meal.date.desc(), Meal.id.desc()).all()

@app.post("/meals", response_model=MealOut)
def create_meal(payload: MealCreate, db: Session = Depends(get_db)):
    m = Meal(**payload.model_dump())
    db.add(m); db.commit(); db.refresh(m)
    return m

def calc_weight_g(unit: str, amount: float, piece_grams: float | None) -> float:
    if unit == 'g': return amount
    if unit == 'ml': return amount
    if unit == '個': return amount * (piece_grams or 0)
    raise ValueError("unknown unit")

@app.post("/meal_items", response_model=MealItemOut)
def create_meal_item(payload: MealItemCreate, db: Session = Depends(get_db)):
    food = db.get(Food, payload.food_id) if payload.food_id else None
    wg = calc_weight_g(payload.unit, payload.amount, food.piece_grams if food else None)
    factor = (wg / 100.0) if food else 0.0
    mi = MealItem(
        meal_id=payload.meal_id, food_id=payload.food_id, custom_name=payload.custom_name,
        amount=payload.amount, unit=payload.unit, weight_g=wg,
        protein_g=(float(food.per_100g_protein)*factor) if food else 0.0,
        fat_g=(float(food.per_100g_fat)*factor) if food else 0.0,
        carb_g=(float(food.per_100g_carb)*factor) if food else 0.0,
        kcal=(float(food.per_100g_kcal)*factor) if food else 0.0,
    )
    db.add(mi); db.commit(); db.refresh(mi)
    return mi

@app.get("/meal_items", response_model=list[MealItemOut])
def list_meal_items(meal_id: int, db: Session = Depends(get_db)):
    return db.query(MealItem).filter(MealItem.meal_id == meal_id).order_by(MealItem.id.desc()).all()

# ---- DB CRUD ----
from fastapi import Depends
from sqlalchemy.orm import Session
from db import SessionLocal, engine, Base
from models import Food, Meal, MealItem
from schemas import FoodCreate, FoodOut, MealCreate, MealOut, MealItemCreate, MealItemOut

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/foods", response_model=list[FoodOut])
def list_foods(db: Session = Depends(get_db)):
    return db.query(Food).order_by(Food.id.desc()).all()

@app.post("/foods", response_model=FoodOut)
def create_food(payload: FoodCreate, db: Session = Depends(get_db)):
    food = Food(**payload.model_dump())
    db.add(food); db.commit(); db.refresh(food)
    return food

@app.get("/meals", response_model=list[MealOut])
def list_meals(user_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Meal)
    if user_id is not None: q = q.filter(Meal.user_id == user_id)
    return q.order_by(Meal.date.desc(), Meal.id.desc()).all()

@app.post("/meals", response_model=MealOut)
def create_meal(payload: MealCreate, db: Session = Depends(get_db)):
    m = Meal(**payload.model_dump())
    db.add(m); db.commit(); db.refresh(m)
    return m

def calc_weight_g(unit: str, amount: float, piece_grams: float | None) -> float:
    if unit == 'g': return amount
    if unit == 'ml': return amount
    if unit == '個': return amount * (piece_grams or 0)
    raise ValueError("unknown unit")

@app.post("/meal_items", response_model=MealItemOut)
def create_meal_item(payload: MealItemCreate, db: Session = Depends(get_db)):
    food = db.get(Food, payload.food_id) if payload.food_id else None
    wg = calc_weight_g(payload.unit, payload.amount, food.piece_grams if food else None)
    factor = (wg / 100.0) if food else 0.0
    mi = MealItem(
        meal_id=payload.meal_id, food_id=payload.food_id, custom_name=payload.custom_name,
        amount=payload.amount, unit=payload.unit, weight_g=wg,
        protein_g=(float(food.per_100g_protein)*factor) if food else 0.0,
        fat_g=(float(food.per_100g_fat)*factor) if food else 0.0,
        carb_g=(float(food.per_100g_carb)*factor) if food else 0.0,
        kcal=(float(food.per_100g_kcal)*factor) if food else 0.0,
    )
    db.add(mi); db.commit(); db.refresh(mi)
    return mi

@app.get("/meal_items", response_model=list[MealItemOut])
def list_meal_items(meal_id: int, db: Session = Depends(get_db)):
    return db.query(MealItem).filter(MealItem.meal_id == meal_id).order_by(MealItem.id.desc()).all()

# ---- health with DB ping ----
from sqlalchemy import text
@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        # ログに詳細は出るので、外には簡潔に返す
        return {"status": "degraded", "error": str(e)}, 500

from sqlalchemy import text
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
