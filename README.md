
# Dockerized Next.js + FastAPI + Firebase Starter

This repo gives you a minimal environment that satisfies:
- Next.js (App Router) on http://localhost:3000
- FastAPI on http://localhost:8000  (with Swagger UI at `/docs`)
- Firebase:
  - Backend: Firebase Admin SDK using a service account key (`backend/firebase_admin_key.json`)
  - Frontend: Firebase Web SDK via environment variables in `frontend/.env.local`
- Next.js → FastAPI communication via Next **rewrites** so the browser calls `/api/...` and the Next server proxies internally to the FastAPI container (no CORS hassle).

## Quick Start

1) **Prerequisites**
- Docker & Docker Compose installed.

2) **Firebase Setup (one-time)**
- Create a Firebase project and enable **Firestore (Native mode)**.
- Create a **service account key** for the Admin SDK.
  - In Firebase Console → Project Settings → Service Accounts → Generate new private key.
  - Save the JSON as `backend/firebase_admin_key.json` (this is ignored by git).
- Grab the Web App config (Project Settings → General → Your apps → Web app):
  - Fill `frontend/.env.local` using your values (below).

3) **Local Env Vars (Frontend)**
Create `frontend/.env.local` (already present here with placeholders) and fill:
```
NEXT_PUBLIC_FIREBASE_API_KEY=YOUR_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=YOUR_PROJECT.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=YOUR_PROJECT_ID
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=YOUR_PROJECT.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=YOUR_SENDER_ID
NEXT_PUBLIC_FIREBASE_APP_ID=YOUR_APP_ID
```

> Note: `backend/firebase_admin_key.json` stays **local only**. It must NOT be committed. It is already in `.gitignore`.

4) **Run**
```
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend:  http://localhost:8000  (test: http://localhost:8000/health, docs: http://localhost:8000/docs)

5) **Test end-to-end**
- Open http://localhost:3000/items
- Use the form to add an item. If Firebase Admin is configured, it writes to Firestore; otherwise it will still echo the item with a warning (in JSON).

## Git (example flow)
```
git init
git add .
git commit -m "chore: scaffold dockerized Next.js + FastAPI + Firebase"
git branch -M main
git remote add origin <YOUR_REPO_URL>
git push -u origin main
```
After you place `backend/firebase_admin_key.json` and fill `frontend/.env.local`, re-run:
```
git add frontend/.env.local backend/firebase_admin_key.json
# (they are ignored; verify with `git status` that they're not staged)
docker compose up --build
```

## Directory
```
project-root/
├─ frontend/                 # Next.js
│  ├─ app/
│  │  ├─ page.tsx           # Home
│  │  ├─ layout.tsx         # Root layout
│  │  └─ items/
│  │     └─ page.tsx        # Item list page
│  ├─ lib/
│  │  ├─ api.ts             # Fetch helpers
│  │  └─ firebase.ts        # Firebase Web SDK init (optional)
│  ├─ public/
│  ├─ .env.local            # (fill with your Firebase Web config)
│  ├─ next.config.js        # Rewrites /api/* -> backend
│  ├─ package.json
│  ├─ tsconfig.json
│  └─ Dockerfile
├─ backend/                  # FastAPI
│  ├─ main.py
│  ├─ firebase_admin_key.json  # (put your service account JSON here)
│  ├─ requirements.txt
│  └─ Dockerfile
└─ docker-compose.yml
```

## Notes
- The Next.js rewrite handles **both GET and POST** to `/api/*` and proxies to the FastAPI container; this avoids CORS issues.
- FastAPI includes CORS middleware allowing http://localhost:3000 if you ever call it directly from the browser.
- If `backend/firebase_admin_key.json` is missing, API will still work with **in-memory fallback** so you can verify wiring and UI quickly.
