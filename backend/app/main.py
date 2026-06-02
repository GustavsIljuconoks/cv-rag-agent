from app.api.routes.profile import router as profile_router
from fastapi import FastAPI
from app.db import init_db

app = FastAPI(title="CareerGraph API")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(profile_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
