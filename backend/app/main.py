from app.api.routes.jobs import router as jobs_router
from app.api.routes.matches import router as matches_router
from app.api.routes.profile import router as profile_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db

app = FastAPI(title="CareerGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(profile_router)
app.include_router(jobs_router)
app.include_router(matches_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
