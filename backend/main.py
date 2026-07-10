from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.user import router as user_router
from app.routers.preferences import router as pref_router
from app.routers.resume import router as resume_router
from app.routers.notifications import router as notif_router
from app.routers.jobs import router as jobs_router
from app.routers.reports import router as reports_router
from app.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(pref_router)
app.include_router(resume_router)
app.include_router(notif_router)
app.include_router(jobs_router)
app.include_router(reports_router)

