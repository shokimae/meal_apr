
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
